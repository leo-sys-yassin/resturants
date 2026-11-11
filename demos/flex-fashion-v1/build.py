"""Build the self-contained desktop HTML and distributable ZIP. Python stdlib only."""
from pathlib import Path
import base64,json,zipfile
R=Path(__file__).resolve().parent

def data_url(path):
 mime='font/ttf' if path.suffix=='.ttf' else 'image/webp'
 return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()

css=(R/'style.css').read_text().replace("url('assets/Montserrat.ttf')","url('"+data_url(R/'assets/Montserrat.ttf')+"')")
catalog=json.loads((R/'catalog.json').read_text())
# Keep catalog.js synchronized with the editable JSON source.
(R/'catalog.js').write_text('window.FLEX_CATALOG='+json.dumps(catalog,ensure_ascii=False)+';\n')
for product in catalog:
 for views in product['views'].values():
  for direction,path in views.items():views[direction]=data_url(R/path)
html=(R/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>')
html=html.replace('<script src="catalog.js"></script>','<script>window.FLEX_CATALOG='+json.dumps(catalog,ensure_ascii=False)+';</script>')
html=html.replace('<script src="app.js"></script>','<script>'+(R/'app.js').read_text()+'</script>')
(R/'Flex_Fashion_Standalone.html').write_text(html)
files=['Flex_Fashion_Standalone.html','index.html','style.css','app.js','catalog.js','catalog.json','build.py','README.md','verification.json','test_shop.py','preview.jpg']
with zipfile.ZipFile(R/'Flex_Fashion_Desktop_v1.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in files:
  if (R/name).exists():z.write(R/name,'Flex_Fashion/'+name)
 for path in sorted((R/'assets').iterdir()):z.write(path,'Flex_Fashion/assets/'+path.name)
print('Built standalone HTML and ZIP')
