#!/usr/bin/env python3
"""
Script to apply dark theme and remove empty tags/date section from Notion-exported HTML files.
"""

import os
import re
from pathlib import Path

# Dark theme CSS to be injected
DARK_THEME_CSS = """
/* Dark Theme */
@media only screen {
    body {
        background-color: #1e1e1e;
        color: #f0f0f0;
    }
}

html {
    background-color: #1e1e1e;
}

body {
    color: #f0f0f0;
}

h1, h2, h3 {
    color: #e4e4e4;
}

a, a.visited {
    color: #4a9eff;
}

.page-title {
    color: #ffffff;
}

code {
    background: #2d2d2d;
    color: #f0f0f0;
}

.callout {
    background: #2d2d2d;
    border: 1px solid #404040;
}

table, th, td {
    border-color: #404040;
}

th {
    color: rgba(212, 212, 212, 0.6);
}

hr {
    border-bottom-color: rgba(212, 212, 212, 0.09);
}

.source {
    background: #2d2d2d;
    border-color: #404040;
}

.pdf-relative-link-path {
    color: #b4b4b4;
}

.table_of_contents-link {
    border-bottom-color: rgba(212, 212, 212, 0.18);
}

pre {
    background: #2d2d2d;
}

blockquote {
    border-left-color: #404040;
}

/* Fix KaTeX equations - show only rendered version, hide MathML source */
.notion-text-equation-token .katex-mathml,
.katex-mathml {
    display: none !important;
}

.notion-text-equation-token .katex-html,
.katex-html {
    display: inline !important;
}

/* Fix highlight text colors for dark theme */
.highlight-default {
    color: rgba(212, 212, 212, 1) !important;
}

.highlight-default_background {
    color: rgba(212, 212, 212, 1) !important;
}

.highlight-gray_background {
    color: rgba(212, 212, 212, 1) !important;
}

.highlight-brown_background {
    color: rgba(212, 212, 212, 1) !important;
}

.highlight-orange_background {
    color: rgba(212, 212, 212, 1) !important;
}

.highlight-yellow_background {
    color: rgba(212, 212, 212, 1) !important;
}

.highlight-teal_background {
    color: rgba(212, 212, 212, 1) !important;
}

.highlight-blue_background {
    color: rgba(212, 212, 212, 1) !important;
}

.highlight-purple_background {
    color: rgba(212, 212, 212, 1) !important;
}

.highlight-pink_background {
    color: rgba(212, 212, 212, 1) !important;
}

.highlight-red_background {
    color: rgba(212, 212, 212, 1) !important;
}

.block-color-default {
    color: inherit;
}
"""

def process_html_file(file_path):
    """Process a single HTML file to add dark theme and remove properties table."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Add favicon link in head if not present
        favicon_link = '<link rel="icon" type="image/svg+xml" href="../../../favicon.svg">'
        if 'favicon.svg' not in content and '<head>' in content:
            content = content.replace('<head>', f'<head>\n{favicon_link}')
        
        # 2. Add KaTeX CSS link in head if not present
        katex_css = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.25/dist/katex.min.css" crossorigin="anonymous">'
        if katex_css not in content and '<head>' in content:
            content = content.replace('<head>', f'<head>\n{katex_css}')
        
        # 3. Add Prism.js for code syntax highlighting (dark theme)
        prism_css = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">'
        prism_js = '<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>'
        
        if prism_css not in content and '<head>' in content:
            content = content.replace('</head>', f'{prism_css}\n</head>')
        
        if prism_js not in content and '</body>' in content:
            content = content.replace('</body>', f'{prism_js}\n</body>')
        
        # 4. Add dark theme CSS before </style>
        if DARK_THEME_CSS not in content:
            content = content.replace('</style>', f'{DARK_THEME_CSS}\n</style>')
        
        # 5. Remove the properties table (tags, created date, etc.)
        # This regex matches the entire <table class="properties">...</table> block
        content = re.sub(
            r'<table class="properties">.*?</table>',
            '',
            content,
            flags=re.DOTALL
        )
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def find_and_process_html_files(root_dir):
    """Find all HTML files in the Courses directory and process them."""
    root_path = Path(root_dir)
    courses_dir = root_path / "Courses" / "Courses"
    
    if not courses_dir.exists():
        print(f"Directory not found: {courses_dir}")
        return
    
    # Find all HTML files recursively
    html_files = list(courses_dir.rglob("*.html"))
    
    if not html_files:
        print("No HTML files found.")
        return
    
    print(f"Found {len(html_files)} HTML files to process...\n")
    
    processed_count = 0
    for html_file in html_files:
        if process_html_file(html_file):
            processed_count += 1
            print(f"✓ Processed: {html_file.relative_to(root_path)}")
        else:
            print(f"○ Skipped (no changes): {html_file.relative_to(root_path)}")
    
    print(f"\n{'='*60}")
    print(f"Complete! Modified {processed_count} out of {len(html_files)} files.")
    print(f"{'='*60}")

if __name__ == "__main__":
    # Get the script's directory (workspace root)
    script_dir = Path(__file__).parent
    find_and_process_html_files(script_dir)
