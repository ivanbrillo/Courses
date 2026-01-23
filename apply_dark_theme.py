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

# Enhanced styling for main course pages (full-width banner, modern design)
MAIN_PAGE_ENHANCED_CSS = """
/* Enhanced Banner and Layout for Main Course Pages */

/* Remove body margins for full-width banner effect */
@media only screen {
    body {
        margin: 0 !important;
        padding: 0;
    }
}

/* Full-width banner image - reduced height for banner effect */
.page-cover-image {
    display: block;
    object-fit: cover;
    width: 100vw !important;
    max-width: 100vw !important;
    height: 200px !important;
    max-height: 200px !important;
    min-height: 200px !important;
    margin: 0 !important;
    padding: 0 !important;
    position: relative;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    filter: brightness(0.85);
}

/* Enhanced header styling */
header {
    position: relative;
    margin: 0 !important;
    padding: 0 !important;
    background: linear-gradient(to bottom, rgba(30, 30, 30, 0) 0%, rgba(30, 30, 30, 0.8) 80%, rgba(30, 30, 30, 1) 100%);
}

/* Icon positioned over banner */
.page-header-icon-with-cover {
    position: relative;
    margin-top: -2.5rem !important;
    margin-left: 2rem !important;
    font-size: 4rem !important;
    display: inline-flex !important;
    align-items: center;
    justify-content: center;
    line-height: 1;
}

.page-header-icon-with-cover .icon {
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
}

/* Enhanced title styling */
.page-title {
    font-size: 3rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin: 1rem 0 0 0 !important;
    padding: 0 2rem 1rem 2rem !important;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
    letter-spacing: -0.02em;
}

/* Content area with max-width and centered */
.page-body {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
}

/* Enhanced link boxes */
.link-to-page {
    margin: 1em 0;
    padding: 1rem 1.5rem;
    background: linear-gradient(135deg, rgba(45, 45, 45, 0.8) 0%, rgba(35, 35, 35, 0.9) 100%);
    border: 1px solid rgba(74, 158, 255, 0.3);
    border-radius: 8px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.link-to-page:hover {
    border-color: rgba(74, 158, 255, 0.6);
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(74, 158, 255, 0.2);
}

.link-to-page a {
    color: #4a9eff !important;
    text-decoration: none;
    font-weight: 500;
    font-size: 1.1rem;
    display: block;
}

.link-to-page a:hover {
    color: #6cb3ff !important;
}

/* Article content styling */
article.page {
    background: #1e1e1e;
}
"""

def process_html_file(file_path, is_main_page=False):
    """Process a single HTML file to add dark theme and remove properties table.
    
    Args:
        file_path: Path to the HTML file
        is_main_page: If True, applies enhanced styling for main course pages
    """
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
        
        # 5. For main pages, remove any existing enhanced CSS and add the current one
        if is_main_page:
            # Remove old enhanced CSS if present
            content = re.sub(
                r'/\* Enhanced Banner and Layout for Main Course Pages \*/.*?/\* Article content styling \*/\n[^}]+}',
                '',
                content,
                flags=re.DOTALL
            )
            # Add current enhanced CSS
            if MAIN_PAGE_ENHANCED_CSS not in content:
                content = content.replace('</style>', f'{MAIN_PAGE_ENHANCED_CSS}\n</style>')
        
        # 6. Remove the properties table (tags, created date, etc.)
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
    main_page_count = 0
    
    for html_file in html_files:
        # Determine if this is a main course page (directly in Courses/Courses/, not in a subdirectory)
        # Main pages are like: Courses/Courses/Cloud Computing 1a4eea59ca7a80a0b836e90366079610.html
        # Subpages are like: Courses/Courses/Cloud Computing/Foundamental Concepts 1a4eea59ca7a80139ef8fa93e18e38b6.html
        relative_path = html_file.relative_to(courses_dir)
        is_main_page = len(relative_path.parts) == 1  # Only one part means it's directly in Courses/Courses/
        
        if process_html_file(html_file, is_main_page):
            processed_count += 1
            if is_main_page:
                main_page_count += 1
                print(f"✓ Processed (Main Page): {html_file.relative_to(root_path)}")
            else:
                print(f"✓ Processed: {html_file.relative_to(root_path)}")
        else:
            print(f"○ Skipped (no changes): {html_file.relative_to(root_path)}")
    
    print(f"\n{'='*60}")
    print(f"Complete! Modified {processed_count} out of {len(html_files)} files.")
    print(f"Enhanced styling applied to {main_page_count} main course pages.")
    print(f"{'='*60}")

if __name__ == "__main__":
    # Get the script's directory (workspace root)
    script_dir = Path(__file__).parent
    find_and_process_html_files(script_dir)
