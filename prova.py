import re
import os
import urllib.parse

# --- SETTINGS ---
INPUT_FILE = "courses.html"  # Your Notion export file
OUTPUT_FILE = "index.html"   # The resulting dashboard
PAGE_TITLE = "My Learning Dashboard"

# --- HTML TEMPLATE ---
html_top = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{PAGE_TITLE}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background-color: #191919;
            color: #FFFFFF;
            padding: 40px;
            margin: 0;
        }}
        h1 {{ font-weight: 700; margin-bottom: 20px; font-size: 32px; border-bottom: 1px solid #333; padding-bottom: 20px; }}
        .grid-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .card {{
            background-color: #2F3437;
            border-radius: 6px;
            overflow: hidden;
            text-decoration: none;
            color: inherit;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transition: transform 0.2s ease, background 0.2s;
            display: flex;
            flex-direction: column;
            height: 200px;
            border: 1px solid #333;
        }}
        .card:hover {{
            background-color: #3F4447;
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }}
        .card-cover {{
            height: 110px;
            width: 100%;
            background-size: cover;
            background-position: center;
        }}
        .card-content {{
            padding: 12px 16px;
            display: flex;
            align-items: center;
            flex-grow: 1;
        }}
        .card-icon {{ font-size: 22px; margin-right: 10px; }}
        .card-title {{ font-weight: 600; font-size: 16px; line-height: 1.3; }}
        
        /* Small tag to identify PDF vs Page if needed */
        .type-tag {{
            font-size: 10px;
            opacity: 0.5;
            margin-left: auto;
            border: 1px solid #555;
            padding: 2px 4px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <h1>{PAGE_TITLE}</h1>
    <div class="grid-container">
"""

def get_fallback_cover(seed):
    # Generates a consistent random gradient based on name
    gradients = [
        "linear-gradient(45deg, #FF9A9E 0%, #FECFEF 100%)",
        "linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%)",
        "linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%)",
        "linear-gradient(to top, #cfd9df 0%, #e2ebf0 100%)",
        "linear-gradient(45deg, #fa709a 0%, #fee140 100%)",
        "linear-gradient(to right, #4facfe 0%, #00f2fe 100%)",
        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
    ]
    index = sum(ord(c) for c in seed) % len(gradients)
    return f"background: {gradients[index]};"

def find_image_for_link(link_path):
    # Tries to find if the sub-page has a _files folder with an image
    try:
        decoded_path = urllib.parse.unquote(link_path)
        base_name = os.path.splitext(decoded_path)[0]
        files_dir = base_name + "_files"
        
        if os.path.exists(files_dir):
            for f in os.listdir(files_dir):
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    path = urllib.parse.quote(files_dir + '/' + f)
                    return f"background-image: url('{path}');"
    except:
        pass
    return None

def main():
    cards = []

    # 1. SCAN FOR NOTION HTML COURSES
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex to find table rows with links and icons
        pattern = r'<td class="cell-title"><a href="([^"]+)">(?:<span class="icon">([^<]+)</span>)?(.*?)(?:</a>)'
        matches = re.findall(pattern, content)
        
        for link, icon, title in matches:
            if not icon: icon = "📄"
            title = title.strip()
            
            # Look for specific cover, else gradient
            cover = find_image_for_link(link)
            if not cover:
                cover = get_fallback_cover(title)
                
            cards.append({
                "title": title,
                "link": link,
                "icon": icon,
                "cover": cover,
                "type": "Notion"
            })
    else:
        print(f"Warning: {INPUT_FILE} not found. Skipping HTML parsing.")

    # 2. SCAN FOR LOCAL PDF FILES
    # Loop through current directory
    for file in os.listdir('.'):
        if file.lower().endswith('.pdf'):
            title = os.path.splitext(file)[0]
            # Use a red book icon for PDFs
            icon = "📕" 
            # Ensure filenames with spaces work as links
            link = urllib.parse.quote(file)
            
            # Generate gradient cover based on filename
            cover = get_fallback_cover(title)
            
            cards.append({
                "title": title,
                "link": link,
                "icon": icon,
                "cover": cover,
                "type": "PDF"
            })

    # 3. GENERATE HTML
    gallery_html = ""
    # Optional: Sort alphabetically by title
    cards.sort(key=lambda x: x['title'].lower())

    print(f"Found {len(cards)} items ({len([c for c in cards if c['type']=='PDF'])} PDFs). Generating...")

    for card in cards:
        gallery_html += f"""
        <a href="{card['link']}" class="card">
            <div class="card-cover" style="{card['cover']}"></div>
            <div class="card-content">
                <span class="card-icon">{card['icon']}</span>
                <span class="card-title">{card['title']}</span>
                </div>
        </a>
        """

    final_html = html_top + gallery_html + "</div></body></html>"

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"Success! Created {OUTPUT_FILE}")

if __name__ == "__main__":
    main()