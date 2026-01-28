#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import base64
from pathlib import Path

ROOT = Path('/Users/RoanV/Year-10-Digital-Tech')
CONTENT_DIR = ROOT / 'content' / 'year-10-digital-tech'
EXPORTS_DIR = ROOT / 'exports'
PUBLIC_EXPORTS = ROOT / 'website' / 'public' / 'exports'
CONFIG_PATH = EXPORTS_DIR / 'printables-config.json'
LOGO_SRC = ROOT / 'website' / 'public' / 'images' / 'tkc-crest.svg'

FILES = {
    'assessment-calendar-2026.md': 'assessment-calendar-2026',
    'scope-sequence-2026.md': 'scope-sequence-2026',
}

RUBRICS = [
    ('Major Project Rubric', ROOT / 'assessments' / 'major-project' / 'rubric.md'),
    ('Minor A1 Rubric', ROOT / 'assessments' / 'minor' / 'a1-ux-ui-rubric.md'),
    ('Minor A2 Rubric', ROOT / 'assessments' / 'minor' / 'a2-data-analysis-rubric.md'),
    ('Minor A3 Rubric', ROOT / 'assessments' / 'minor' / 'a3-algorithms-rubric.md'),
    ('Minor A4 Rubric', ROOT / 'assessments' / 'minor' / 'a4-privacy-security-rubric.md'),
]


def load_base_url() -> str:
    if CONFIG_PATH.exists():
        data = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
        return data.get('baseUrl', '').rstrip('/')
    return ''


def git_last_updated(path: Path) -> str:
    try:
        result = subprocess.check_output(
            ['git', '-C', str(ROOT), 'log', '-1', '--format=%cs', str(path)],
            text=True
        ).strip()
        return result or 'Unknown'
    except Exception:
        return 'Unknown'


