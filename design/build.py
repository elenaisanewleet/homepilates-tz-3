"""Build the offline review site using the shared studio content and archived images."""
from html import escape
from pathlib import Path
import shutil
import subprocess
import sys

PACK = Path(__file__).resolve().parents[1]
ROOT = PACK / "design" / "shared"
sys.path.insert(0, str(ROOT / "tools"))
import generate as base

D, L = base.DATA, base.LABEL
OUT = PACK / "review" / "site"
ASSETS = OUT / "assets"
SOURCE = PACK / "homepilates-sources"
PHOTOS = SOURCE / "photos-classes-homepilates-ru"
TEXTS = SOURCE / "texts"
PHOTOMAP = {
    "studio": ("3039_IMG_8788-min.jpg", "Тренер помогает выполнить упражнение на реформере"),
    "stretch": ("3138_zanyatie-pilatesom_3.png", "Тренер помогает с боковым вытяжением на реформере"),
    "group": ("3135_DSC_1333-min.jpg", "Группа выполняет упражнение на реформерах в студии"),
    "detail-hands-straps": ("6631_zhenskie-ruki-v-proc.png", "Руки держат ремень реформера"),
    "reformer-arms-up": ("3138_zanyatie-pilatesom_3.png", "Боковое вытяжение на реформере с тренером"),
    "reformer-trainer-assist": ("6437_krasivyj-trener-prid.png", "Тренер направляет движение на реформере"),
    "reformer-supine-trainer": ("6637_trener-priderzhivaet.png", "Упражнение лёжа на реформере"),
    "cadillac-seated-stretch": ("3964_IMG_9173_1-min.jpg", "Упражнение на растяжку с тренером"),
    "reformer-box-side-trainer": ("3838_devushka-s-trenerom-.png", "Тренер помогает выполнить боковой наклон"),
    "cadillac-pair-stretch": ("3761_krasivyj-trener-pomo.png", "Растяжка с ремнями на оборудовании студии"),
}
DASH = '<span class="dot" aria-hidden="true"></span>'
ICON_PATHS = {
    "next": "M4 12h15m-6-6 6 6-6 6",
    "prev": "M20 12H5m6 6-6-6 6-6",
    "out": "M6 18 18 6M7 6h11v11",
    "menu": "M4 8h16M8 16h12",
    "close": "m6 6 12 12M18 6 6 18",
    "account": "M16 8a4 4 0 1 1-8 0 4 4 0 1 1 8 0M4 21v-2a8 6 0 0 1 16 0v2",
    "pin": "M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0ZM14.3 10a2.3 2.3 0 1 1-4.6 0 2.3 2.3 0 0 1 4.6 0Z",
}


def icon(name):
    return (f'<svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false" '
            f'fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" '
            f'stroke-linejoin="round"><path d="{ICON_PATHS[name]}"/></svg>')


ARROW = icon("out")
NEXT = icon("next")


def link(href, label, cls="", decoration=""):
    return f'<a href="{escape(href)}" class="{cls}">{escape(label)}{decoration}</a>'


