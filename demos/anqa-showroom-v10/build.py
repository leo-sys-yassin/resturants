from pathlib import Path
import base64,json,zipfile
r=Path(__file__).parent
enc=lambda p:base64.b64encode(p.read_bytes()).decode()
cat=json.loads((r/'data.json').read_text());models={p['id']:enc(r/'assets'/f"{p['id']}-product.glb") for p in cat};images={p['id']:'data:image/webp;base64,'+enc(r/'assets'/f"{p['id']}-product-front.webp") for p in cat}
names={'walnut-color.jpg','walnut-normal.jpg','walnut-rough.jpg','plaster-color.jpg','plaster-normal.jpg','plaster-rough.jpg','facade-color.png','floor-color.png','architecture-irradiance.jpg','street.png'}
textures={p.name:'data:image/'+('png' if p.suffix=='.png' else 'jpeg')+';base64,'+enc(p) for p in (r/'assets').iterdir() if p.name in names}
data='window.SURFACES='+json.dumps(textures)+';window.ARCHITECTURE='+json.dumps(enc(r/'assets/architecture.glb'))+';window.PBR='+json.dumps({'exterior.hdr':enc(r/'assets/exterior.hdr')})+';window.CATALOG='+json.dumps(cat,ensure_ascii=False)+';window.MODELS='+json.dumps(models)+';window.IMAGES='+json.dumps(images)+';';(r/'data.js').write_text(data)
css=(r/'style.css').read_text()
for f in (r/'assets').glob('*.woff2'):css=css.replace("url('assets/"+f.name+"')","url('data:font/woff2;base64,"+enc(f)+"')")
bundle=(r/'app.bundle.js').read_text()
html=(r/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>').replace('<script src="data.js"></script>','<script>'+data+'</script>').replace('<script src="app.bundle.js"></script>','<script>'+bundle+'</script>');out=r/'ANQA_Showroom_v10.html';out.write_text(html)
with zipfile.ZipFile(r/'ANQA_Showroom_v10.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(out,out.name)
print('HTML bytes',out.stat().st_size,'; ZIP contains the HTML file only')
