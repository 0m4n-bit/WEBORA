#!/usr/bin/env python3
"""
WEBORA static site builder.

Reads the copy from content/ar.json and content/en.json, the assets in src/,
and writes the finished website to public/.

    python3 build.py

No third-party packages are needed (Python 3.8+).
Arabic pages live at the site root, English pages under /en/.
"""
import json
import shutil
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "public"

# Set this once the domain is ready (e.g. "https://webora.om") to enable
# canonical/hreflang URLs, Open Graph URLs and sitemap.xml.
SITE_URL = ""

PHONE_E164 = "+96897464626"
PHONE_DISPLAY = "+968 9746 4626"
WHATSAPP = "https://wa.me/96897464626"

PAGES = {"home": "index.html", "services": "services.html", "sectors": "sectors.html", "how": "how.html"}

META = {
    "ar": {
        "home": ("WEBORA | مواقع وحجوزات ومحاسبة ذكية للأعمال في عُمان",
                 "منصة WEBORA: مواقع ومتاجر إلكترونية، ونظام حجوزات، ومحاسبة ذكية باشتراك شهري للصالونات والعيادات ومتاجر الملابس والمنتجات في سلطنة عُمان."),
        "services": ("الخدمات | WEBORA",
                     "المواقع والمتاجر الإلكترونية، ونظام الحجوزات، والمحاسبة الذكية بالريال العُماني مع ضريبة القيمة المضافة، في منصة واحدة متكاملة."),
        "sectors": ("القطاعات | WEBORA",
                    "حلول رقمية للصالونات ومراكز التجميل، والعيادات والمراكز الطبية، ومتاجر الملابس والمنتجات في سلطنة عُمان."),
        "how": ("آلية العمل والأسئلة الشائعة | WEBORA",
                "كيف نعمل من الاستشارة المجانية حتى الإطلاق والدعم المستمر، وإجابات أكثر الأسئلة شيوعاً حول منصة WEBORA."),
        "nameError": "يرجى كتابة الاسم.",
        "skip": "تخطَّ إلى المحتوى",
    },
    "en": {
        "home": ("WEBORA | Websites, Booking & Smart Accounting for Businesses in Oman",
                 "WEBORA: websites and online stores, online booking and smart accounting in one monthly subscription for salons, clinics, and clothing and product stores in Oman."),
        "services": ("Services | WEBORA",
                     "Websites and online stores, a booking system and smart accounting in OMR with VAT, in one integrated platform."),
        "sectors": ("Industries | WEBORA",
                    "Digital solutions for salons and beauty centers, clinics and medical centers, and clothing and product stores in Oman."),
        "how": ("How it works & FAQ | WEBORA",
                "How we work from a free consultation to launch and ongoing support, plus answers to common questions about WEBORA."),
        "nameError": "Please enter your name.",
        "skip": "Skip to content",
    },
}

# ---------------------------------------------------------------- icons
def svg(paths, size=20, stroke=1.8, extra=""):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{extra}>{paths}</svg>')

ICON = {
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/>',
    "calendar": '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4M8.5 15l2.3 2.3 4.7-4.6"/>',
    "chart": '<path d="M5 20v-6M10 20v-9M15 20v-7M20 20V9"/><path d="m4 11 5-5 4 3 7-6M16 3h4v4"/>',
    "scissors": '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4 8.1 15.9M14.5 14.5 20 20M8.1 8.1 12 12"/>',
    "clinic": '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M12 8v8M8 12h8"/>',
    "bag": '<path d="M5 8h14l-1 13H6L5 8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    "alert": '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    "chat": '<path d="M21 11.5a8.4 8.4 0 0 1-12.4 7.4L3 21l2.1-5.4A8.4 8.4 0 1 1 21 11.5z"/>',
}
SERVICE_ICONS = ["globe", "calendar", "chart"]
SECTOR_ICONS = ["scissors", "clinic", "bag"]

e = escape


# ---------------------------------------------------------------- layout
def prefix(lang):
    return "" if lang == "ar" else "../"


def page_url(lang, key):
    return ("" if lang == "ar" else "en/") + PAGES[key]


