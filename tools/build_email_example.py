"""Build the Nov 19 community newsletter: HTML, plain text and link list.

Starts from last week's HTML (the Mailchimp template) and regenerates the event
sections, Ongoing list, title, preview text, header and intro.
"""
import json, re, html as H
from bs4 import BeautifulSoup

ISSUE = "2026-11-19"
ISSUE_LONG = "Thursday, November 19, 2026"
ISSUE_SHORT = "November 19, 2026"
THIS_WEEK_END = (11, 25)  # This Week runs through Wednesday, Nov 25
ASSETS = f"https://visithighlandsnc.github.io/newsletter-assets/{ISSUE}"
SV = "https://assets.simpleviewinc.com/simpleview/image/upload/c_limit,h_1200,q_75,w_1200/v1/crm/highlandsnc/"
CHAMBER = "https://www.highlandschamber.org"

PREVIEW = ("Mark O’Connor’s Appalachian Christmas, an oyster roast with bluegrass, "
           "ice skating and more happening in Highlands this week.")
INTRO = ("*|IF:FNAME|*Hi *|FNAME|*,*|ELSE:|*Hi there,*|END:IF|* if you’re looking for something to do this "
         "week, you’ve got plenty of options in Highlands. You can lace up your skates at Kelsey-Hutchinson Founders Park starting today, "
         "and on Friday morning families can learn how birds of prey hunt in winter with the "
         "Highlands Biological Foundation. Saturday is a full one: oysters and live bluegrass at Highlander "
         "Mountain House in the afternoon, then Mark O’Connor’s Appalachian Christmas at the "
         "Highlands Performing Arts Center that night. Take a look at everything happening&nbsp;this&nbsp;"
         "week&nbsp;below.")

