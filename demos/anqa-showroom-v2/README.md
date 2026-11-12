# ANQA Showroom — material and tour revision 02

افتح ANQA_Showroom_v2.html مباشرة. الملف مستقل ويحتاج متصفحًا يدعم WebGL.

## التغييرات
- مسار كامل: الواجهة، الدخول، رفوف الأحذية، داخل المحل، الملابس، الخروج، ثم إعادة عرض الواجهة وإغلاق الأبواب.
- دوران النظر بالماوس مقفول قبل الدخول وبعد الخروج، ومتاح فقط داخل المحل. اتجاهات الكاميرا تتغير باستخدام quaternion slerp لتجنب انقلابات اتجاه النظر.
- الحفاظ على تقسيمات المحل والستاندات والسقف والمقعد والطاولة.
- خامات سطحية مصوّرة للجدران والخشب والبلاط مع normal/roughness maps، وبيئة HDR محايدة للانعكاسات.
- زجاج بنفاذية وانكسار وسماكة بدل سطح شفاف بسيط، مع عدم جعله يحجب ضوء الشمس كجدار مصمت.
- كرت منتج أكبر من عمودين للكمبيوتر، ونافذة سفلية للهاتف، وتنقيح القوائم.

## حدود النتيجة
هذا تحسين لمشهد WebGL تفاعلي، وليس صورة فوتوغرافية أو نسخة مطابقة لصورة AURA. الانعكاسات تعتمد على بيئة HDR ثابتة، وليست انعكاسات آنية لجميع الأشياء خلف الزائر. مجسمات الملابس التقريبية القديمة باقية. الألوان والإضاءة والأداء تختلف بحسب الشاشة والجهاز. لا دفع ولا إرسال طلبات ولا مخزون حقيقي.

## مصدر الخامات
Poly Haven — CC0: https://polyhaven.com/license
https://polyhaven.com/a/plastered_wall_04 — color, normal GL, roughness
https://polyhaven.com/a/marble_01 — color, normal GL, roughness
https://polyhaven.com/a/wood_floor — color, normal GL, roughness
https://polyhaven.com/a/studio_small_08 — 1K HDR (ملف courtyard.hdr يحتفظ باسم داخلي قديم)
الروابط المباشرة في assets من dl.polyhaven.org. تراخيص الخطوط وThree مرفقة.

## التطوير
npm install
npm run build
python -m http.server 8921
python test.py