class Page(base.Page):
    def __init__(self, slug):
        super().__init__(slug, False)

    def photo(self, filename, alt="", cls="", priority=False):
        original, desc = PHOTOMAP[filename]
        stem = Path(original).stem
        timing = 'fetchpriority="high"' if priority else 'loading="lazy"'
        return (f'<img class="photo {cls}" src="{self.assets}/{stem}.webp" alt="{escape(desc)}" '
                f'{timing} decoding="async">')

    def brand(self):
        return (f'<a class="brand" href="{self.link("")}"><img src="{self.assets}/logo.svg" '
                'width="38" height="38" alt=""><span>HomePilates</span></a>')

    def menu(self, cls):
        items = []
        for slug, title in D["pages"].items():
            # The full page name remains the accessible name of the compact navigation link.
            label = "Сертификаты" if slug == "sertifikaty" and cls == "nav" else title
            current = ' aria-current="page"' if slug == self.slug else ""
            items.append(f'<a href="{self.link(slug)}"{current} aria-label="{title}">{label}</a>')
        return f'<nav class="{cls}" aria-label="{"Основное меню" if cls != "footnav" else "Разделы в подвале"}">' + "".join(items) + '</nav>'

    def header(self):
        cabinet = self.link("", "#cabinet")
        return (f'<a class="skip" href="#content">К содержанию</a><header class="bar"><div class="wrap bar-inner">'
                f'{self.brand()}{self.menu("nav")}<a class="cab" href="{cabinet}" aria-label="{L["account"]}">'
                f'{icon("account")}<span class="cab-wide">{L["account"]}</span><span class="cab-short">Кабинет</span></a>'
                f'<button class="burger" type="button" aria-label="Открыть меню" aria-expanded="false" '
                f'aria-haspopup="dialog" aria-controls="sections">{icon("menu")}</button></div></header>'
                f'<dialog id="sections" class="menu-drawer" aria-labelledby="menu-title">'
                f'<div class="drawer-head"><h2 id="menu-title">Меню</h2><button type="button" '
                f'class="drawer-close" aria-label="Закрыть меню" autofocus>{icon("close")}</button></div>'
                f'{self.menu("drawer-links")}<a class="drawer-account" href="{cabinet}">'
                f'{icon("account")}{L["account"]}</a></dialog>')

    def action(self, target="raspisanie", label=None, anchor=""):
        return link(self.link(target, anchor), label or L["book"], "action", NEXT)

    def crumb(self):
        return (f'<div class="crumb">{link(self.link(""),"Главная")}<span aria-hidden="true">/</span>'
                f'<span>{self.title}</span></div>')

    def intro(self, text, photo=None):
        side = f'<figure>{self.photo(photo, priority=True)}</figure>' if photo else ''
        return (f'<section class="intro"><div class="wrap">{self.crumb()}<div class="intro-grid">'
                f'<div><h1>{self.title}</h1>{base.p(text) if text else ""}</div>{side}</div></div></section>')

    def legal_link(self, key):
        return self.prefix + "legal/" + key + "/index.html"

    def consent(self):
        start, end = base.LEGAL["consent"].rsplit(" ", 1)
        return f'<label class="check"><input type="checkbox" required><span>{start} {link(self.legal_link("policy"),end,"under")}</span></label>'

    def footer(self):
        c, legal = base.CONTACT, base.LEGAL
        terms = "".join(f'<dt>{escape(k)}</dt><dd>{escape(v)}</dd>' for k,v in legal["requisites"].items())
        return (f'<footer><div class="wrap"><div class="footgrid"><div>{self.brand()}<p>{c["hours"]}</p></div>'
                f'{self.menu("footnav")}<div class="contact-lines">{link(c["bot"], L["footerBot"])}'
                f'<span>{base.max_contact()}</span>{link(self.link("kontakty","#feedback"),L["feedback"])}{base.social()}</div></div>'
                f'<div class="legal"><details><summary>{L["requisites"]}</summary><dl>{terms}</dl></details>'
                f'<div class="policy-links">{link(self.legal_link("policy"), L["policy"])}'
                f'{link(self.legal_link("approval"), L["approval"])}<button data-cookie-open>Cookie</button></div></div></div></footer>')

    def widget(self, kind, button, section=""):
        if kind == "schedule":
            return external_panel("Расписание Мобифитнес", "Локальный прототип. Расписание студии доступно для просмотра при подключении к интернету. Запись проверяется на тестовом стенде.", "Показать расписание",
                                  "https://r308687.mobi.fitness/?club=9514", readonly=True)
        title = "Магазин Мобифитнес" if section else "Личный кабинет"
        msg = ("Покупка и доставка сертификата будут доступны на подключённом стенде." if section else
               "Вход по SMS, покупка и запись будут доступны на подключённом стенде.")
        return (f'<div class="service"><div class="eyebrow">{DASH}Локальный прототип</div>'
                f'<h3>{title}</h3><p>{msg}</p>{self.consent()}<button class="action" disabled>{button}</button></div>')


def external_panel(title, message, button, url, readonly=False):
    # A live schedule may be viewed by explicit choice. Keep all booking operations out of the local prototype.
    mode = ' data-readonly' if readonly else ''
    return (f'<div class="service" data-view="{escape(url)}"{mode}><div class="eyebrow">{DASH}Модуль просмотра</div>'
            f'<h3>{title}</h3><p>{message}</p><button class="outline" type="button" aria-expanded="false">{button}</button>'
            f'<div class="viewer" hidden></div></div>')