# Chamber event photos (og:image file names) and sizes, by Simpleview event ID
PHOTOS = {
 "2360": ("CBH-Web-691x675_3E7952A9-9D05-C277-A8F133E4D7156160_3e7d4fbd-c626-383f-0c5d82c1aeb95fad.png", 691, 675),
 "2423": ("Point-Of-Grace-Web-2-691x675_0EF9AEDF-BEF8-6A7E-C74024C13FAF9416_0eff855b-0ab9-cc85-c8a510cf55c0d298.png", 691, 675),
 "2477": ("MM-Xmas-1_AF1AB9CC-DFE5-96B8-B34F5F48FEBB1CF2_af1f0a61-de96-2adf-971f573e4d54ed4d.jpg", 1200, 675),
 "2888": ("santa_E9F4E72B-5056-BFCE-A864ACD4D9621DBA_e9f67c89-5056-bfce-a81744ab200c1e36.jpg", 418, 282),
 "2894": ("holiday-fest-26_3B601A05-B523-40D3-CD1404B8917EDCD0_3b7ac1ca-dd71-d7bc-362c4340affd440d.jpg", 923, 1200),
 "2906": ("_74A9632-2-_B555ADD2-B7A8-5DAF-0C74481912EB2FD1_b55bab50-d101-e3eb-b3cf1daffa5c1633.jpg", 1200, 802),
 "2923": ("Copy-of-Community-Newsletter-Template-14-_62FC3153-B837-7E3E-4DE11D1E8D9B4C9E_62fcc99d-ca8e-a2c6-f3b1777c2bb1ae56.png", 1105, 580),
 "2932": ("highlands-nc-highlander-mountain-house-oyster-roast_85D0F294-B7D4-9866-2F6C936B91F974A7_85e4767f-0a55-0bc4-c956ae9d4813e252.jpg", 1080, 606),
 "2947": ("star_E9D11D35-5056-BFCE-A865F577587866DD_e9d17230-5056-bfce-a88051aafa1475d6.jpg", 800, 1200),
 "2969": ("Interstellar-Echoes_243B07A7-A87C-3109-982DB07381588CFA_243f99f2-b002-a55f-d073233772d0e4b4.jpg", 420, 315),
 "2970": ("Rumours-Fleetwood-Mac_244C2395-FBCD-A275-9BB54690FAE5CC97_24557456-bed8-700c-52458cdf1817f81f.jpg", 420, 315),
 "2971": ("Celtic-Angels_246881EB-C99C-CD18-63537E8812A76DBC_246ccd5c-90f1-64df-3bc4013d31d0d99e.jpg", 420, 315),
 "2972": ("Sean-Dietrich_254A1E16-B3D4-EB83-1CC35EF8C3CF26B5_254e1898-fe33-86d9-87a2de18c597b712.jpg", 420, 315),
 "2973": ("Kiss_255DCB56-AE3B-07B6-FB375F4C633E87AF_25623ff6-a265-4aab-7385ca098d37ee70.jpg", 420, 315),
 "2975": ("Samantha-Fish_Paul-Hunt-Photography-27-1-_52593D2B-CEDB-653C-F20E640DDEA23AA7_525ced8c-b403-cc89-d9ba947a8f0d0f43.jpg", 420, 315),
 "2982": ("rapid-raptors-nov20_5C29B472-F99D-2BDC-B08C965425690F32_5c355b69-978c-faad-a7418ae02cfc233c.jpg", 1150, 760),
 "2983": ("homestead-skills-nov21_5C442689-B59A-B23C-B1EC088B96C21733_5c489ff1-d7b6-7a87-afbb2fe48083a938.jpg", 1150, 760),
 "2988": ("Holiday-Market-Insta-Graphic17_8CD1F0E9-B410-01AF-A4438F308E564420_8cd7536f-06e9-6f64-942f1ca88617707c.png", 960, 1200),
 "2989": ("Holiday-Market-Insta-Graphic10_8CEAFAD8-FFD4-0587-A48E53DB2283655D_8cec9dc8-ab0d-965a-363889f1f0686d5b.png", 960, 1200),
 "2991": ("Holiday-Market-Insta-Graphic17_8D120A21-E4C4-1435-9135208EBB37164D_8d1a46ee-0203-c24e-23f7952c55fa3959.png", 960, 1200),
 "2995": ("Holiday-Market-Insta-Graphic11_8E03EA7A-0DBF-D3ED-C99D34F63A3673A1_8e09955c-ac96-b8a2-abe9e6534d145f69.png", 960, 1200),
 "2999": ("Book-Lover-s-Tea_55801B28-964D-086B-91F1A6FB683D38D3_558d1beb-c22c-8478-1c91aad61c3aba6b.jpg", 1200, 847),
 "3001": ("Lighting-of-the-Menorahs---Sign_62DE2BFD-9B1D-AB76-329DD3D8C706B542_62e06986-9ae9-b576-1d88d7bbfee5187a.png", 1200, 900),
 "3006": ("inbound6219370846410737985_576A1959-D560-E7DE-7456AA34C27A55C5_57743244-93f5-13aa-b35e9f273d5d696d.png", 1200, 1200),
 "3007": ("inbound8447587761639258965_5783B073-9A67-CE96-085E5BFA04CC6D9F_57903283-f8a5-baae-02d4113ef510c224.png", 1000, 1200),
 "3010": ("Edwin-McCain_F72A3A9B-EB7F-9F0F-50AAB49E0331E795_f72f2a49-f571-8233-88866741fe6bddb2.jpg", 420, 315),
 "3020": ("IMG_0769_586B4F45-3094-4307-95B273C3FFB1D856_660e225d-e506-4c6b-92fc61e06455e013.png", 1200, 1200),
 "3028": ("IMG_0770_54E317E8-5C2E-4789-AD9A19BDDBBAF43E_13b23ee4-2436-489f-af80e2bc4228f57c.png", 960, 1200),
 "3046": ("IMG_0135_E0D78ED6-C6C2-41D1-B44430B53F7076F8_b0efd96b-7ca5-4cb8-b2d0d2ec57b23a19.jpg", 978, 991),
 "3047": ("IMG_0135_AF57FFBE-DFD7-46E0-82AFBAF62E48CE4B_eb0df4d0-eae9-4249-a098a05f7b2e12b0.jpg", 978, 991),
 "3049": ("IMG_0772_7CB12D39-C179-45AA-AD10EBD405D79AC3_75e8e550-88fe-431a-9a7d64ed9502100e.png", 1097, 1200),
 "3053": ("milli_botique_ribbon_cutting_25D2CD56-0D3D-E750-1EFF7EE7B1EAAA3C_25d341d2-bdb7-f871-f788b66e7add8798.png", 939, 628),
 "3054": ("winter-wildlife-dec4_F4940AB2-DEB6-667E-01F9B554120F872D_f4a7bebb-0ee0-c630-656d4425e685f51e.jpg", 1150, 760),
 "3055": ("ranger-falls-dec11_F4B7E57C-AE30-4B56-5EF55F35DCEB1F91_f4c32191-0d2d-3eea-cf691c78b733e6d5.jpg", 1150, 760),
 "3056": ("holiday-gathering-dec12_F4D01BC6-A295-C3D8-5E2D3E53D9683AE8_f4db11f8-e3ea-c903-a8d494c762741fc1.jpg", 1150, 760),
}
# Tall photos cropped to 4:5 (max 360x450 in the email) by tools/split_export.py crop mode
CROPPED = {"hunger": (870, 1088), "2947": (800, 1000), "2894": (923, 1154),
           "merritt": (1152, 1440), "santa": (1080, 1350)}