def head(lang, key):
    title, desc = META[lang][key]
    p = prefix(lang)
    other = "en" if lang == "ar" else "ar"
    extra = ""
    if SITE_URL:
        base = SITE_URL.rstrip("/") + "/"
        extra = (f'<link rel="canonical" href="{base}{page_url(lang, key)}">\n'
                 f'<link rel="alternate" hreflang="ar" href="{base}{page_url("ar", key)}">\n'
                 f'<link rel="alternate" hreflang="en" href="{base}{page_url("en", key)}">\n'
                 f'<link rel="alternate" hreflang="x-default" href="{base}{page_url("ar", key)}">\n'
                 f'<meta property="og:url" content="{base}{page_url(lang, key)}">\n'
                 f'<meta property="og:image" content="{base}assets/og-image.png">\n')
    ld = ""
    if key == "home":
        data = {"@context": "https://schema.org", "@type": "Organization", "name": "WEBORA",
                "telephone": PHONE_E164, "areaServed": "OM",
                "slogan": "Your Business, Digitally Connected."}
        if SITE_URL:
            data["url"] = SITE_URL
            data["logo"] = SITE_URL.rstrip("/") + "/assets/logo-mark.png"
        ld = f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>\n'
    return f"""<!doctype html>
<html lang="{lang}" dir="{'rtl' if lang == 'ar' else 'ltr'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#0B1428">
<meta property="og:type" content="website">
<meta property="og:site_name" content="WEBORA">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:locale" content="{'ar_OM' if lang == 'ar' else 'en_US'}">
{extra}<link rel="icon" type="image/png" href="{p}assets/favicon.png">
<link rel="apple-touch-icon" href="{p}assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&amp;family=Inter:wght@400;500;600;700&amp;display=swap">
<link rel="stylesheet" href="{p}assets/style.css?v={VERSION}">
{ld}</head>
<body>
<a class="skip-link" href="#main">{e(META[lang]['skip'])}</a>
"""


def header(c, lang, key):
    h = c["header"]
    p = prefix(lang)
    other = "en" if lang == "ar" else "ar"
    other_href = (f"en/{PAGES[key]}" if lang == "ar" else f"../{PAGES[key]}")

    def links(cls=""):
        out = []
        for k in PAGES:
            cur = ' aria-current="page"' if k == key else ""
            out.append(f'<a href="{PAGES[k]}"{cur}>{e(h["pages"][k])}</a>')
        return "\n".join(out)

    return f"""<header class="site-header">
<div class="container header-bar">
<a class="brand" href="index.html" aria-label="WEBORA">
<img src="{p}assets/logo-mark.png" alt="" width="39" height="30">
<span dir="ltr">WEBORA</span>
</a>
<nav class="nav" aria-label="{e(h['navLabel'])}">
{links()}
</nav>
<div class="header-actions">
<a class="btn-ghost" href="{other_href}" hreflang="{other}" lang="{other}">{svg(ICON['globe'], 16)}<span>{e(h['langSwitch'])}</span></a>
<a class="btn-light" href="{WHATSAPP}" target="_blank" rel="noopener">{e(h['cta'])}</a>
<button class="burger" type="button" aria-expanded="false" aria-controls="mobile-nav" aria-label="{e(h['menu'])}">{svg(ICON['menu'], 20, 2)}</button>
</div>
</div>
<nav class="mobile-nav" id="mobile-nav" aria-label="{e(h['navLabel'])}">
{links()}
<a class="btn-light" href="{WHATSAPP}" target="_blank" rel="noopener">{e(h['cta'])}</a>
</nav>
</header>
<main id="main">
"""


