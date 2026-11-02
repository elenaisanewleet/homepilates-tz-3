"""Regenerate the static site and Tilda T123 blocks. Python 3, no dependencies."""
import json
from html import escape as esc
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools"
DATA = json.loads((ROOT / "content.json").read_text())
SITE, TILDA = ROOT / "site", ROOT / "tilda"
ASSET_CDN = "https://cdn.jsdelivr.net/gh/elenaisanewleet/homepilates-tz@7d21b5c8de5e5a31d09ea95fac29a1acda797ac6/site/assets"
LABEL = DATA["labels"]
CONTACT = DATA["contacts"]
LEGAL = DATA["legal"]
INTEGR = DATA["integrations"]
MISS = DATA["placeholder"]


def a(url, text, classes="textlink"):
    return f'<a class="{classes}" href="{esc(url)}">{esc(text)}</a>'


def p(text):
    return f'<p>{esc(text)}</p>'


def listing(items, numbered=False):
    tag, cls = ("ol", "steps") if numbered else ("ul", "list")
    return f'<{tag} class="{cls}">' + "".join(f'<li>{esc(x)}</li>' for x in items) + f'</{tag}>'


def consent():
    start, end = LEGAL["consent"].rsplit(" ", 1)
    return (f'<label class="check"><input type="checkbox" name="{esc(LABEL["approval"])}" '
            f'value="{esc(LEGAL["consent"])}" required><span>{esc(start)} '
            f'{a(LEGAL["policy"], end)}</span></label>')


def social():
    icons = {
        "vk": "M2 5h3.6c.4 5 2.7 8 4.7 8.7V5H14v5.1c2-.2 4.1-2.6 4.9-5.1h3.5c-.7 3.2-3 5.7-4.7 6.8 1.7.9 4.3 3.1 5.1 6.7h-3.9c-.9-2.3-2.6-4.1-4.9-4.4v4.4h-.6C6.1 18.5 2.5 13.5 2 5Z",
        "telegram": "M21.8 3.2 18.3 20c-.3 1.2-1 1.5-2 .9l-5.4-4-2.6 2.5.4-5.6L18.9 5.9 6.3 12.6l-4.8-1.5c-1-.3-1-1 .2-1.5L20.4 2.5c.9-.3 1.6.1 1.4.7Z"
    }
    return '<div class="social">' + "".join(
        f'<a aria-label="{esc(LABEL[key])}" href="{esc(CONTACT[key])}"><svg viewBox="0 0 24 24" '
        f'aria-hidden="true"><path d="{path}"/></svg></a>' for key, path in icons.items()) + '</div>'


def max_contact():
    label = LABEL["max"] + ": " + CONTACT["messengerPhone"]
    if CONTACT["maxUrl"]:
        return a(CONTACT["maxUrl"], label)
    return f'{esc(label)} <span class="missing">{MISS}</span>'


def cookie_box():
    config = DATA["cookie"]
    names = ["essential-cookie", "analytics", "ads"]
    opts = "".join(f'<label class="check"><input type="checkbox" name="{name}" '
                   f'{"checked disabled" if i == 0 else ""}><span>{esc(text)}</span></label>'
                   for i, (name, text) in enumerate(zip(names, config["categories"])))
    return (f'<form class="cookie-box" aria-label="{LABEL["cookie"]}" hidden>{p(config["intro"])}'
            f'<details><summary>{LABEL["categories"]}</summary><div class="cookie-opts">{opts}</div></details>'
            f'<div class="cookie-foot"><button class="textlink" name="essential">{LABEL["essentialOnly"]}</button>'
            f'<button class="action" name="save">{LABEL["save"]}</button></div></form>')