BIRD_PHOTO = ("https://highlandsbiological.org/wp-content/uploads/2026/11/HBS_ChristmasBirdCount_FBEvent_1920x1005-1024x536.png", 1024, 536)

# Chamber event pages for events with no External Link in the report
CHAMBER_PAGES = {
 "3028": "/event/jingle-brew-decking-halls-and-filling-glasses/3028/",
 "3049": "/event/hearth-%26-hops-holiday-market/3049/",
 "2923": "/event/small-business-saturday-holiday-stroll/2923/",
 "2888": "/event/highlands-christmas-parade/2888/",
 "3020": "/event/highlands-holiday-crawl/3020/",
 "3046": "/event/christmas-music-bingo/3046/",
 "3047": "/event/sleigh-the-mic%3a-christmas-karaoke-%26-caroling/3047/",
}

MONTHS = {m: i for i, m in enumerate(
    "JANUARY FEBRUARY MARCH APRIL MAY JUNE JULY AUGUST SEPTEMBER OCTOBER NOVEMBER DECEMBER".split(), 1)}


def link_for(c):
    u = (c.get("ext") or "").strip()
    if not u:
        return CHAMBER + CHAMBER_PAGES[c["id"]]
    if not u.startswith("http"):
        u = "https://" + u
    # drop social tracking parameters (fbclid, utm_*)
    base, _, q = u.partition("?")
    keep = [kv for kv in q.split("&") if kv and not kv.startswith(("fbclid=", "utm_"))]
    return base + ("?" + "&".join(keep) if keep else "")


def nice_date(s):
    day, _, time = s.partition(" | ")
    words = [w.capitalize() if w.rstrip(",").isalpha() else w.lower() for w in day.split()]
    day = " ".join(words).replace(" Starting", " starting")
    return f"{day} | {time.lower()}" if time else day


FIX = {"Hbf": "HBF", "N. E.": "N. E.", "Sc": "SC", "Nc": "NC", "Rd": "Rd", "St": "St", "And": "and"}


def nice_place(s):
    t = s.title()
    t = re.sub(r"\bHbf\b", "HBF", t)
    t = re.sub(r"\bSc\b", "SC", t)
    t = t.replace(" And ", " and ").replace(" Of ", " of ").replace(" The ", " the ")
    return t


def month_day(s):
    m = re.search(r"(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER) (\d+)", s)
    return (MONTHS[m.group(1)], int(m.group(2)))


def esc(t):
    return H.escape(t, quote=False).replace("'", "’")


def keep(t):
    """Escape text and tie its last words together with non-breaking spaces so a
    line never ends with a single word on its own. A "|" separator is not counted
    as a word, so a time stays with the word before it."""
    toks = esc(t).split(" ")
    real = [i for i, w in enumerate(toks) if w not in ("|", "&amp;")]
    if len(real) < 3:
        return "&nbsp;".join(toks)
    n = 3 if len(toks[real[-1]]) + len(toks[real[-2]]) < 12 and len(real) > 3 else 2
    cut = real[-n]
    return (" ".join(toks[:cut]) + ' <span style="white-space:nowrap;">'
            + "&nbsp;".join(toks[cut:]) + "</span>")