def footer(c, lang, show_cta):
    f = c["footer"]
    p = prefix(lang)
    cta = ""
    if show_cta:
        cta = f"""<section class="container cta-wrap" aria-label="{e(f['ctaTitle'])}">
<div class="cta-band">
<div>
<h2>{e(f['ctaTitle'])}</h2>
<p>{e(f['ctaSub'])}</p>
</div>
<div class="btn-row">
<a class="btn btn-white" href="{WHATSAPP}" target="_blank" rel="noopener">{svg(ICON['chat'])}<span>{e(f['wa'])}</span></a>
<a class="btn btn-outline-white" href="tel:{PHONE_E164}">{e(f['call'])}</a>
</div>
</div>
</section>
"""
    year = date.today().year
    rights = f["rights"].replace("2026", str(year))
    return f"""{cta}</main>
<footer class="site-footer">
<div class="container">
<div class="footer-grid">
<div>
<div class="footer-brand"><img src="{p}assets/logo-mark.png" alt="" width="36" height="28"><span dir="ltr">WEBORA</span></div>
<p class="footer-about">{e(f['about'])}</p>
<p class="tagline" dir="ltr">Your Business, Digitally Connected.</p>
</div>
<div>
<h3>{e(f['pagesH'])}</h3>
<div class="links">
<a href="index.html">{e(f['p1'])}</a>
<a href="services.html">{e(f['p2'])}</a>
<a href="sectors.html">{e(f['p3'])}</a>
<a href="how.html">{e(f['p4'])}</a>
</div>
</div>
<div>
<h3>{e(f['servicesH'])}</h3>
<div class="links">
<a href="services.html">{e(f['s1'])}</a>
<a href="services.html">{e(f['s2'])}</a>
<a href="services.html">{e(f['s3'])}</a>
</div>
</div>
<div>
<h3>{e(f['contactH'])}</h3>
<div class="links">
<a href="tel:{PHONE_E164}" dir="ltr" class="latin">{PHONE_DISPLAY}</a>
<a href="{WHATSAPP}" target="_blank" rel="noopener">WhatsApp</a>
<span>{e(f['country'])}</span>
</div>
</div>
</div>
<p class="copyright">{e(rights)}</p>
</div>
</footer>
<script src="{p}assets/main.js?v={VERSION}" defer></script>
</body>
</html>
"""


def section_head(kicker, title, sub=None, tag="h2"):
    s = f'<p class="kicker">{e(kicker)}</p>\n<{tag} class="{"h1" if tag == "h1" else "h2"}">{e(title)}</{tag}>\n'
    if sub:
        s += f'<p class="lead">{e(sub)}</p>\n'
    return s


def page_hero(kicker, title, sub, extra=""):
    return f"""<section class="grid-bg">
<div class="container page-hero">
{section_head(kicker, title, sub, "h1")}{extra}</div>
</section>
"""


def check_items(items, icon="check"):
    return "\n".join(f'<li>{svg(ICON[icon], 18, 2.2)}<span>{e(i)}</span></li>' for i in items)


def chips(items, cls="chip"):
    return '<div class="chips">' + "".join(f'<span class="{cls}">{e(i)}</span>' for i in items) + "</div>"


# ---------------------------------------------------------------- pages
def home(c, lang):
    t = c["home"]
    p = prefix(lang)
    pillars = "\n".join(
        f'<li class="pillar">{svg(ICON[SERVICE_ICONS[i]], 36, 1.3)}<span>{e(x)}</span></li>' for i, x in enumerate(t["pillars"]))
    strip = "\n".join(f"<li>{e(x)}</li>" for x in t["strip"]["items"])
    services = "\n".join(
        f'<article class="panel"><span class="num" dir="ltr">{e(s["num"])}</span><h3>{e(s["title"])}</h3><p>{e(s["desc"])}</p></article>'
        for s in t["services"]["list"])
    why = "\n".join(
        f'<div class="card"><h3>{svg(ICON["check-circle"], 18, 2)}<span>{e(w["title"])}</span></h3><p>{e(w["desc"])}</p></div>'
        for w in t["why"]["list"])
    ct = t["contact"]
    options = "\n".join(f'<option>{e(o)}</option>' for o in ct["types"])
    return f"""<section class="grid-bg">
<div class="container hero">
<img class="hero-mark" src="{p}assets/logo-mark.png" alt="" width="94" height="72">
<p class="badge">{e(t['hero']['badge'])}</p>
<h1>{e(t['hero']['title1'])}<br><span>{e(t['hero']['title2'])}</span></h1>
<p class="lead">{e(t['hero']['sub'])}</p>
<div class="btn-row">
<a class="btn btn-primary" href="#contact">{e(t['hero']['cta1'])}</a>
<a class="btn btn-outline" href="services.html">{e(t['hero']['cta2'])}</a>
</div>
<ul class="pillars">
{pillars}
</ul>
</div>
</section>
<section class="strip" aria-label="{e(t['strip']['label'])}">
<div class="container">
<span class="muted">{e(t['strip']['label'])}</span>
<ul class="strip-items">
{strip}
</ul>
</div>
</section>
<section class="section">
<div class="container">
<div class="section-head section-head--row">
<div>{section_head(t['services']['kicker'], t['services']['title'])}</div>
<a class="text-link" href="services.html">{e(t['services']['all'])}</a>
</div>
<div class="panel-grid">
{services}
</div>
</div>
</section>
<section class="section section--alt">
<div class="container split">
<div class="split-side">{section_head(t['why']['kicker'], t['why']['title'], t['why']['sub'])}</div>
<div class="split-main card-grid">
{why}
</div>
</div>
</section>
<section class="section" id="contact">
<div class="container contact">
<div class="contact-info">
{section_head(ct['kicker'], ct['title'], ct['sub'])}
<a class="phone-card" href="tel:{PHONE_E164}">
<span class="ico">{svg(ICON['phone'])}</span>
<span><small>{e(ct['phoneLabel'])}</small><strong dir="ltr">{PHONE_DISPLAY}</strong></span>
</a>
</div>
<form class="form" id="contact-form" novalidate
 data-intro="{e(ct['waIntro'])}" data-l-name="{e(ct['waName'])}" data-l-biz="{e(ct['waType'])}" data-l-msg="{e(ct['waMsg'])}">
<div class="field">
<label for="f-name">{e(ct['name'])}</label>
<input id="f-name" name="name" type="text" autocomplete="name" required aria-describedby="f-name-err">
<span class="error" id="f-name-err">{e(META[lang]['nameError'])}</span>
</div>
<div class="field">
<label for="f-biz">{e(ct['type'])}</label>
<select id="f-biz" name="business">
{options}
</select>
</div>
<div class="field">
<label for="f-msg">{e(ct['msg'])}</label>
<textarea id="f-msg" name="message" rows="4"></textarea>
</div>
<button class="btn btn-primary" type="submit">{svg(ICON['chat'])}<span>{e(ct['send'])}</span></button>
<p class="form-note">{e(ct['note'])}</p>
</form>
</div>
</section>
"""


