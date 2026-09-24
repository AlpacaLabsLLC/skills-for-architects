"""Guard reusable slide output against baked-in vendor branding.

This checks authored assets, not a host's ability to resolve studio context or render.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SLIDES = ROOT / "skills/slide-deck-generator"


class SlideMarkup(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.depth = 0
        self.slides = []
        self.current = None
        self.mark_depth = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag != "div":
            return
        self.depth += 1
        classes = set(dict(attrs).get("class", "").split())
        if "slide" in classes:
            self.current = {"depth": self.depth, "classes": classes, "marks": []}
            self.slides.append(self.current)
        if "brand-mark" in classes and self.current:
            self.mark_depth = self.depth
            self.current["marks"].append("")

    def handle_data(self, data):
        if self.mark_depth is not None:
            self.current["marks"][-1] += data

    def handle_endtag(self, tag):
        if tag != "div":
            return
        if self.depth == self.mark_depth:
            self.mark_depth = None
        if self.current and self.depth == self.current["depth"]:
            self.current = None
        self.depth -= 1


class SlideBranding(unittest.TestCase):
    def test_no_vendor_brand_in_reusable_slide_sources(self):
        # Scope excludes repository legal attribution and real studio records.
        for path in SLIDES.iterdir():
            if path.suffix in {".md", ".html", ".svg"}:
                with self.subTest(path=path.name):
                    self.assertIsNone(re.search(r"\bALPA\b|Alpaca Labs|alpa\.llc", path.read_text()))

    def test_sample_marks_and_photography_omissions(self):
        slides = SlideMarkup((SLIDES / "sample.html").read_text()).slides
        self.assertGreaterEqual(len(slides), 22)
        self.assertTrue(any("image-title-slide" in s["classes"] for s in slides))
        for slide in slides:
            omitted = bool(slide["classes"] & {"image-slide", "image-grid"})
            self.assertEqual(slide["marks"], [] if omitted else ["Insert Studio Name"])

    def test_template_marks_are_substitution_slots(self):
        for filename in ["html-template.md", "slide-types.md"]:
            text = (SLIDES / filename).read_text()
            marks = re.findall(r'<div class="brand-mark">(.*?)</div>', text)
            self.assertTrue(marks, filename)
            self.assertEqual(set(marks), {"{{STUDIO_NAME}}"}, filename)

    def test_template_examples_do_not_create_live_slides(self):
        text = (SLIDES / "html-template.md").read_text()
        self.assertEqual(SlideMarkup(text).slides, [])
        inserted = '\n'.join(
            '<div class="slide"><div class="brand-mark">Test Studio</div></div>'
            for _ in range(3)
        )
        rendered = text.replace("<!-- SLIDES GO HERE -->", inserted, 1)
        self.assertEqual(len(SlideMarkup(rendered).slides), 3)

    def test_visible_brand_preserves_name_case(self):
        # Uppercasing would visibly change the exact fallback and supplied studio names.
        for filename in ["html-template.md", "sample.html"]:
            text = (SLIDES / filename).read_text()
            style = re.search(r"\.brand-mark\s*\{([^}]+)\}", text).group(1)
            transform = re.search(r"text-transform\s*:\s*([^;]+)", style)
            self.assertTrue(transform is None or transform.group(1).strip() == "none")


if __name__ == "__main__":
    unittest.main()
