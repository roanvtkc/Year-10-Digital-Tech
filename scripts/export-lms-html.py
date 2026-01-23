#!/usr/bin/env python3
from __future__ import annotations

import base64
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


def logo_data_uri() -> str:
    if not LOGO_SRC.exists():
        return ''
    svg_bytes = LOGO_SRC.read_bytes()
    svg_text = svg_bytes.decode('utf-8', errors='ignore')
    match = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', svg_text)
    if match:
        return f'data:image/png;base64,{match.group(1)}'
    encoded = base64.b64encode(svg_bytes).decode('ascii')
    return f'data:image/svg+xml;base64,{encoded}'


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

def apply_inline_styles(html_text: str) -> str:
    style_map = {
        'h2': 'color:#003865;margin-top:26px;',
        'h3': 'color:#002847;margin-top:20px;',
        'p': 'line-height:1.6;',
        'li': 'line-height:1.6;',
        'ul': 'padding-left:18px;margin-top:8px;',
        'ol': 'padding-left:18px;margin-top:8px;',
        'table': 'width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;',
        'th': 'border:1px solid #e5e7eb;padding:8px 10px;text-align:left;background:#f8fafc;',
        'td': 'border:1px solid #e5e7eb;padding:8px 10px;text-align:left;',
        'img': 'max-width:100%;height:auto;',
    }

    def repl(tag: str):
        pattern = re.compile(rf'<{tag}([^>]*)>', flags=re.I)
        def _replace(match: re.Match) -> str:
            attrs = match.group(1)
            if 'style=' in attrs:
                return match.group(0)
            return f'<{tag} style=\"{style_map[tag]}\"{attrs}>'
        return pattern.sub(_replace, html_text)

    for tag in style_map:
        html_text = repl(tag)

    return html_text


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

def remove_first_h1(html_fragment: str) -> str:
    return re.sub(r'<h1[^>]*>.*?</h1>', '', html_fragment, count=1, flags=re.S | re.I).strip()


def build_page(title: str, body_html: str, logo_uri: str) -> str:
    body_html = apply_inline_styles(body_html)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} | Year 10 Digital Technologies</title>
</head>
<body style="margin:0;font-family:Arial, sans-serif;color:#111827;background:#ffffff;">
  <div style="background:linear-gradient(135deg,#003865,#002847);color:#fff;padding:20px 28px;border-bottom:4px solid #C5B783;">
    <div style="display:flex;align-items:center;gap:14px;">
      <img src="{logo_uri}" alt="The King's College" style="width:52px;height:auto;" />
      <div>
        <div style="font-weight:700;font-size:20px;line-height:1.1;">Year 10 Digital Technologies</div>
        <div style="color:#C5B783;font-size:13px;">The King's College · 2026</div>
      </div>
    </div>
  </div>
  <div style="max-width:980px;margin:0 auto;padding:24px 28px 40px;">
    <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:20px 22px;box-shadow:0 8px 24px rgba(0,0,0,0.08);">
      <h1 style="margin-top:0;color:#003865;">{title}</h1>
      {body_html}
    </div>
  </div>
</body>
</html>
"""


def generate_from_markdown() -> None:
    logo_uri = logo_data_uri()
    for out_name, src in MARKDOWN_SOURCES.items():
        text = src.read_text(encoding='utf-8')
        text = strip_markdown_extras(text)
        html_fragment = md_to_html_fragment(text)
        html_fragment = remove_first_h1(html_fragment)
        # Extract title from first H1
        title_match = re.search(r'^#\s+(.+)$', text, flags=re.M)
        title = title_match.group(1).strip() if title_match else out_name.replace('.html', '').replace('-', ' ')
        page = build_page(title, html_fragment, logo_uri)
        (OUT_DIR / out_name).write_text(page, encoding='utf-8')


def generate_from_html() -> None:
    logo_uri = logo_data_uri()
    for out_name, src in HTML_SOURCES.items():
        html_text = src.read_text(encoding='utf-8')
        title, body = extract_title_and_body(html_text)
        if not title:
            title = out_name.replace('.html', '').replace('-', ' ')
        page = build_page(title, body, logo_uri)
        (OUT_DIR / out_name).write_text(page, encoding='utf-8')


def main() -> None:
    ensure_output()
    generate_from_markdown()
    generate_from_html()


if __name__ == '__main__':
    main()
