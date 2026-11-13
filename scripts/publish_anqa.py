"""Publish a built local ANQA project into the stable GitHub Pages path.
Run: python scripts/publish_anqa.py --source /path/to/current/project
Then commit docs/anqa and push main; GitHub Pages deploys the same URL.
"""
from pathlib import Path
import argparse,ast,hashlib,json,re,shutil
parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);args=parser.parse_args();src=Path(args.source).resolve();dest=Path(__file__).resolve().parents[1]/'docs/anqa';(dest/'assets').mkdir(parents=True,exist_ok=True)
def put(path,folder='assets'):
 data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()[:16];name=f'{path.stem}.{digest}{path.suffix}';out=dest/folder/name if folder else dest/name
 if out.exists():assert out.read_bytes()==data
 else:out.write_bytes(data)
 return str(out.relative_to(dest))
# The runtime's texture inventory comes from the already verified standalone build.
assign=next(n for n in ast.parse((src/'build.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='names' for t in n.targets));names=ast.literal_eval(assign.value)
surfaces={name:put(src/'assets'/name) for name in sorted(names)};catalog=json.loads((src/'data.json').read_text());models={p['id']:put(src/'assets'/f"{p['id']}-product.glb") for p in catalog};images={p['id']:put(src/'assets'/f"{p['id']}-product-front.webp") for p in catalog}
fonts={p.name:put(p) for p in (src/'assets').glob('*.woff2')};css=(src/'style.css').read_text()
for name,url in fonts.items():css=css.replace("assets/"+name,url)
csspath=dest/'client.css';csspath.write_text(css);style=put(csspath,'');csspath.unlink()
bundle=put(src/'app.bundle.js','');arch=put(src/'assets/architecture-v13.glb');hdr=put(src/'assets/exterior.hdr')
manifest={'surfaces':surfaces,'catalog':catalog,'models':models,'images':images,'architecture':arch,'hdr':hdr,'style':style,'script':bundle}
sourcehtml=(src/'index.html').read_text();body=re.search(r'<body>(.*)</body>',sourcehtml,re.S).group(1);manifest['body']=re.sub(r'<script\b[^>]*>.*?</script>','',body,flags=re.S);manifest['title']=re.search(r'<title>(.*?)</title>',sourcehtml,re.S).group(1)
manifest['version']='anqa-'+hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()[:16]
(dest/'version.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')))
html=(src/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>body{margin:0;background:#d9cbbb}#loadingFacade{position:fixed;inset:0;z-index:99;background:#d9cbbb}#loadingFacade img{width:100%;height:100%;object-fit:cover}#loadingFacade span{position:absolute;bottom:105px;left:50%;transform:translateX(-50%);background:#f7f2e6ee;padding:6px 14px;border-radius:5px;font:14px Arial}</style>')
poster='<div id="loadingFacade"><img src="'+surfaces['new-facade.png']+'" alt="واجهة أناقة"><span>نجهّز الجولة…</span></div>'
html=html.replace('<body>','<body>'+poster).replace('<script src="data.js"></script>','').replace('<script src="app.bundle.js"></script>','<script src="boot.js"></script>')
(dest/'index.html').write_text(html)
print('Published',manifest['version'],'to',dest)
