from pathlib import Path
import trimesh,numpy as np,json
from PIL import Image
W=Path(__file__).resolve().parent/'work';A=Path(__file__).resolve().parents[1]/'assets'
report={}
for key in ['forest','coal','wine','sky','oat']:
 file=W/f'{key}-new.glb'
 if not file.exists():continue
 scene=trimesh.load(file);meshes=[]
 for name in scene.graph.nodes_geometry:
  tr,geo=scene.graph[name];m=scene.geometry[geo].copy();m.apply_transform(tr);meshes.append(m)
 # One source mesh per object, preserving the generated UV atlas.
 m=meshes[0];original=len(m.faces);uv=m.visual.uv;im=np.asarray(m.visual.material.baseColorTexture.convert('RGB'));h,w=im.shape[:2]
 pixels=im[np.clip(((1-uv[:,1])*(h-1)).astype(int),0,h-1),np.clip((uv[:,0]*(w-1)).astype(int),0,w-1)].astype(float)
 r,g,b=pixels.T;y=m.vertices[:,1]
 brown=(r>g*1.12)&(g>b*1.13)&(r>85)&(y>.30)
 discard=(brown[m.faces].mean(axis=1)>.32)
 if key in ['forest','oat','sky']:discard|=(y[m.faces].max(axis=1)>.425)
 m.update_faces(~discard);m.remove_unreferenced_vertices()
 # Remove disconnected reconstruction residue without changing the surviving UVs.
 proxy=trimesh.Trimesh(vertices=m.vertices,faces=m.faces,process=False);proxy.merge_vertices();comps=trimesh.graph.connected_components(proxy.face_adjacency,nodes=np.arange(len(proxy.faces)),min_len=1)
 keep=np.zeros(len(m.faces),bool)
 for comp in comps:
  if len(comp)>max(80,len(m.faces)*.008):keep[comp]=True
 m.update_faces(keep);m.remove_unreferenced_vertices()
 unique,inv=np.unique(np.round(m.vertices,6),axis=0,return_inverse=True)
 welded=trimesh.Trimesh(vertices=unique,faces=inv[m.faces],process=False)
 boundary=welded.edges[trimesh.grouping.group_rows(np.sort(welded.edges,axis=1),require_count=1)]
 bv=np.unique(boundary);bv=bv[welded.vertices[bv,1]>.22];neighbors=welded.vertex_neighbors
 for _ in range(4):
  before=welded.vertices.copy()
  for v in bv:
   ns=neighbors[v]
   if len(ns):welded.vertices[v]=before[v]*.55+before[ns].mean(axis=0)*.45
 m.vertices=welded.vertices[inv]
 target=.82 if key in ['coal','wine'] else .72 if key!='sky' else .70
 lo,hi=m.bounds;center=(lo+hi)/2;scale=target/(hi[1]-lo[1]);m.vertices=(m.vertices-center)*scale;m.vertices[:,1]+=(.38 if key in ['coal','wine'] else .30)-target/2
 # Clamp the whole neck region to one smooth sewn edge, not only boundary vertices.
 if key in ['forest','oat','sky']:
  v=m.vertices.copy();x=v[:,0];z=v[:,2];front=np.clip((z+.015)/.035,0,1)
  envelope=.285-.030*np.maximum(0,1-(x/.11)**2)*front-.05*np.maximum(0,np.abs(x)-.12)
  region=(v[:,1]>.20)&(np.abs(x)<.28)
  v[region,1]=np.minimum(v[region,1],envelope[region]);m.vertices=v
 # Flat cotton surface; generated light/shadow stays fixed across rotation.
 m.visual.material.roughnessFactor=.92;m.visual.material.metallicFactor=0;m.visual.material.doubleSided=True
 (A/f'{key}-product.glb').write_bytes(m.export(file_type='glb',include_normals=True))
 report[key]={'source_faces':original,'retained_faces':len(m.faces),'removed_faces':original-len(m.faces),'bounds':m.bounds.tolist(),'source':'SAM 3D Objects, rebuilt from original front product image','repairs':'Removed hanger-colored upper faces and isolated fragments; physical garment scale normalized; UV texture retained.'}
 print(key,report[key],flush=True)
(W/'garment-repairs.json').write_text(json.dumps(report,indent=2))
# Three rotating copies per source for a perspective review, transformed in geometry space.
s=trimesh.Scene()
for row,key in enumerate(['forest','coal','wine','sky']):
 m=trimesh.load(A/f'{key}-product.glb').to_geometry()
 for col,angle in enumerate([0,np.pi/2,np.pi]):
  t=trimesh.transformations.rotation_matrix(angle,[0,1,0]);t[:3,3]=[(col-1)*.9,(1.5-row)*1.0,0];s.add_geometry(m,transform=t,node_name=f'{key}-{col}')
(W/'garment-review.glb').write_bytes(s.export(file_type='glb'))
