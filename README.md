# WEBORA – الموقع التعريفي

موقع WEBORA الرسمي: صفحات ثابتة (HTML/CSS/JS) بالعربية والإنجليزية، بلا أي مكتبات خارجية.

## البنية
| المسار | المحتوى |
|---|---|
| `content/ar.json` · `content/en.json` | كل نصوص الموقع. **عدّل النصوص من هنا فقط.** |
| `src/style.css` · `src/main.js` | التصميم والسلوك (القائمة، نموذج التواصل عبر واتساب) |
| `src/img/` | الشعار والأيقونات وصورة المشاركة |
| `build.py` | يبني الموقع من الملفات أعلاه |
| `public/` | الموقع الجاهز للنشر (يُولَّد تلقائياً، لا تعدّله يدوياً) |

الصفحات: الرئيسية `index.html` · الخدمات `services.html` · القطاعات `sectors.html` · آلية العمل والأسئلة `how.html`.
العربية في الجذر، والإنجليزية تحت `/en/`.

## التشغيل محلياً
```bash
python3 build.py
cd public && python3 -m http.server 8000
# افتح http://localhost:8000
```

## النشر
**GitHub Pages (الطريقة المعتمدة):** ملف `.github/workflows/deploy-pages.yml` يبني الموقع وينشره تلقائياً مع كل تحديث على `main`.
تفعيل لمرة واحدة: Settings ← Pages ← Source: **GitHub Actions**.
(GitHub Pages مجاني للمستودعات العامة؛ المستودع الخاص يحتاج اشتراك GitHub Pro.)

بديل: Vercel عبر `vercel.json`.

بعد ربط النطاق، ضع رابطه في `SITE_URL` داخل `build.py` لتفعيل الروابط الأساسية (canonical/hreflang) وملف `sitemap.xml` وصورة المشاركة.

## التواصل
واتساب واتصال: +968 9746 4626
