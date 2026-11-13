import {ShaderChunk} from 'three';
// Static room surfaces already contain the diffuse LED lighting in their irradiance atlas.
// Outdoor surfaces use daylight; they must not run expensive indoor LTC-area-light loops.
const daylightChunk=ShaderChunk.lights_fragment_begin.replace(/#if \( NUM_RECT_AREA_LIGHTS > 0 \) && defined\( RE_Direct_RectArea \)[\s\S]*?#endif/,'');
export function skipIndoorAreaLights(shader){shader.fragmentShader=shader.fragmentShader.replace('#include <lights_fragment_begin>',daylightChunk)}
