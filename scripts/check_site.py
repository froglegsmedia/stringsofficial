#!/usr/bin/env python3
"""Check the static STRINGS site for required copy, broken local links, and forbidden status language."""

from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".html", ".css", ".js", ".md", ".svg", ".txt", ".xml"}
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr", "path",
}
REQUIRED = [
    "A music drama from Scary Romantic.",
    "Distribution and press",
    "contact@scaryromantic.com",
    "f74UleON9DM",
    "Tye is a passionate songwriter",
    "His latest feature is Strings.",
    "Kasey Yale",
    "Killamind",
    "Lead Cast",
    "Music drama · 90 min",
    "90 minutes",
    "PT90M",
    "Cinematographer",
    "© 2026 Scary Romantic",
    "https://www.stringsofficial.com/",
    "https://www.stringsofficial.com/filmmakers/",
    "https://www.stringsofficial.com/donate/",
    "Donate to the Project",
    "Help Us Finish Strings",
    "From the Heart Productions, Inc.",
    "95-4445418",
    "1013 Harbor Blvd #53",
    "Oxnard, CA 93035",
    "tyler@tylerforrest.com",
    "Donate with PayPal",
    'id="donate-qr" hidden',
    "https://www.stringsofficial.com/sitemap.xml",
    "https://instagram.com/stringsmovie",
    'property="og:image"',
    'name="twitter:card"',
]
FORBIDDEN = [
    "post-production",
    "post production",
    "raw cut",
    "raw director",
    "coming soon",
    "110 minutes",
    "pt110m",
    "as kel",
    "kasey yale ·",
    "kasey yale and william",
    "plays kel",
    "charactername",
    "985-705-1628",
    "9857051628",
    "tel:",
]
STATUS_WORDS = re.compile(r"\b(?:complete|completed|completion|finished|premiere|premiered)\b", re.I)


class Balancer(HTMLParser):
    def __init__(self, name):
        super().__init__(convert_charrefs=True)
        self.name = name
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"{self.name}: mismatched </{tag}> near {self.stack[-4:]}")
            return
        self.stack.pop()

    def close(self):
        super().close()
        if self.stack:
            self.errors.append(f"{self.name}: unclosed {self.stack}")


def local_target(html_path, url):
    url = url.split("#", 1)[0].strip()
    if not url or re.match(r"^(?:[a-z]+:)?//", url, re.I) or url.startswith(("mailto:", "tel:", "data:")):
        return None
    return (html_path.parent / url).resolve()


def main():
    errors = []
    cname_path = ROOT / "CNAME"
    cname = cname_path.read_text(encoding="utf-8").strip() if cname_path.is_file() else ""
    if cname != "www.stringsofficial.com":
        errors.append("CNAME must contain www.stringsofficial.com")

    pages = sorted(ROOT.glob("**/*.html"))
    if not pages:
        errors.append("no HTML pages found")
    combined_paths = pages + [ROOT / "robots.txt", ROOT / "sitemap.xml"]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in combined_paths if path.is_file())

    for phrase in REQUIRED:
        if phrase not in combined:
            errors.append(f"missing required text: {phrase}")

    content_files = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix in TEXT_SUFFIXES and "scripts" not in p.parts]
    blob = "\n".join(path.read_text(encoding="utf-8") for path in content_files).lower()
    for phrase in FORBIDDEN:
        if phrase in blob:
            errors.append(f"forbidden phrase present: {phrase}")

    for path in content_files:
        text = path.read_text(encoding="utf-8")
        match = STATUS_WORDS.search(text)
        if match:
            errors.append(f"{path.relative_to(ROOT)}: status word {match.group(0)!r}")
        if "froglegsmedia.github.io" in text:
            errors.append(f"{path.relative_to(ROOT)}: still points at github.io")

    phone = re.search(r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]\d{4}", blob)
    if phone:
        errors.append(f"phone number present: {phone.group(0)}")

    donate_js_path = ROOT / "js" / "donate.js"
    if not donate_js_path.is_file():
        errors.append("js/donate.js is missing")
    else:
        donate_js = donate_js_path.read_text(encoding="utf-8")
        if not re.search(r"(?m)^var DONATE_URL\s*=", donate_js):
            errors.append("js/donate.js: missing DONATE_URL")
        if not re.search(r"(?m)^var DONATE_QR_SRC\s*=", donate_js):
            errors.append("js/donate.js: missing DONATE_QR_SRC")
        if "—" in donate_js or "louisiana" in donate_js.lower():
            errors.append("js/donate.js: em dash or Louisiana")

    donate_page = ROOT / "donate" / "index.html"
    if donate_page.is_file():
        donate_html = donate_page.read_text(encoding="utf-8")
        if "—" in donate_html or "louisiana" in donate_html.lower():
            errors.append("donate/index.html: em dash or Louisiana")
    else:
        errors.append("donate/index.html is missing")

    for page in pages:
        html = page.read_text(encoding="utf-8")
        if "Donate to the Project" not in html:
            errors.append(f"{page.relative_to(ROOT)}: missing Donate to the Project link")
        balancer = Balancer(page.relative_to(ROOT).as_posix())
        balancer.feed(html)
        balancer.close()
        errors.extend(balancer.errors)
        for match in re.finditer(r"""(?:src|href)\s*=\s*["']([^"']+)["']""", html):
            target = local_target(page, match.group(1))
            if target is None:
                continue
            if target.is_file():
                continue
            if target.is_dir() and (target / "index.html").is_file():
                continue
            errors.append(f"{page.relative_to(ROOT)}: missing {match.group(1)}")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"ok: {len(pages)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