class Page:
    def __init__(self, slug, embed):
        self.slug, self.embed = slug, embed
        self.prefix = "../" if slug else ""
        self.assets = ASSET_CDN if embed else self.prefix + "assets"
        self.title = DATA["pages"][slug]

    def link(self, target, anchor=""):
        if self.embed:
            return "/" + target + anchor
        return self.prefix + (target + "/" if target else "") + "index.html" + anchor

    def nav(self, cls):
        links = []
        for slug, title in DATA["pages"].items():
            current = ' aria-current="page"' if slug == self.slug else ""
            links.append(f'<a href="{self.link(slug)}"{current}>{esc(title)}</a>')
        return f'<nav class="{cls}" aria-label="{LABEL["menu"]}">' + "".join(links) + '</nav>'

    def brand(self):
        return (f'<a class="brand" href="{self.link("")}"><img src="{self.assets}/logo.svg" '
                f'width="38" height="38" alt=""><span>{esc(DATA["brand"])}</span></a>')

    def header(self):
        return (f'<header class="bar"><div class="wrap bar-inner">{self.brand()}'
                f'<div id="hp-sections">{self.nav("nav")}</div>'
                f'{a(self.link("", "#cabinet"), LABEL["account"], "cab")}'
                f'<button type="button" class="burger" aria-label="{LABEL["menu"]}" '
                'aria-expanded="false" aria-controls="hp-sections"><span></span><span></span></button>'
                '</div></header>')

    def footer(self):
        terms = "".join(f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>' for k,v in LEGAL["requisites"].items())
        return (f'<footer><div class="wrap"><div class="footgrid"><div>{self.brand()}</div>'
                f'{self.nav("footnav")}<div class="contact-lines">{a(CONTACT["bot"], LABEL["footerBot"])}'
                f'<span>{max_contact()}</span>{a(self.link("kontakty","#feedback"),LABEL["feedback"])}{social()}</div>'
                f'</div><div class="legal"><details><summary>{LABEL["requisites"]}</summary><dl>{terms}</dl></details>'
                f'<div class="policy-links">{a(LEGAL["policy"],LABEL["policy"])}'
                f'{a(LEGAL["approval"],LABEL["approval"])}'
                f'<button type="button" class="textlink" data-cookie-open>{LABEL["cookie"]}</button>'
                f'</div></div></div></footer>')

    def photo(self, filename, alt, cls="", priority=False):
        timing = 'fetchpriority="high"' if priority else 'loading="lazy"'
        return (f'<img class="photo {cls}" src="{self.assets}/photos/{filename}.jpg" '
                f'alt="{esc(alt)}" {timing} decoding="async">')

    def intro(self, text, photo=None):
        image = f'<figure>{self.photo(photo,self.title,priority=True)}</figure>' if photo else ""
        return (f'<section class="intro"><div class="wrap {"intro-media" if photo else ""}">'
                f'<div><span class="kicker">{DATA["brand"]}</span><h1>{esc(self.title)}</h1>'
                f'{p(text)}</div>{image}</div></section>')

    def action(self, target="raspisanie", label=None, anchor=""):
        return a(self.link(target,anchor),label or LABEL["book"],"action")

    def widget(self, kind, button, section=""):
        cfg = INTEGR["mobifitness"]
        params = dict(code=cfg["code"],club=cfg["club"],type=kind,language="ru",
                      version="v6",host=cfg["domain"])
        if section:
            params["section"] = section
        url = "https://" + cfg["domain"] + "/" + kind + "-widget/?" + urlencode(params)
        standalone = url + ("#" + section if section else "")
        title = DATA["pages"]["raspisanie"] if kind == "schedule" else LABEL["account"]
        return (f'<form class="form-grid" data-widget-form>'
                f'<button class="action" type="submit">{esc(button)}</button>{consent()}</form>'
                f'<div class="mobi" id="hp-mobi" data-code="{cfg["code"]}" data-club="{cfg["club"]}" '
                f'data-type="{kind}" data-section="{esc(section)}" data-url="{esc(url)}" data-title="{esc(title)}" inert></div>'
                f'{a(standalone,LABEL["mobiOpen"],"textlink go")}')

    def body(self):
        renderer = PAGES.get(self.slug)
        return renderer(self) if renderer else self.intro(DATA["seo"][self.slug])

    def fragment(self):
        script = (SRC / "runtime.js").read_text() if self.embed else ""
        js = f'<script>\n{script}</script>' if self.embed else f'<script src="{self.assets}/homepilates.js"></script>'
        return (f'<div class="hp" data-hp data-counter="{INTEGR["metrika"]}">{self.header()}'
                f'<main>{self.body()}</main>{self.footer()}{cookie_box()}</div>\n{js}\n')


PAGES = {}


def home(page):
    h = DATA["home"]
    shot = page.photo("studio-reformer-standing", h["whyTitle"], priority=True)
    sections = "".join(a(page.link(slug),title,"tile") for slug,title in DATA["pages"].items() if slug)
    reviews_url = "https://yandex.ru/maps-reviews-widget/" + INTEGR["organization"] + "?comments"
    return f"""
<section class="home-hero wrap">
  <div><span class="kicker">{LABEL["brandPlace"]}</span>
    <h1>{esc(h["title"])}</h1>{p(h["intro"])}{p(h["trial"])}
    <div class="actions">{page.action()}{a(page.link("stoimost"), DATA["pages"]["stoimost"], "textlink go")}</div>
  </div>
  <figure class="hero-shot">{shot}<figcaption class="credit">
    <span>{esc(CONTACT["hours"])}</span><span aria-hidden="true">01 / 08</span>
  </figcaption></figure>
</section>
<section class="band wrap split"><div><span class="section-id" aria-hidden="true">01</span>
  <h2>{h["whyTitle"]}</h2></div><div>{p(h["why"])}</div></section>
<section class="band wrap split"><figure>{page.photo("detail-feet-bar",h["whyTitle"])}</figure>
  <div><span class="section-id" aria-hidden="true">02</span><h2>{h["whoTitle"]}</h2>{listing(h["who"])}</div></section>
<section class="band wrap split"><div><span class="section-id" aria-hidden="true">03</span>
  <h2>{h["lessonTitle"]}</h2><div>{p(h["lesson"])}</div></div>{listing(h["steps"],True)}</section>
<div class="wrap quote"><blockquote>{esc(h["quote"])}</blockquote><cite>{esc(h["author"])}</cite></div>
<section class="band wrap split"><div><h2>{LABEL["reviews"]}</h2>
  <div>{a(INTEGR["map"]+"reviews/",LABEL["maps"],"textlink go")}</div></div>
  <iframe class="frame reviews" title="{LABEL["reviews"]}" loading="lazy" src="{reviews_url}"></iframe></section>
<nav class="band wrap tiles" aria-label="{LABEL["menu"]}">{sections}</nav>
<section id="cabinet" class="band wrap split"><div><span class="kicker">{LABEL["account"]}</span>
  <h2>{esc(h["cta"])}</h2></div><div>{page.widget("personal",LABEL["account"])}</div></section>"""


PAGES[""] = home


def directions(page):
    d = DATA["directions"]
    cards = []
    for i, item in enumerate(d["items"],1):
        title = esc(item["title"])
        image = page.photo(item["photo"],item["title"]) if item["photo"] else ""
        cards.append(f'<article class="card">{("<figure>"+image+"</figure>") if image else ""}'
                     f'<span class="section-id" aria-hidden="true">{i:02d}</span><h2>{title}</h2>'
                     f'{p(item["text"]) if item["text"] else ""}'
                     f'{a(page.link("raspisanie"),LABEL["book"],"textlink go")}</article>')
    return page.intro(d["intro"]) + '<div class="band wrap tiles">' + "".join(cards) + '</div>'


PAGES["napravleniya"] = directions


def schedule(page):
    s = DATA["schedule"]
    return (page.intro(s["intro"]) + '<section class="band wrap">'
            + page.widget("schedule", LABEL["book"]) + '</section>'
            + f'<section class="band wrap split"><h2>{LABEL["account"]}</h2><div>{p(s["rule"])}'
              f'<div class="actions">{page.action("", LABEL["account"], "#cabinet")}</div></div></section>')


PAGES["raspisanie"] = schedule


def prices(page):
    data = DATA["prices"]
    tables = []
    for i, group in enumerate(data["groups"]):
        columns = data["singleColumns"] if i == 0 else data["columns"]
        head = "".join(f'<th scope="col">{esc(col)}</th>' for col in columns)
        rows = []
        for cells in group["rows"]:
            row = "".join(f'<td data-label="{esc(col)}">{esc(value)}</td>' for col,value in zip(columns,cells))
            rows.append("<tr>" + row + "</tr>")
        title = esc(group["title"])
        tables.append(f'<details><summary><span class="index" aria-hidden="true">{i+1:02d}</span>{title}</summary>'
                      f'<div class="tablebox"><table aria-label="{title}"><thead><tr>{head}</tr></thead>'
                      f'<tbody>{"".join(rows)}</tbody></table></div></details>')
    return (page.intro(data["intro"]) + f'<section class="band wrap"><h2 class="details-header">{data["title"]}</h2>'
            + "".join(tables) + f'<div class="actions">{page.action()}</div></section>'
            + f'<section class="band wrap split"><h2>{data["notice"]}</h2>{p(data["rule"])}</section>')


PAGES["stoimost"] = prices


def team(page):
    team_data = DATA["team"]
    profiles = []
    for i, person in enumerate(team_data["people"],1):
        name = person["name"]
        if person["photo"]:
            image = page.photo(person["photo"],name,"portrait")
        else:
            image = f'<div class="missing missing-photo" role="img" aria-label="{LABEL["photo"]}: {esc(name)}">{MISS}</div>'
        bio = "".join(p(text) for text in person["bio"])
        profiles.append(f'<article class="band wrap split"><figure>{image}</figure><div>'
                        f'<span class="section-id" aria-hidden="true">{i:02d} / 05</span>'
                        f'<h2>{esc(name)}</h2><div class="copy">{bio}</div></div></article>')
    return page.intro(team_data["intro"]) + "".join(profiles)


PAGES["komanda"] = team


def faq(page):
    f = DATA["faq"]
    items = "".join(f'<details><summary>{esc(question)}</summary>{p(answer)}</details>'
                    for question,answer in f["items"])
    return page.intro(f["intro"]) + '<div class="band wrap split"><figure>' + page.photo(
        "detail-hands-straps", DATA["directions"]["items"][0]["title"]) + '</figure><div>' + items + '</div></div>'


PAGES["faq"] = faq


def certificates(page):
    c = DATA["certificates"]
    return (page.intro(c["intro"],"cadillac-pair-stretch")
            + f'<section class="band wrap split"><h2>{esc(c["how"])}</h2>{listing(c["steps"],True)}</section>'
            + f'<section class="band wrap split"><h2>{esc(c["denominationsTitle"])}</h2><div>'
              f'{listing(c["denominations"])}{p(c["end"])}'
              f'<div class="stack">{page.widget("personal",LABEL["buy"],"shop/all")}</div>'
              f'<div class="actions">{a(CONTACT["bot"], LABEL["footerBot"], "textlink go")}</div></div></section>')


PAGES["sertifikaty"] = certificates


def feedback():
    email = esc(CONTACT["email"])
    return (f'<form class="form-grid" data-feedback="{email}" data-subject="{LABEL["feedback"]}" '
            f'action="mailto:{email}" method="post" enctype="text/plain">'
            f'<label class="field">{LABEL["phone"]}<input type="tel" autocomplete="tel" '
            f'name="{LABEL["phone"]}" required></label>'
            f'<label class="field">{LABEL["message"]}<textarea rows="3" name="{LABEL["message"]}" required></textarea></label>'
            f'<button class="action" type="submit">{LABEL["submit"]}</button>{consent()}'
            f'<span>{CONTACT["emailLabel"]}: {a("mailto:"+CONTACT["email"], CONTACT["email"])}</span></form>')


def contacts(page):
    c = CONTACT
    social_rows = (f'<span>{c["botLabel"]} {a(c["bot"], c["bot"])}</span>'
                   f'<span>{c["whatsappLabel"]}: {a("https://wa.me/"+digits(c["messengerPhone"]),c["messengerPhone"])}</span>'
                   f'<span>{max_contact()}</span>'
                   f'<span>{LABEL["phone"]}: {a("tel:+"+digits(c["phone"]),c["phone"])}</span>'
                   f'<span>{c["emailLabel"]}: {a("mailto:"+c["email"],c["email"])}</span>')
    apps = "".join(f'<li>{a(url, label) if url else esc(label)+" "+MISS}</li>' for label,url in c["stores"].items())
    map_url = "https://yandex.ru/map-widget/v1/?" + urlencode(dict(ol="biz",oid=INTEGR["organization"],z="17"))
    return (f'<section class="intro"><div class="wrap"><span class="kicker">{DATA["brand"]}</span>'
            f'<h1>{page.title}</h1></div></section>'
            f'<section class="band wrap split"><div><h2>{c["addressLabel"]}</h2><div>{p(c["address"])}'
            f'{p(c["directions"])}{p(c["hours"])}</div><div class="actions">'
            f'{a(INTEGR["map"], LABEL["maps"],"textlink go")}</div></div>'
            f'<iframe class="frame map" src="{esc(map_url)}" title="{LABEL["maps"]}" loading="lazy"></iframe></section>'
            f'<section class="band wrap split"><div><h2>{c["booking"]}</h2><div class="actions">{page.action()}</div>'
            f'<div><span class="cap">{c["apps"]}</span><ul class="list">{apps}</ul></div></div>'
            f'<div class="contact-lines">{social_rows}<span>{LABEL["social"]}</span>{social()}'
            f'<span>{c["instagramLabel"]} {a(c["instagram"],c["instagram"])}</span>{p(c["instagramNote"])}</div></section>'
            f'<section id="feedback" class="band wrap split"><h2>{LABEL["formTitle"]}</h2>{feedback()}</section>')


def digits(phone):
    return "".join(char for char in phone if char.isdigit())


PAGES["kontakty"] = contacts


def styles(asset_base):
    fonts = (SRC / "fonts.css").read_text().replace("__ASSETS__", asset_base)
    return fonts + (SRC / "theme.css").read_text()


def generate():
    TILDA.mkdir(exist_ok=True)
    (TILDA / "common.html").write_text("<style>\n" + styles(ASSET_CDN) + "</style>\n")
    (SITE / "assets/homepilates.css").write_text(styles("."))
    (SITE / "assets/homepilates.js").write_text((SRC / "runtime.js").read_text())
    for slug in DATA["pages"]:
        page = Page(slug, False)
        meta = DATA["seo"][slug]
        title = esc(page.title + " — " + DATA["brand"])
        html = (f'<!doctype html>\n<html lang="ru"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{title}</title><meta name="description" content="{esc(meta)}">'
                f'<link rel="icon" href="{page.assets}/logo.svg"><link rel="stylesheet" href="{page.assets}/homepilates.css">'
                f'</head><body>{page.fragment()}</body></html>\n')
        directory = SITE / slug
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text(html)
        (TILDA / ((slug or "index") + ".html")).write_text(Page(slug, True).fragment())


if __name__ == "__main__":
    generate()
