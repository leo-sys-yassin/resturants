# Current visual provenance

## Direction references
The user supplied `video_2026-11-04_06-23-57.mp4` (light version) and `video_2026-11-04_06-23-02.mp4` (dark version). The implementation follows their textured light/dark surface, large floating dishes, scroll movement, centered headings and sparse editorial composition. User-requested plate selection galleries, the full 24-item menu and a mobile layout adapt the reference to this fictional restaurant. The source videos are not redistributed in the exported website.

## Product and ingredient illustrations
The user authorised creating new visual assets when suitable original photography was unavailable. The new food and beverage assets are AI-generated photographic-style illustrations, not photographs of a real restaurant or 3D mesh renders. The site information dialog explicitly states this distinction.

`dist/assets/plated/sources.json` maps all 24 assets to generated source sheets. Six sheets consistently portray 16 prepared meals on white porcelain plates and eight drinks without plates. A correction sheet removes unrequested meat toppings from classicmeal/loadedfries. Alpha separation and WebP conversion package complete objects for web animation, without slicing an assembled burger into bands.

The seven complete ingredient assets in `dist/assets/burger-photo/` originate from generated sheet `exec-4c3af822-fe2a-4959-8903-db518a5c704c.png`, using a food-photography reference. Each ingredient occupies its own isolated row; `layers.json` records the regions used. The scene is animated by CSS transforms linked to native scroll; it is not a GLB/WebGL model.

Source food photographs used as visual editing references remain documented in `dist/assets/menu-v2/sources.json`. They are not embedded as current product pictures in the downloadable motion-menu HTML. Public repository availability alone does not prove the original commercial image licence. Before a real commercial launch, use restaurant-owned photography or establish appropriate commercial licences.

## Typography and surfaces
- IBM Plex Sans Arabic, SIL Open Font License 1.1: `dist/assets/FONT-LICENSE.txt`.
- Amiri, SIL Open Font License 1.1: `dist/assets/AMIRI-OFL.txt`, sourced from google/fonts/ofl/amiri.
- Aref Ruqaa, SIL Open Font License 1.1: `dist/assets/AREF-OFL.txt`, sourced from google/fonts/ofl/arefruqaa.
- Light paper and dark slate surface textures are procedurally created for this prototype by `research/make-surfaces.py`.

Legacy version-2 GLB, Three.js runtime and cutout examples are not used by the current website or offline HTML.

## User-provided burger reference — 4 November 2026
Eight whole visible ingredients extracted from the first frame of the supplied Dribbble MP4 (547e5da3bf2571c757a00af2c023d2d2.mp4). Background-edge matte cleaned; original texture preserved. Reverse motion rebuilt as scroll-controlled independent layers. Other menu food imagery remains photographic-style generated imagery, not restaurant photography. New garnish sprites are generated photographic-style assets.

## Component imagery revision
Generated, photographic-style drink bodies: exec-c9847aa1-1418-4bb2-8373-cc12a61545b1.png; cream/straw sheet: exec-1bd0e980-6a8c-4069-8f46-3d8563a2e19b.png; snack props: exec-8b8c8dda-09db-42ce-a608-4a879cc509a2.png. Burger reference-preserving transparent cleanup: exec-85156d7e-2415-40cd-83d2-3b0dac0af991.png and exec-1f37efb7-3172-4ede-8d2b-529ce8ffa129.png. Cola matched-glass pair: exec-c95a51b5-9c45-4b64-9a70-505e263a465e.png (cleaned from exec-4f7444a4-1d59-487c-b726-1c06732c7f04.png). Technical sprite extraction and WebP packaging preserve source PNGs. These are illustrative assets, not photography of a real operating restaurant.

## Syrian menu additions (v8)
Photographic-style generated complete food plates: exec-8b3bac3f-1d8b-4281-a6ec-742396842934.png (nine shawarma/sandwich plates), exec-eb04d2c4-ad40-495f-b51e-d4c594ca33be.png (nine chicken/side plates). Cold drinks: exec-c019bb9b-1fd9-4c09-9018-fe9bb18f5eff.png. Hot drinks: exec-8503a7dd-a559-4605-9e32-968f1180bc22.png with transparent-background cleanup exec-bd026baf-a8ec-474e-aabf-642f008ba2db.png. Original seven complete milkshake photos and original complete cola photograph-style asset restored. Each plate/vessel is extracted as one complete image; no cream/body separation is used. Generated assets illustrate a fictional restaurant and are not actual restaurant photography.

## Asset edge corrections v9
New whole separated burger: exec-7807709f-1258-4e3f-a20a-8efdf2abd03e.png. Whole plate sets with spacious gutters: exec-413e8d14-e214-4078-94c8-32f6e340021d.png, exec-b43aee6b-fcf9-426d-9e65-c9abcbe244c9.png, exec-3794b9f9-8461-47f4-8ca2-e4742d28047e.png. Each object was extracted using alpha bounds, with disconnected neighbouring fragments removed and complete objects fitted into padded presentation canvases. Original generated PNGs are preserved.

## Premium juice and cold-coffee glassware v11
Generated photographic-style whole drinks: exec-a1c2d3e8-23ab-499e-a0e5-020ec4a939f0.png (five juices) and exec-12aeeeff-b883-44a4-be42-6cda571c4bfc.png (five cold coffees). Complete vessel alpha extraction and padded image packaging; no separated cream/body effects. Original PNGs preserved.
