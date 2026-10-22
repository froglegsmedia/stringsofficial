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
    "Plays Kel",
    "© 2026 Scary Romantic",
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
    if (ROOT / "CNAME").exists():
        errors.append("CNAME must not be added; the domain is switched separately")

    pages = sorted(ROOT.glob("**/*.html"))
    if not pages:
        errors.append("no HTML pages found")
    combined = "\n".join(page.read_text(encoding="utf-8") for page in pages)

    for phrase in REQUIRED:
        if phrase not in combined:
            errors.append(f"missing required text: {phrase}")

    content_files = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix in TEXT_SUFFIXES and "scripts" not in p.parts]
    blob = "\n".join(path.read_text(encoding="utf-8") for path in content_files).lower()
    for phrase in FORBIDDEN:
        if phrase in blob:
            errors.append(f"forbidden phrase present: {phrase}")

    for path in content_files:
        match = STATUS_WORDS.search(path.read_text(encoding="utf-8"))
        if match:
            errors.append(f"{path.relative_to(ROOT)}: status word {match.group(0)!r}")

    phone = re.search(r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]\d{4}", blob)
    if phone:
        errors.append(f"phone number present: {phone.group(0)}")

    for page in pages:
        html = page.read_text(encoding="utf-8")
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