DIVIDER = ('<tr>\n<!-- DIVIDER: Horizontal line and spacing between content blocks -->\n'
           '<td style="padding:18px 0;">\n<table align="center" cellpadding="0" cellspacing="0" width="76%">'
           '<tr><td style="border-top:1px solid #9fae9c;font-size:0;line-height:0;height:1px;"></td></tr></table>\n'
           '</td>\n</tr>\n')


def card_html(n, c):
    url = H.escape(link_for(c))
    if c.get("photo"):
        src, w, h = c["photo"]
    elif c["id"]:
        f, w, h = PHOTOS[c["id"]]
        src = SV + f
    else:
        src, w, h = BIRD_PHOTO
    # Photos taller than 4:5 use a cropped copy hosted with the issue assets
    if c["key"] in CROPPED:
        src, (w, h) = f"{ASSETS}/photo-{c['key']}.jpg", CROPPED[c["key"]]
    disp = 400 if w / h >= 1.25 else 360
    disp_h = round(disp * h / w)
    title = c["title_pretty"]
    title_alt = H.escape(title, quote=True)
    date = nice_date(c["date"])
    place = nice_place(c["loc"])
    return f'''<!-- START EVENT {n}: {title} / {date} -->
<tr>
<td align="center" class="px" style="padding:0 64px;text-align:center;">
<!-- EDIT: Organizer / presenter name -->
<p style="font:12px/18px Arial,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#826638;margin:0 0 14px;">{keep(c["host"])}</p>
<!-- EDIT: Image click destination in href. Match the button destination below. -->
<a href="{url}" style="display:block;">
<!-- EDIT: MAIN EVENT IMAGE OR FLYER: edit src URL and alt description. Width is 400 for landscape images, 360 for square or portrait. -->
<img alt="{title_alt}" height="{disp_h}" src="{src}" style="display:block;margin:0 auto;width:100%;max-width:{disp}px;height:auto;border:0;" width="{disp}">
</a>
</td>
</tr>
<tr>
<td align="center" style="padding:0;text-align:center;">
<!-- EDIT: EVENT TITLE GRAPHIC: edit src and alt. Made in Canva, hosted at visithighlandsnc.github.io/newsletter-assets -->
<img alt="{title_alt}" height="42" src="{ASSETS}/{c.get('title_img', f'title-{n:02d}.png')}" style="display:block;margin:16px auto 0;width:100%;max-width:600px;height:auto;border:0;font-family:Georgia,serif;font-size:22px;font-style:italic;color:#826638;" width="600">
</td>
</tr>
<tr>
<td align="center" class="px" style="padding:0 64px;text-align:center;">
<!-- EDIT: Date and time -->
<p style="font:bold 13px/20px Arial,sans-serif;letter-spacing:1.5px;text-transform:uppercase;color:#826638;margin:0 0 2px;">{keep(date)}</p>
<!-- EDIT: Venue and address -->
<p style="font:11px/17px Arial,sans-serif;letter-spacing:1px;text-transform:uppercase;color:#826638;margin:0 0 14px;">{keep(place)}</p>
<!-- EDIT: Event description. Georgia 16px with 25px line spacing. -->
<p style="font:16px/25px Georgia,serif;color:#2e5940;margin:0 0 18px;">{keep(c["desc"])}</p>
<table align="center" cellpadding="0" cellspacing="0" style="margin:0 auto;">
<tr>
<td style="border:1px solid #2e5940;">
<!-- EDIT: Button destination in href; button label is the text before </a>. -->
<a href="{url}" style="text-decoration:none;display:block;padding:8px 20px;font:12px/18px Arial,sans-serif;letter-spacing:1.5px;text-transform:uppercase;color:#2e5940;">{esc(c["btn"])}</a>
</td>
</tr>
</table>
</td>
</tr>
<!-- END EVENT {n}: {title} / {date} -->
'''