def services(c, lang):
    t = c["services"]
    blocks = []
    for i, s in enumerate(t["svc"]):
        feats = "\n".join(
            f'<div class="card"><h3>{svg(ICON["check"], 18, 2)}<span>{e(f["t"])}</span></h3><p>{e(f["d"])}</p></div>'
            for f in s["features"])
        blocks.append(f"""<section class="service">
<div class="container">
<div class="service-intro">
<div class="head"><span class="icon-box">{svg(ICON[SERVICE_ICONS[i]], 30, 1.4)}</span><span class="num" dir="ltr">0{i + 1}</span></div>
<h2>{e(s['title'])}</h2>
<p class="desc">{e(s['desc'])}</p>
<p class="label">{e(t['fitFor'])}</p>
{chips(s['fit'])}
</div>
<div class="service-features">
{feats}
</div>
</div>
</section>""")
    fl = t["flow"]
    flow = "\n".join(
        f'<li class="step-card"><span class="step-num" dir="ltr">{i + 1}</span><h3>{e(x["t"])}</h3><p>{e(x["d"])}</p></li>'
        for i, x in enumerate(fl["list"]))
    return page_hero(t["kicker"], t["title"], t["sub"]) + "\n".join(blocks) + f"""
<section class="section section--alt">
<div class="container">
<div class="section-head">{section_head(fl['kicker'], fl['title'], fl['sub'])}</div>
<ol class="steps-grid">
{flow}
</ol>
</div>
</section>
"""


def sectors(c, lang):
    t = c["sectors"]
    jump = '<div class="chips">' + "".join(f'<a href="#{s["id"]}">{e(s["tag"])}</a>' for s in t["list"]) + "</div>\n"
    cards = []
    for i, s in enumerate(t["list"]):
        cards.append(f"""<article class="sector" id="{s['id']}">
<div class="sector-top">
<div class="main">
<p class="sector-tag"><span class="icon-box icon-box--dark">{svg(ICON[SECTOR_ICONS[i]], 26, 1.6)}</span><span>{e(s['tag'])}</span></p>
<h2>{e(s['title'])}</h2>
<p>{e(s['desc'])}</p>
</div>
<div class="side">
<p class="label">{e(t['suggested'])}</p>
{chips(s['services'], 'chip chip--accent')}
</div>
</div>
<div class="sector-bottom">
<div class="pains"><h3>{e(t['challenges'])}</h3><ul class="check-list">{check_items(s['pains'], 'alert')}</ul></div>
<div class="gains"><h3>{e(t['solutions'])}</h3><ul class="check-list">{check_items(s['gains'], 'check-circle')}</ul></div>
</div>
</article>""")
    return page_hero(t["kicker"], t["title"], t["sub"], jump) + f"""<section class="section">
<div class="container sectors">
{chr(10).join(cards)}
</div>
</section>
"""