def home(pg):
    h = D["home"]
    first, last = h["title"].split(" — ",1)
    lead, separator, before_dash = first.rpartition(" ")
    nav = "".join(link(pg.link(slug), title, "tile", ARROW) for slug,title in D["pages"].items() if slug)
    org = D["integrations"]["organization"]
    images = "".join(f'<div data-slide {"" if n == 0 else "hidden"}>{pg.photo(name,priority=n==0)}</div>' for n,name in enumerate(("studio","stretch","group")))
    return f"""
<section class="hero"><div class="wrap hero-grid">
  <div class="hero-copy"><span class="place">{icon("pin")}{L["brandPlace"]}</span>
    <h1>{escape(lead)}{separator}<span class="keep">{escape(before_dash)} —</span> <em>{escape(last)}</em></h1><p>{h["intro"]}</p><p class="trial">{h["trial"]}</p>
    <div class="actions">{pg.action()}{link(pg.link("stoimost"),"Стоимость","secondary",ARROW)}</div></div>
  <figure class="studio-photo"><div class="frames">{images}</div>
    <figcaption><span class="photo-label"><i></i>HomePilates</span>
      <span class="gallery-controls"><button data-prev aria-label="Предыдущее фото">{icon("prev")}</button>
      <span data-count aria-live="polite">01 / 03</span><button data-next aria-label="Следующее фото">{icon("next")}</button></span></figcaption>
  </figure></div></section>
<section class="band wrap atlas" aria-labelledby="why-title">
  <div class="atlas-copy"><div class="plate-index">Атлас движения <span>01 / 03</span></div>
    <h2 id="why-title">{h["whyTitle"]}</h2>{base.p(h["why"])}</div>
  <figure class="plate"><div class="plate-heading"><span>Реформер</span><span>Фиг. 01</span></div>
    <img src="{pg.assets}/reformer.svg" width="670" height="376" loading="lazy"
         alt="Реформер в перспективе. Выноски указывают на каретку, упор и ремни.">
    <figcaption><span><b>01</b> Каретка</span><span><b>02</b> Упор</span><span><b>03</b> Ремни</span></figcaption>
  </figure></section>
<section class="wash audience"><div class="band wrap split"><figure>{pg.photo("reformer-trainer-assist")}</figure><div><span class="index">02</span><h2>{h["whoTitle"]}</h2>{base.listing(h["who"])}</div></div></section>
<section class="band wrap split lesson"><div><span class="index">03</span><h2>{h["lessonTitle"]}</h2>{base.p(h["lesson"])}</div>{base.listing(h["steps"],True)}</section>
<div class="quote"><div class="wrap"><blockquote>{h["quote"]}</blockquote><cite>{h["author"]}</cite></div></div>
<section class="band wrap split"><div><h2>{L["reviews"]}</h2>{link(D["integrations"]["map"]+"reviews/", L["maps"],"under",ARROW)}</div>{external_panel("Отзывы студии","Отзывы загружаются с Яндекс Карт.","Показать отзывы","https://yandex.ru/maps-reviews-widget/"+org+"?comments")}</section>
<nav class="band wrap tilelinks" aria-label="Разделы сайта">{nav}</nav>
<section id="cabinet" class="cabinet-panel"><div class="band wrap split"><h2>{h["cta"]}</h2>{pg.widget("personal",L["account"])}</div></section>"""


def prices(pg):
    d = D["prices"]
    groups = []
    for i, group in enumerate(d["groups"]):
        cols = d["columns"] if i else d["singleColumns"]
        head = "".join(f'<th scope="col">{x}</th>' for x in cols)
        rows = []
        for row in group["rows"]:
            cells = []
            for j,(label,value) in enumerate(zip(cols,row)):
                val = escape(value)
                if j == 2 and " вместо " in val:
                    val, old = val.split(" вместо ")
                    val += f' <small>вместо <s>{old}</s></small>'
                cells.append(f'<td data-label="{label}">{val}</td>')
            rows.append('<tr>' + "".join(cells) + '</tr>')
        title = escape(group["title"])
        groups.append(f'<details class="tariff" {"open" if not i else ""}><summary><span class="index">{i+1:02d}</span>'
                      f'<span>{title}</span></summary><table aria-label="{title}"><thead><tr>{head}</tr></thead>'
                      f'<tbody>{"".join(rows)}</tbody></table></details>')
    return (f'<section class="price-intro"><div class="wrap">{pg.crumb()}<div class="price-head"><div>'
            f'<h1>{pg.title}</h1><p>{d["intro"]}</p></div><figure>{pg.photo("detail-hands-straps",priority=True)}</figure></div></div></section>'
            f'<section class="wrap tariff-grid"><aside><h2>{d["title"]}</h2>{pg.action()}</aside><div>{"".join(groups)}</div></section>'
            f'<section class="wash"><div class="band wrap split"><h2>{d["notice"]}</h2>{base.p(d["rule"])}</div></section>')