ICE = '''<!-- START RECURRING LISTING: Kelsey-Hutchinson Founders Park -->
<tr>
<td style="padding:16px 0;text-align:center;">
<!-- EDIT: Organizer name -->
<p style="margin:0 0 8px;font-family:Arial,sans-serif;font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#826638;line-height:16px;">Kelsey-Hutchinson Founders&nbsp;Park</p>
<p style="margin:0 0 6px;font-family:Georgia,serif;font-size:16px;color:#2e5940;line-height:25px;">
<!-- EDIT: Activity name; schedule and any notes follow the closing strong tag. -->
<strong style="font-family:Arial,sans-serif;font-size:16px;font-weight:bold;">Ice&nbsp;Skating</strong>
<br>Thursdays |&nbsp;3:30-8pm
<br>Fridays |&nbsp;3:30-10pm
<br>Saturdays |&nbsp;1-10pm
<br>Sundays |&nbsp;1-5pm
</p>
<!-- EDIT: More info destination in href -->
<a href="https://www.highlandsnc.org/highlands-parks-and-recreation-department/page/ice-rink" style="font-family:Arial,sans-serif;font-size:12px;color:#2e5940;text-decoration:underline;">More info</a>
</td>
</tr>
<!-- END RECURRING LISTING: Kelsey-Hutchinson Founders Park -->


'''


ONG_ACT = '''<p style="margin:0 0 6px;font-family:Georgia,serif;font-size:16px;color:#2e5940;line-height:25px;">
<!-- EDIT: Activity name; schedule and any notes follow the closing strong tag. -->
<strong style="font-family:Arial,sans-serif;font-size:16px;font-weight:bold;">{name}</strong>
<br>{sched}
</p>
'''


TIME_RANGE = re.compile(r"(\d(?::\d\d)?(?:am|pm)?)\s*[–—-]\s*(\d)", re.I)
TIME_SPACE = re.compile(r"(\d(?::\d\d)?)\s+(am|pm)\b", re.I)


def tidy_times(t):
    """Times read 4-5pm, 10am-2pm: hyphen, no spaces, lowercase am/pm."""
    t = TIME_SPACE.sub(lambda m: m.group(1) + m.group(2).lower(), t)
    return TIME_RANGE.sub(r"\1-\2", t)