def how(c, lang):
    t = c["how"]
    steps = "\n".join(f"""<li>
<div class="t-head"><span class="t-num" dir="ltr">0{i + 1}</span><div><h2>{e(s['title'])}</h2><p class="who">{e(s['who'])}</p></div></div>
<div class="t-body"><p>{e(s['desc'])}</p>{chips(s['out'])}</div>
</li>""" for i, s in enumerate(t["steps"]))
    need = t["need"]
    faq = t["faq"]
    qs = "\n".join(
        f'<details><summary><span>{e(q["q"])}</span>{svg(ICON["plus"], 20, 2)}</summary><p>{e(q["a"])}</p></details>'
        for q in faq["list"])
    return page_hero(t["kicker"], t["title"], t["sub"]) + f"""<section class="section">
<div class="container">
<ol class="timeline">
{steps}
</ol>
<div class="need">
<div><h2>{e(need['title'])}</h2><p class="muted">{e(need['sub'])}</p></div>
<ul>{check_items(need['list'])}</ul>
</div>
</div>
</section>
<section class="section section--alt" id="faq">
<div class="container split">
<div class="split-side">
{section_head(faq['kicker'], faq['title'], faq['sub'])}
<p style="margin-top:24px"><a class="btn btn-outline" href="{WHATSAPP}" target="_blank" rel="noopener">{e(faq['ask'])}</a></p>
</div>
<div class="split-main faq-list">
{qs}
</div>
</div>
</section>
"""


BUILDERS = {"home": (home, False), "services": (services, True), "sectors": (sectors, True), "how": (how, True)}
VERSION = date.today().strftime("%Y%m%d")


def faq_ld(c):
    items = [{"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
             for q in c["how"]["faq"]["list"]]
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    (OUT / "en").mkdir()
    for f in ["style.css", "main.js"]:
        shutil.copy(ROOT / "src" / f, OUT / "assets" / f)
    for f in (ROOT / "src" / "img").iterdir():
        shutil.copy(f, OUT / "assets" / f.name)

    for lang in ["ar", "en"]:
        c = json.loads((ROOT / "content" / f"{lang}.json").read_text(encoding="utf-8"))
        for key, (fn, cta) in BUILDERS.items():
            html = head(lang, key)
            if key == "how":
                html = html.replace("</head>", f'<script type="application/ld+json">{json.dumps(faq_ld(c), ensure_ascii=False)}</script>\n</head>')
            html += header(c, lang, key) + fn(c, lang) + footer(c, lang, cta)
            (OUT / page_url(lang, key)).write_text(html, encoding="utf-8")

    # 404 page (Arabic + English)
    (OUT / "404.html").write_text(f"""<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>الصفحة غير موجودة | WEBORA</title><meta name="robots" content="noindex">
<link rel="icon" type="image/png" href="/assets/favicon.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;600;700&amp;family=Inter:wght@600;700&amp;display=swap">
<link rel="stylesheet" href="/assets/style.css?v={VERSION}"></head>
<body><main class="grid-bg" style="min-height:100vh;display:flex;align-items:center">
<div class="container hero"><img class="hero-mark" src="/assets/logo-mark.png" alt="WEBORA" width="94" height="72">
<h1>الصفحة غير موجودة</h1><p class="lead" lang="en" dir="ltr">Page not found</p>
<div class="btn-row"><a class="btn btn-primary" href="/">العودة للرئيسية</a><a class="btn btn-outline" href="/en/" lang="en">Back to home</a></div>
</div></main></body></html>
""", encoding="utf-8")

    robots = "User-agent: *\nAllow: /\n"
    if SITE_URL:
        base = SITE_URL.rstrip("/") + "/"
        robots += f"Sitemap: {base}sitemap.xml\n"
        urls = "".join(f"<url><loc>{base}{page_url(l, k)}</loc></url>" for l in ["ar", "en"] for k in PAGES)
        (OUT / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
            encoding="utf-8")
    (OUT / "robots.txt").write_text(robots, encoding="utf-8")
    print("Built", sum(1 for _ in OUT.rglob("*.html")), "pages into", OUT)


if __name__ == "__main__":
    build()
