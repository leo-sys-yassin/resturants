"""Build self-contained ANQA HTML and source ZIP. Python standard library only."""
from pathlib import Path
import base64,json,zipfile,hashlib
R=Path(__file__).resolve().parent

def uri(path):
 mime='font/ttf' if path.suffix=='.ttf' else 'image/webp'
 return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()
provenance=json.loads((R/'asset-provenance.json').read_text())
provenance['assets']=[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((R/'assets').glob('*.webp'))]
(R/'asset-provenance.json').write_text(json.dumps(provenance,indent=2,ensure_ascii=False))
css=(R/'style.css').read_text().replace("url('assets/Montserrat.ttf')","url('"+uri(R/'assets/Montserrat.ttf')+"')")
catalog=json.loads((R/'catalog.json').read_text())
(R/'catalog.js').write_text('window.ANQA_CATALOG='+json.dumps(catalog,ensure_ascii=False)+';\n')
for p in catalog:
 for views in p['views'].values():
  for direction,path in views.items():views[direction]=uri(R/path)
 for seq in p['sequences'].values():seq['atlas']=uri(R/seq['atlas'])
html=(R/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>')
html=html.replace('<script src="catalog.js"></script>','<script>window.ANQA_CATALOG='+json.dumps(catalog,ensure_ascii=False)+';</script>')
for name in ['turntable.js','app.js']:html=html.replace('<script src="'+name+'"></script>','<script>'+(R/name).read_text()+'</script>')
(R/'ANQA_Standalone.html').write_text(html)
files=['index.html','style.css','app.js','turntable.js','catalog.js','catalog.json','build.py','README.md','verification.json','test_shop.py','preview.jpg','asset-provenance.json']
with zipfile.ZipFile(R/'ANQA_Desktop_v2.zip','w',zipfile.ZIP_DEFLATED) as z:
 z.write(R/'ANQA_Standalone.html','ANQA_Standalone.html')
 z.writestr('START_HERE.txt','ANQA — أناقة\n\nافتح ANQA_Standalone.html الموجود مباشرة داخل هذا المجلد.\nهذا هو الموقع الكامل: الصور والخط والتنسيق موجودة داخل الملف نفسه.\n\nمجلد ANQA يحتوي الملفات القابلة للتعديل. إذا أردت فتح ANQA/index.html، فك ضغط المجلد كاملاً أولاً؛ فتح index.html وحده من داخل ZIP لا يحمّل بقية الملفات.\n')
 for name in files:
  if (R/name).exists():z.write(R/name,'ANQA/'+name)
 for p in sorted((R/'assets').iterdir()):z.write(p,'ANQA/assets/'+p.name)
print('Built ANQA standalone:',(R/'ANQA_Standalone.html').stat().st_size,'bytes. ZIP:',(R/'ANQA_Desktop_v2.zip').stat().st_size,'bytes.')