def main():
    cards = json.load(open("/home/claude/scripts/issue_cards_v2.json"))
    h = open("/home/claude/ref/lastweek.html", encoding="utf-8").read()

    # --- pieces of last week's template
    i_first = h.find("<!-- START EVENT 15")
    pre = h[:i_first]
    up_head = h[h.find("<!-- SECTION: UPCOMING EVENTS"):h.find("<!-- START EVENT 24")]
    on_head = h[h.find("<!-- SECTION: ONGOING EVENTS"):h.find("<!-- START RECURRING LISTING: Unfurl")]
    end_tag = "<!-- END RECURRING LISTING: Rotary Club of Highlands -->"
    listings = h[h.find("<!-- START RECURRING LISTING: Unfurl"):h.find(end_tag) + len(end_tag)]
    tail = h[h.find(end_tag) + len(end_tag):]

    # --- header, title, preview, intro
    pre = re.sub(r"<title>.*?</title>", f"<title>Community News | {ISSUE_SHORT} | Visit Highlands</title>", pre)
    pre = re.sub(r'(mso-hide:all;[^>]*>)[^<]*(</div>)', lambda m: m.group(1) + H.escape(PREVIEW, quote=False) + m.group(2), pre, count=1)
    pre = re.sub(r'alt="Highlands Chamber of Commerce Community News, [^"]*"',
                 f'alt="Highlands Chamber of Commerce Community News, {ISSUE_LONG}"', pre)
    pre = re.sub(r'(<img alt="Highlands Chamber of Commerce Community News[^>]*?)height="\d+" src="[^"]*"',
                 lambda m: m.group(1) + f'height="394" src="{ASSETS}/header-v2.png"', pre)
    pre = re.sub(r'(line-height:29px;">)\*\|IF:FNAME\|\*.*?(</p>)', lambda m: m.group(1) + INTRO + m.group(2), pre, flags=re.S)

    # --- Ongoing: add ice skating, drop past Mountain Findings dates
    listings = ICE + listings
    listings = re.sub(r"(\S+) \|&nbsp;([^<\n]+)",
                      r'<span style="white-space:nowrap;">\1&nbsp;|&nbsp;\2</span>', listings)
    tail = tail.replace("All rights reserved.", "All&nbsp;rights&nbsp;reserved.")
    tail = re.sub(r"\s+or\s+(<a [^>]*>unsubscribe</a>)", r"&nbsp;or&nbsp;\1", tail)
    listings = listings.replace("<br>November 14 &amp; 15 |&nbsp;10am-1pm\n", "")
    # --- Ongoing additions from member sites and the Laurel calendar (Nov 18 review)
    def _act(name, sched):
        return ONG_ACT.format(name=name, sched=sched)
    def _listing(org, acts, url):
        return (f'<!-- START RECURRING LISTING: {org} -->\n<tr>\n<td style="padding:16px 0;text-align:center;">\n'
                f'<!-- EDIT: Organizer name -->\n<p style="margin:0 0 8px;font-family:Arial,sans-serif;font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#826638;line-height:16px;">{org.replace(" ", "&nbsp;", 1) if org.count(" ")==1 else org.rsplit(" ",1)[0]+"&nbsp;"+org.rsplit(" ",1)[1]}</p>\n'
                + "".join(acts) +
                f'<!-- EDIT: More info destination in href -->\n<a href="{url}" style="font-family:Arial,sans-serif;font-size:12px;color:#2e5940;text-decoration:underline;">More info</a>\n</td>\n</tr>\n<!-- END RECURRING LISTING: {org} -->\n')
    def _add_acts(listings, org, acts):
        end = f"<!-- EDIT: More info destination in href -->"
        i = listings.find(f"<!-- START RECURRING LISTING: {org} -->")
        j = listings.find(end, i)
        return listings[:j] + "".join(acts) + listings[j:]
    listings = _add_acts(listings, "The Bascom", [
        _act("Holiday&nbsp;Market", "Mondays through Saturdays |&nbsp;10am-5pm"),
        _act("Fiber&nbsp;Club", "Saturdays |&nbsp;10am-12pm")])
    listings = _add_acts(listings, "Hudson Library", [
        _act("Family&nbsp;Storytime", "Thursdays |&nbsp;10:40-11am")])
    listings = _add_acts(listings, "Trailborn Highlands", [
        _act("Supper Club&nbsp;Sundays", "Sundays |&nbsp;4-6pm<br>Live music with David&nbsp;Crisp")])
    k = listings.find("<!-- START RECURRING LISTING: Skyline Lodge -->")
    listings = listings[:k] + _listing("4118 Kitchen &amp; Bar", [_act("Live Music&nbsp;Thursdays", "Thursdays |&nbsp;6:30-8:30pm")], "https://4118kitchenbar.toast.site/") + listings[k:]
    k = listings.find("<!-- START RECURRING LISTING: Western Carolina Brew and Wine -->")
    listings = listings[:k] + _listing("Spruce Interiors", [_act("Tuesday Tiles on the&nbsp;Terrace", "Tuesdays |&nbsp;5pm<br>Open tile games with refreshments; sign-up&nbsp;required.")], "https://tickets.signupgenius.com/#/wizard/org/org_2yf/events/evt_1sb") + listings[k:]
    listings = re.sub(r"(\S+) \|&nbsp;([^<\n]+)",
                      r'<span style="white-space:nowrap;">\1&nbsp;|&nbsp;\2</span>', listings)

    # --- event sections
    tw = [c for c in cards if month_day(c["date"]) <= THIS_WEEK_END]
    up = [c for c in cards if month_day(c["date"]) > THIS_WEEK_END]
    body = pre
    n = 0
    for c in tw:
        n += 1
        body += card_html(n, c) + "\n" + DIVIDER + "\n"
    body += up_head
    for c in up:
        n += 1
        body += card_html(n, c) + "\n" + DIVIDER + "\n"
    body += on_head + listings + tail
    open(f"/home/claude/out/newsletter-{ISSUE}.html", "w", encoding="utf-8").write(tidy_times(body).replace("header-v2.png\" style=\"display:block;width:100%;max-width:600px;height:auto;border:0;background:#a89b2a", "header-v2.png\" style=\"display:block;width:100%;max-width:600px;height:auto;border:0;background:#2e5940"))

    # --- plain text
    soup = BeautifulSoup(listings, "html.parser")
    ongoing_txt = []
    for td in soup.find_all("td"):
        ps = td.find_all("p")
        if not ps:
            continue
        org = ps[0].get_text().replace("\xa0", " ").strip()
        ongoing_txt.append(org.upper())
        for p in ps[1:]:
            lines = [l.strip().replace("\xa0", " ") for l in p.get_text("\n").split("\n") if l.strip()]
            ongoing_txt.append(lines[0])
            for l in lines[1:]:
                ongoing_txt.append("  " + l)
        a = td.find("a")
        if a:
            ongoing_txt.append("More info: " + a["href"])
        ongoing_txt.append("")

    def card_txt(c):
        return "\n".join([
            c["title_pretty"].upper(),
            c["host"],
            nice_date(c["date"]),
            nice_place(c["loc"]),
            "",
            c["desc"].replace("'", "’"),
            f'{c["btn"]}: {link_for(c)}',
            "", ""])

    rule = "=" * 40
    txt = [f"COMMUNITY NEWS | {ISSUE_LONG.upper()}", "Highlands Chamber of Commerce", "",
           "View this email in your browser: *|ARCHIVE|*", "",
           H.unescape(INTRO), "", "",
           rule, "THIS WEEK IN HIGHLANDS", rule, ""]
    txt += [card_txt(c) for c in tw]
    txt += [rule, "UPCOMING EVENTS", rule, ""]
    txt += [card_txt(c) for c in up]
    txt += [rule, "ONGOING EVENTS", rule, ""] + ongoing_txt + ["", rule, ""]
    txt += ["JUST LANDED: New Highlands merch, available online and in store.",
            "Shop now: https://highlands-chamber-of-commerce.square.site/", "",
            "ASK MAYOR PAT",
            "Send your question: https://askmayorpat.com/contact-pat", "", rule, "",
            "Copyright © *|CURRENT_YEAR|* *|LIST:COMPANY|*. All rights reserved.",
            "*|IFNOT:ARCHIVE_PAGE|**|LIST:DESCRIPTION|**|END:IF|*", "",
            "Our mailing address is:", "*|IFNOT:ARCHIVE_PAGE|**|LIST_ADDRESS|**|END:IF|*", "",
            "Want to change how you receive these emails?",
            "Update your preferences: *|UPDATE_PROFILE|*",
            "Unsubscribe: *|UNSUB|*", ""]
    open(f"/home/claude/out/newsletter-{ISSUE}-plain-text.txt", "w", encoding="utf-8").write(tidy_times("\n".join(txt)))

    # --- link list for the Canva-image route
    ll = [f"Community News, {ISSUE_LONG}: links in newsletter order", "",
          "Header image: https://www.highlandschamber.org", "", "THIS WEEK IN HIGHLANDS"]
    n = 0
    for sec, lst in (("THIS WEEK IN HIGHLANDS", tw), ("UPCOMING EVENTS", up)):
        if sec == "UPCOMING EVENTS":
            ll += ["", "UPCOMING EVENTS"]
        for c in lst:
            n += 1
            ll.append(f"{n}. {c['title_pretty']} ({nice_date(c['date'])})")
            ll.append(f"   {link_for(c)}")
    ll += ["", "PROMOS",
           "Merch: https://highlands-chamber-of-commerce.square.site/",
           "Ask Mayor Pat: https://askmayorpat.com/contact-pat", ""]
    open(f"/home/claude/out/newsletter-{ISSUE}-link-list.txt", "w", encoding="utf-8").write("\n".join(ll))
    print("this week", len(tw), "upcoming", len(up))


if __name__ == "__main__":
    main()
