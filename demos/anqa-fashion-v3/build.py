from pathlib import Path
import base64,json,re,zipfile,shutil
R=Path(__file__).parent
catalog=json.loads((R/'data.json').read_text())
models={p['id']+'-'+kind:base64.b64encode((R/'assets'/f"{p['id']}-{kind}.glb").read_bytes()).decode() for p in catalog for kind in ['product','model']}
images={p['id']:f"assets/{p['id']}-product-front.webp" for p in catalog}
def data_js(images):return 'window.ANQA_CATALOG='+json.dumps(catalog,ensure_ascii=False)+';\nwindow.ANQA_MODELS='+json.dumps(models)+';\nwindow.ANQA_IMAGES='+json.dumps(images)+';\n'
(R/'data.js').write_text(data_js(images))
css=(R/'style.css').read_text()
for f in (R/'assets').glob('*.woff2'):
 css=css.replace("url('assets/"+f.name+"')","url('data:font/woff2;base64,"+base64.b64encode(f.read_bytes()).decode()+"')")
embedded={k:'data:image/webp;base64,'+base64.b64encode((R/v).read_bytes()).decode() for k,v in images.items()}
bundle='\n'.join(line.rstrip() for line in (R/'app.bundle.js').read_text().splitlines())+'\n'
(R/'app.bundle.js').write_text(bundle)
html=(R/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>').replace('<script src="data.js"></script>','<script>'+data_js(embedded).replace('</','<\\/')+'</script>').replace('<script src="app.bundle.js"></script>','<script>'+(R/'app.bundle.js').read_text()+'</script>')
(R/'ANQA_v3.html').write_text(html)
files=['index.html','style.css','app.js','engine.js','i18n.js','app.bundle.js','data.js','data.json','build.py','package.json','package-lock.json','README.md','verification.json','test_app.py','test_360.py','preview.jpg','THREE-LICENSE.txt']
with zipfile.ZipFile(R/'ANQA_Desktop_v3.zip','w',zipfile.ZIP_DEFLATED) as z:
 z.write(R/'ANQA_v3.html','ANQA_v3.html')
 z.writestr('START_HERE.txt','ANQA — أناقة\nافتح ANQA_v3.html لمعاينة الموقع مباشرة.\nالملف يتضمن كل شيء ولا يحتاج إنترنت.\nمجلد ANQA_Source يحتوي نسخة المشروع القابلة للتعديل.\n')
 for f in files:
  if (R/f).exists():z.write(R/f,'ANQA_Source/'+f)
 for p in (R/'assets').iterdir():
  if p.suffix in ['.glb','.woff2','.txt'] or p.name.endswith('-product-front.webp'):z.write(p,'ANQA_Source/assets/'+p.name)
print('Standalone',len(html.encode()),'bytes; ZIP',(R/'ANQA_Desktop_v3.zip').stat().st_size,'bytes')
