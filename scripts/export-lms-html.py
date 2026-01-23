#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path('/Users/RoanV/Year-10-Digital-Tech')
OUT_DIR = Path('/Users/RoanV/Desktop/Year-10-Digital-Tech-LMS-HTML')
LOGO_SRC = ROOT / 'website' / 'public' / 'images' / 'tkc-crest.svg'

MARKDOWN_SOURCES = {
    'Year-10-Digital-Tech-Course-Outline.html': ROOT / 'docs' / 'course-outline.md',
    'Year-10-Digital-Tech-Assessment-Outline.html': ROOT / 'docs' / 'assessment-outline.md',
    'Year-10-Digital-Tech-Weekly-Planner.html': ROOT / 'planners' / 'weekly' / 'overview.md',
    'Assessment-A1-UX-UI-Brief-Student.html': ROOT / 'assessments' / 'minor' / 'a1-ux-ui-brief-student.md',
    'Assessment-A2-Data-Analysis-Student.html': ROOT / 'assessments' / 'minor' / 'a2-data-analysis-student.md',
    'Assessment-A3-Algorithms-Student.html': ROOT / 'assessments' / 'minor' / 'a3-algorithms-student.md',
    'Assessment-A4-Privacy-Security-Student.html': ROOT / 'assessments' / 'minor' / 'a4-privacy-security-student.md',
    'Assessment-M1-Major-Project-Student.html': ROOT / 'assessments' / 'major-project' / 'brief-student.md',
    'Rubric-A1-UX-UI.html': ROOT / 'assessments' / 'minor' / 'a1-ux-ui-rubric.md',
    'Rubric-A2-Data-Analysis.html': ROOT / 'assessments' / 'minor' / 'a2-data-analysis-rubric.md',
    'Rubric-A3-Algorithms.html': ROOT / 'assessments' / 'minor' / 'a3-algorithms-rubric.md',
    'Rubric-A4-Privacy-Security.html': ROOT / 'assessments' / 'minor' / 'a4-privacy-security-rubric.md',
    'Rubric-M1-Major-Project.html': ROOT / 'assessments' / 'major-project' / 'rubric.md',
    'Assessment-Calendar-2026.html': ROOT / 'content' / 'year-10-digital-tech' / 'assessment-calendar-2026.md',
    'Scope-and-Sequence-2026.html': ROOT / 'content' / 'year-10-digital-tech' / 'scope-sequence-2026.md',
}

HTML_SOURCES = {
    'Teacher-Pack-2026.html': ROOT / 'exports' / 'teacher-pack-2026.html',
    'Printables-2026.html': ROOT / 'exports' / 'printables-2026.html',
}


def ensure_output() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / 'assets').mkdir(parents=True, exist_ok=True)
    if LOGO_SRC.exists():
        (OUT_DIR / 'assets' / 'tkc-crest.svg').write_text(LOGO_SRC.read_text(encoding='utf-8'), encoding='utf-8')


def load_css() -> str:
    return """
:root {
  --tkc-blue: #003865;
  --tkc-blue-dark: #002847;
  --tkc-gold: #C5B783;
  --text: #111827;
  --muted: #6b7280;
  --border: #e5e7eb;
  --card: #f8fafc;
  --shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: 'Montserrat', ui-sans-serif, system-ui, sans-serif;
  color: var(--text);
  background: #fff;
}
.header {
  background: linear-gradient(135deg, var(--tkc-blue), var(--tkc-blue-dark));
  color: #fff;
  padding: 20px 28px;
  border-bottom: 4px solid var(--tkc-gold);
}
.header .brand {
  display: flex;
  align-items: center;
  gap: 14px;
}
.header img { width: 52px; }
.header .title { font-weight: 700; font-size: 20px; }
.header .subtitle { color: var(--tkc-gold); font-size: 13px; }
.container { max-width: 980px; margin: 0 auto; padding: 24px 28px 40px; }
.doc-card {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 22px;
  box-shadow: var(--shadow);
}
.doc-card h1 { margin-top: 0; color: var(--tkc-blue); }
.doc-card h2 { color: var(--tkc-blue); margin-top: 26px; }
.doc-card h3 { color: var(--tkc-blue-dark); margin-top: 20px; }
.doc-card p, .doc-card li { line-height: 1.6; }
.doc-card table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }
.doc-card th, .doc-card td { border: 1px solid var(--border); padding: 8px 10px; text-align: left; }
.doc-card th { background: var(--card); }
.doc-card ul { padding-left: 18px; }
.footer { color: var(--muted); font-size: 12px; margin-top: 16px; }
""".strip() + "\n"


