"""Build the complete reference-inspired motion menu as one offline HTML file."""
from pathlib import Path
import re,json,base64,mimetypes
root=Path(__file__).resolve().parent;src=root/'web'
def uri(p):return 'data:'+(mimetypes.guess_type(str(p))[0] or 'application/octet-stream')+';base64,'+base64.b64encode(p.read_bytes()).decode()
# Only assets used by this version, no legacy 3D runtime or model.
files=list((src/'assets/plated').glob('*.webp'))+list((src/'assets/snacks').glob('*.webp'))+[p for p in (src/'assets/burger-photo').glob('*.webp') if p.stem.startswith('ref-')]
assets={str(p.relative_to(src/'assets')):uri(p) for p in files}
html=(src/'index.html').read_text().replace('<base href="/">','');html=re.sub(r'<a class="management-link" href="service.html">.*?</a>','',html);css=(src/'style.css').read_text()
def css_asset(m):
 path=src/m.group(1)
 if not path.exists():raise RuntimeError('Missing CSS asset: '+str(path))
 return "url('"+uri(path)+"')"
css=re.sub(r"url\('([^']+)'\)",css_asset,css)
html=html.replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>')
for name,value in assets.items():html=html.replace('src="assets/'+name+'"','src="'+value+'"')
html=html.replace('href="favicon.svg"','href="'+uri(src/'favicon.svg')+'"')
bootstrap='<script>window.EMBER_EMBEDDED_ASSETS='+json.dumps(assets,separators=(',',':'))+';window.EMBER_PHOTO_ASSETS='+json.dumps({p.stem:assets['burger-photo/'+p.name] for p in (src/'assets/burger-photo').glob('*.webp') if 'burger-photo/'+p.name in assets},separators=(',',':'))+';</script>'
html=html.replace('<script id="deployment-config" src="runtime-config.js"></script>','<script id="deployment-config">'+(src/'runtime-config.js').read_text()+'</script>')
html=html.replace('<script src="menu-bootstrap.js"></script>',bootstrap+'<script>'+(src/'menu-bootstrap.js').read_text()+'</script>')
html=html.replace('<script src="menu-options.js"></script>','<script>'+(src/'menu-options.js').read_text()+'</script>')
html=html.replace('<script src="menu-store.js"></script>','<script>'+(src/'menu-store.js').read_text()+'</script>')
html=html.replace('<script src="i18n.js"></script>','<script>'+(src/'i18n.js').read_text()+'</script>')
html=html.replace('<script src="motion.js"></script>','<script>'+ (src/'motion.js').read_text()+'</script>')
html=html.replace('<script src="app.js"></script>','<script>'+(src/'app.js').read_text()+'</script>')
html=html.replace('<script src="photo-motion.js"></script>','<script>'+(src/'photo-motion.js').read_text()+'</script>')
html=html.replace('<script src="menu-cloud.js"></script>','<script>'+(src/'menu-cloud.js').read_text()+'</script>')
html=html.replace('<script src="admin.js"></script>','<script>'+(src/'admin.js').read_text()+'</script>')
out=root/'offline-menu.html';out.parent.mkdir(exist_ok=True,parents=True);out.write_text(html)
print(out, out.stat().st_size,'bytes')