def team(pg):
    team = D["team"]
    rows = []
    for i, person in enumerate(team["people"],1):
        bio = person["bio"]
        if person["name"] == "Татьяна Негреева":
            source = (TEXTS / "classes-homepilates-ru.txt").read_text()
            bio = source[source.index("Привет, я Татьяна"):source.index("НАШи тренеры")].strip().split("\n\n")
        copy = "".join(base.p(para) for para in bio)
        if person["name"] == "Татьяна Негреева":
            copy = f'<details><summary>Биография из материалов студии</summary>{copy}<p>Актуальный стаж — [уточнить].</p></details>'
        rows.append(f'<article class="person"><div class="eyebrow">{i:02d} / 05</div><h2>{person["name"]}</h2>{copy}</article>')
    return pg.intro(team["intro"]) + '<section class="band wrap people">' + "".join(rows) + '</section>'


def contacts(pg):
    c = base.CONTACT
    org = D["integrations"]["organization"]
    source = base.contacts(pg)
    start = source.index('<section class="band')
    source = pg.intro("") + source[start:]
    a = source.index('<iframe'); b = source.index('</iframe>',a)+9
    source = source[:a] + external_panel(L["maps"], c["address"], "Показать карту",
                        f"https://yandex.ru/map-widget/v1/?oid={org}&ol=biz&z=16") + source[b:]
    a = source.index('<form'); b = source.index('</form>',a)+7
    form = (f'<form class="form-grid" data-feedback><p>Локальный прототип. Отправка в студию не подключена.</p>'
            '<label>Телефон<input type="tel" autocomplete="tel" required></label>'
            '<label>Сообщение<textarea rows="3" required></textarea></label>'
            f'{pg.consent()}<button class="action" type="submit">Отправить</button>'
            '<p role="status" class="feedback-status"></p></form>')
    return source[:a] + form + source[b:]


def page_html(pg, body):
    title = escape(pg.title + " — HomePilates")
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><meta name="description" content="{escape(D["seo"][pg.slug])}"><meta name="robots" content="noindex,nofollow">'
            f'<link rel="icon" href="{pg.assets}/logo.svg"><link rel="stylesheet" href="{pg.assets}/style.css">'
            f'<script defer src="{pg.assets}/ui.js"></script></head><body>{pg.header()}<main id="content" tabindex="-1">{body}</main>'
            f'{pg.footer()}{base.cookie_box()}</body></html>')


def build():
    ASSETS.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "site/assets/fonts", ASSETS/"fonts", dirs_exist_ok=True)
    # Remove empty margins of the supplied vector; the drawing itself stays intact.
    svg = (SOURCE/"logo/logo_homepilates_new.svg").read_text().replace('viewBox="0 0 10000 10000"', 'viewBox="2180 2350 5700 5400"')
    (ASSETS/"logo.svg").write_text(svg)
    for name in sorted({p[0] for p in PHOTOMAP.values()}):
        subprocess.run(["cwebp","-quiet","-q","83",str(PHOTOS/name),"-o",str(ASSETS/(Path(name).stem+".webp"))],check=True)
    (ASSETS/"style.css").write_text((ROOT/"tools/fonts.css").read_text().replace("__ASSETS__", ".") + (PACK/"design/style.css").read_text())
    for asset in ("ui.js", "reformer.svg"):
        shutil.copy(PACK / "design" / asset, ASSETS / asset)
    pages = {**base.PAGES,"":home,"stoimost":prices,"komanda":team,"kontakty":contacts}
    for slug,renderer in pages.items():
        pg = Page(slug)
        path = OUT/slug/"index.html"
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(page_html(pg,renderer(pg)))
    for slug,filename,label in [("policy","privacy_policy","policy"),("approval","approval","approval")]:
        text = (TEXTS/f"classes-homepilates-ru-{filename}.txt").read_text().split("\n",1)[1].strip()
        pars = "".join(base.p(x) for x in text.split("\n\n"))
        path = OUT/"legal"/slug/"index.html"
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(f'<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                        f'<title>{L[label]} — HomePilates</title><link rel="stylesheet" href="../../assets/style.css">'
                        f'<main class="legal-doc"><a class="under" href="../../index.html">Главная</a><h1>{L[label]}</h1>{pars}</main></html>')

if __name__ == "__main__":
    build()