def write_css() -> None:
    (OUT_DIR / 'assets' / 'style.css').write_text(load_css(), encoding='utf-8')


def strip_markdown_extras(text: str) -> str:
    # Remove print buttons and last updated blocks if present
    cleaned = []
    skip = False
    for line in text.splitlines():
        if 'print-actions' in line:
            skip = True
            continue
        if skip:
            if '</div>' in line:
                skip = False
            continue
        if 'last-updated' in line:
            continue
        cleaned.append(line)
    return '\n'.join(cleaned).strip() + '\n'


def md_to_html_fragment(md_text: str) -> str:
    result = subprocess.run(
        ['pandoc', '-f', 'markdown', '-t', 'html'],
        input=md_text,
        text=True,
        check=True,
        capture_output=True,
    )
    return result.stdout


def extract_body(html_text: str) -> str:
    match = re.search(r'<body[^>]*>(.*)</body>', html_text, flags=re.S | re.I)
    return match.group(1).strip() if match else html_text


def remove_qr_blocks(html_text: str) -> str:
    return re.sub(r'<div class="qr-block">.*?</div>', '', html_text, flags=re.S)


def extract_title_and_body(html_text: str) -> tuple[str, str]:
    body = extract_body(html_text)
    body = remove_qr_blocks(body)
    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', body, flags=re.S | re.I)
    title = ''
    if title_match:
        title = re.sub('<[^<]+?>', '', title_match.group(1)).strip()
        body = body[:title_match.start()] + body[title_match.end():]
    return title, body.strip()


def build_page(title: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} | Year 10 Digital Technologies</title>
  <link rel="stylesheet" href="assets/style.css" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet" />
</head>
<body>
  <header class="header">
    <div class="brand">
      <img src="assets/tkc-crest.svg" alt="The King's College" />
      <div>
        <div class="title">Year 10 Digital Technologies</div>
        <div class="subtitle">The King's College · 2026</div>
      </div>
    </div>
  </header>
  <main class="container">
    <div class="doc-card">
      <h1>{title}</h1>
      {body_html}
    </div>
    <div class="footer">Generated for LMS upload.</div>
  </main>
</body>
</html>
"""


def generate_from_markdown() -> None:
    for out_name, src in MARKDOWN_SOURCES.items():
        text = src.read_text(encoding='utf-8')
        text = strip_markdown_extras(text)
        html_fragment = md_to_html_fragment(text)
        # Extract title from first H1
        title_match = re.search(r'^#\s+(.+)$', text, flags=re.M)
        title = title_match.group(1).strip() if title_match else out_name.replace('.html', '').replace('-', ' ')
        page = build_page(title, html_fragment)
        (OUT_DIR / out_name).write_text(page, encoding='utf-8')


def generate_from_html() -> None:
    for out_name, src in HTML_SOURCES.items():
        html_text = src.read_text(encoding='utf-8')
        title, body = extract_title_and_body(html_text)
        if not title:
            title = out_name.replace('.html', '').replace('-', ' ')
        page = build_page(title, body)
        (OUT_DIR / out_name).write_text(page, encoding='utf-8')


def main() -> None:
    ensure_output()
    write_css()
    generate_from_markdown()
    generate_from_html()


if __name__ == '__main__':
    main()