def strip_print_elements(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if 'print-actions' in line or 'last-updated' in line:
            continue
        if '{{LAST_UPDATED}}' in line:
            line = line.replace('{{LAST_UPDATED}}', '')
        lines.append(line)
    return '\n'.join(lines).strip() + '\n'

def strip_top_heading(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith('# '):
        return '\n'.join(lines[1:]).strip() + '\n'
    return text

def demote_headings(text: str, levels: int = 2) -> str:
    output = []
    for line in text.splitlines():
        if line.startswith('#'):
            hashes = len(line) - len(line.lstrip('#'))
            new_hashes = min(6, hashes + levels)
            output.append('#' * new_hashes + line[hashes:])
        else:
            output.append(line)
    return '\n'.join(output).strip() + '\n'


def run_pandoc(markdown_text: str, out_path: Path, css_name: str) -> None:
    subprocess.run(
        ['pandoc', '-f', 'markdown', '-t', 'html', '--standalone', '--css', css_name, '-o', str(out_path)],
        input=markdown_text,
        text=True,
        cwd=str(out_path.parent),
        check=True,
    )


def insert_qr_block(html_text: str, qr_path: str, label: str) -> str:
    block = (
        f'<div class="qr-block">'
        f'<img src="{qr_path}" alt="QR code" />'
        f'<span>{label}</span>'
        f'</div>'
    )
    body_match = re.search(r'<body[^>]*>', html_text, flags=re.I)
    if not body_match:
        return html_text
    insert_at = body_match.end()
    return html_text[:insert_at] + '\n' + block + html_text[insert_at:]


def extract_body(html_text: str) -> str:
    match = re.search(r'<body[^>]*>(.*)</body>', html_text, flags=re.S | re.I)
    return match.group(1).strip() if match else html_text


def logo_data_uri() -> str:
    if not LOGO_SRC.exists():
        return ''
    svg_text = LOGO_SRC.read_text(encoding='utf-8', errors='ignore')
    match = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', svg_text)
    if match:
        return f'data:image/png;base64,{match.group(1)}'
    svg_bytes = LOGO_SRC.read_bytes()
    encoded = base64.b64encode(svg_bytes).decode('ascii')
    return f'data:image/svg+xml;base64,{encoded}'


def insert_brand_header(html_text: str, logo_uri: str) -> str:
    header = (
        '<div class="brand-header">'
        '  <table class="brand-table">'
        '    <tr>'
        '      <td class="brand-logo-cell">'
        f'        <img class="brand-logo" src="{logo_uri}" alt="The King\'s College" />'
        '      </td>'
        '      <td class="brand-text-cell">'
        '        <div class="brand-title">Year 10 Digital Technologies</div>'
        '        <div class="brand-subtitle">The King\'s College · 2026</div>'
        '      </td>'
        '    </tr>'
        '  </table>'
        '</div>'
    )
    body_match = re.search(r'<body[^>]*>', html_text, flags=re.I)
    if not body_match:
        return html_text
    insert_at = body_match.end()
    return html_text[:insert_at] + '\n' + header + '\n' + html_text[insert_at:]


def build_calendar_and_scope(base_url: str) -> None:
    logo_uri = logo_data_uri()
    for md_name, base in FILES.items():
        md_path = CONTENT_DIR / md_name
        text = md_path.read_text(encoding='utf-8')
        updated = git_last_updated(md_path)
        text = text.replace('{{LAST_UPDATED}}', updated)

        for out_dir in (EXPORTS_DIR, PUBLIC_EXPORTS):
            out_dir.mkdir(parents=True, exist_ok=True)
            html_path = out_dir / f'{base}.html'
            pdf_path = out_dir / f'{base}.pdf'

            run_pandoc(text, html_path, 'print.css')

            html_text = html_path.read_text(encoding='utf-8')
            html_text = insert_brand_header(html_text, logo_uri)
            html_path.write_text(html_text, encoding='utf-8')

            subprocess.run(['weasyprint', str(html_path), str(pdf_path)], check=True)


def build_combined_pack(base_url: str) -> None:
    logo_uri = logo_data_uri()
    calendar_html = (EXPORTS_DIR / 'assessment-calendar-2026.html').read_text(encoding='utf-8')
    scope_html = (EXPORTS_DIR / 'scope-sequence-2026.html').read_text(encoding='utf-8')

    calendar_body = extract_body(calendar_html)
    scope_body = extract_body(scope_html)

    combined_html = (
        '<!DOCTYPE html>\n'
        '<html>\n'
        '<head>\n'
        '  <meta charset="utf-8" />\n'
        '  <title>Year 10 Digital Technologies Printables (2026)</title>\n'
        '  <link rel="stylesheet" href="print.css" />\n'
        '</head>\n'
        '<body>\n'
        '  <h1>Year 10 Digital Technologies Printables (2026)</h1>\n'
        '  <h2>Assessment Calendar</h2>\n'
        f'  {calendar_body}\n'
        '  <h2>Scope and Sequence</h2>\n'
        f'  {scope_body}\n'
        '</body>\n'
        '</html>\n'
    )

    for out_dir in (EXPORTS_DIR, PUBLIC_EXPORTS):
        html_path = out_dir / 'printables-2026.html'
        pdf_path = out_dir / 'printables-2026.pdf'
        html_text = insert_brand_header(combined_html, logo_uri)
        html_path.write_text(html_text, encoding='utf-8')
        subprocess.run(['weasyprint', str(html_path), str(pdf_path)], check=True)


def build_teacher_pack(base_url: str) -> None:
    logo_uri = logo_data_uri()
    outline = strip_top_heading(strip_print_elements((ROOT / 'docs' / 'assessment-outline.md').read_text(encoding='utf-8')))
    calendar = strip_top_heading(strip_print_elements((CONTENT_DIR / 'assessment-calendar-2026.md').read_text(encoding='utf-8')))
    scope = strip_top_heading(strip_print_elements((CONTENT_DIR / 'scope-sequence-2026.md').read_text(encoding='utf-8')))
    weekly_overview = strip_top_heading((ROOT / 'planners' / 'weekly' / 'overview.md').read_text(encoding='utf-8'))

    rubric_blocks = []
    for title, path in RUBRICS:
        if not path.exists():
            continue
        rubric_text = demote_headings(strip_top_heading(path.read_text(encoding='utf-8')), levels=2)
        rubric_blocks.append(f'### {title}\n\n{rubric_text}')

    rubrics_text = '\n'.join(rubric_blocks)

    combined_md = (
        '# Year 10 Digital Technologies Teacher Pack (2026)\n\n'
        '## Assessment Outline\n\n'
        f'{outline}\n\n'
        '## Weekly Overview\n\n'
        f'{weekly_overview}\n\n'
        '## Assessment Calendar\n\n'
        f'{calendar}\n\n'
        '## Scope and Sequence\n\n'
        f'{scope}\n\n'
        '## Assessment Rubrics\n\n'
        f'{rubrics_text}\n'
    )

    for out_dir in (EXPORTS_DIR, PUBLIC_EXPORTS):
        html_path = out_dir / 'teacher-pack-2026.html'
        pdf_path = out_dir / 'teacher-pack-2026.pdf'
        run_pandoc(combined_md, html_path, 'print.css')
        html_text = html_path.read_text(encoding='utf-8')
        html_text = insert_brand_header(html_text, logo_uri)
        html_path.write_text(html_text, encoding='utf-8')
        subprocess.run(['weasyprint', str(html_path), str(pdf_path)], check=True)


def update_printables_readme() -> None:
    readme = (
        '# Print Exports\n\n'
        'Printable HTML versions are available:\n'
        '- `exports/assessment-calendar-2026.html`\n'
        '- `exports/scope-sequence-2026.html`\n'
        '- `exports/printables-2026.html`\n'
        '- `exports/teacher-pack-2026.html`\n\n'
        'Printable PDF versions are available:\n'
        '- `exports/assessment-calendar-2026.pdf`\n'
        '- `exports/scope-sequence-2026.pdf`\n'
        '- `exports/printables-2026.pdf`\n'
        '- `exports/teacher-pack-2026.pdf`\n'
    )
    (EXPORTS_DIR / 'README.md').write_text(readme, encoding='utf-8')


def main() -> None:
    base_url = load_base_url()
    build_calendar_and_scope(base_url)
    build_combined_pack(base_url)
    build_teacher_pack(base_url)
    update_printables_readme()


if __name__ == '__main__':
    main()
