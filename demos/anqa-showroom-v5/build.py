from pathlib import Path
import base64,json,zipfile
r=Path(__file__).parent
cat=json.loads((r/'data.json').read_text());models={p['id']:base64.b64encode((r/'assets'/f"{p['id']}-product.glb").read_bytes()).decode() for p in cat};images={p['id']:'data:image/webp;base64,'+base64.b64encode((r/'assets'/f"{p['id']}-product-front.webp").read_bytes()).decode() for p in cat}
pbr={p.name:base64.b64encode(p.read_bytes()).decode() for p in (r/'assets').iterdir() if p.name in ['exterior.hdr','floor-color.jpg','wood-color.jpg']}
architecture=base64.b64encode((r/'assets/architecture.glb').read_bytes()).decode()
photos='window.FACADE_ORIGINAL='+json.dumps('data:image/png;base64,'+base64.b64encode((r/'assets/facade-original.png').read_bytes()).decode())+';window.FACADE_CLEAN='+json.dumps('data:image/png;base64,'+base64.b64encode((r/'assets/facade-clean.png').read_bytes()).decode())+';'
data=photos+'window.ARCHITECTURE='+json.dumps(architecture)+';window.PBR='+json.dumps(pbr)+';window.CATALOG='+json.dumps(cat,ensure_ascii=False)+';window.MODELS='+json.dumps(models)+';window.IMAGES='+json.dumps(images)+';';(r/'data.js').write_text(data)
css=(r/'style.css').read_text()
for f in (r/'assets').glob('*.woff2'):css=css.replace("url('assets/"+f.name+"')","url('data:font/woff2;base64,"+base64.b64encode(f.read_bytes()).decode()+"')")
bundle='\n'.join(l.rstrip() for l in (r/'app.bundle.js').read_text().splitlines());(r/'app.bundle.js').write_text(bundle)
html=(r/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>').replace('<script src="data.js"></script>','<script>'+data+'</script>').replace('<script src="app.bundle.js"></script>','<script>'+bundle+'</script>');(r/'ANQA_Showroom_v5.html').write_text(html)
with zipfile.ZipFile(r/'ANQA_Showroom_v5.zip','w',zipfile.ZIP_DEFLATED) as z:
 z.write(r/'ANQA_Showroom_v5.html','ANQA_Showroom_v5.html')
 z.writestr('START_HERE.txt','افتح ANQA_Showroom_v5.html مباشرة. مرّر للدخول، واسحب للنظر. الملابس متاحة من المجموعة أيضًا. الديمو لا يرسل طلبات.\n')
 for name in ['index.html','style.css','photo-entrance.js','app.js','app.bundle.js','data.js','data.json','build.py','package.json','README.md','THREE-LICENSE.txt','verification.json','test.py','preview-front.png','preview-rail.png','garment-repairs.json']:
  if (r/name).exists():z.write(r/name,'source/'+name)
 for p in (r/'assets').iterdir():z.write(p,'source/assets/'+p.name)
print('HTML bytes',len(html.encode()))
