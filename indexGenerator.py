import re
import os
import urllib.parse

# --- SETTINGS ---
INPUT_FILE = "courses.html"  # Your Notion export file
OUTPUT_FILE = "index.html"   # The resulting dashboard
PAGE_TITLE = "My Learning Dashboard"
INTERMEDIATE_PAGES_DIR = "course_pages"  # Directory for intermediate pages

# --- GITHUB LINKS DICTIONARY ---
# Add your GitHub project links here
# Use None to hide the GitHub box entirely, empty string "" to show "coming soon"
GITHUB_LINKS = {
    "Cloud Computing": "https://github.com/ivanbrillo/CloudProject",
    "Deep Learning": None,  # No project - box will be hidden
    "Distributed System": "https://github.com/ivanbrillo/FederatedLearningErlang",
    "Industrial Applications": "https://github.com/andreabochicchio02/VisionChat",
    "IoT": "https://github.com/ivanbrillo/IoTproject",
    "IR, CV and LM": "https://github.com/ivanbrillo/TransUNet",
    "Large scale database": "https://github.com/ivanbrillo/BioConnect",
    "ML": "https://github.com/ivanbrillo/ArtificialTouch",
    "MOEA and RL": "https://github.com/ivanbrillo/NoProp",
    "Process Mining and Intelligence": "./../HEART DISEASE DETECTOR.zip",
    "Project Management": "https://github.com/ivanbrillo/SignLearnAI",
}

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

def create_intermediate_page(title, icon, cover, notes_links, github_link=""):
    """Creates an intermediate page with links to notes and GitHub project
    
    Args:
        title: Course title
        icon: Emoji icon
        cover: CSS cover style
        notes_links: List of tuples [(link, description, icon), ...] or single link string
        github_link: GitHub project URL
    """
    # Create a safe filename from title
    safe_filename = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    
    # Handle both single link (backward compatibility) and multiple links
    if isinstance(notes_links, str):
        notes_links = [(notes_links, "Access course notes and materials", "📚")]
    
    # Build the options HTML
    options_html = ""
    
    # Add all notes/resource options
    for link, description, link_icon in notes_links:
        options_html += f"""
        <a href="../{link}" class="option-card">
            <div class="option-cover" style="{cover}"></div>
            <div class="option-content">
                <div class="option-icon">{link_icon}</div>
                <div class="option-title">{description}</div>
                <div class="option-description">{description}</div>
            </div>
        </a>
"""
    
    # Add GitHub option (only if not explicitly None)
    if github_link is not None:
        # Determine if it's a zip file or GitHub link
        is_zip = github_link.lower().endswith('.zip') if github_link else False
        icon = "📦" if is_zip else "💻"
        title = "Download Project" if is_zip else "View Project"
        description = "Download project zip file" if is_zip else ('GitHub repository and project code' if github_link else 'GitHub link coming soon...')
        
        options_html += f"""
        <a href="{github_link if github_link else '#'}" class="option-card {'disabled' if not github_link else ''}" {'onclick="return false;"' if not github_link else ''}>
            <div class="option-cover" style="{cover}"></div>
            <div class="option-content">
                <div class="option-icon">{icon}</div>
                <div class="option-title">{title}</div>
                <div class="option-description">{description}</div>
            </div>
        </a>
"""
    
    intermediate_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background-color: #191919;
            color: #FFFFFF;
            padding: 40px;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .course-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        h1 {{
            font-weight: 700;
            font-size: 36px;
            margin: 0;
        }}
        .back-link {{
            position: absolute;
            top: 20px;
            left: 20px;
            color: #888;
            text-decoration: none;
            font-size: 14px;
        }}
        .back-link:hover {{
            color: #FFF;
        }}
        .options-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            max-width: 1200px;
            width: 100%;
        }}
        .option-card {{
            background-color: #2F3437;
            border-radius: 8px;
            overflow: hidden;
            text-decoration: none;
            color: inherit;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            transition: transform 0.2s ease, background 0.2s;
            display: flex;
            flex-direction: column;
            border: 1px solid #333;
        }}
        .option-card:not(.disabled):hover {{
            background-color: #3F4447;
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.4);
        }}
        .option-cover {{
            height: 150px;
            width: 100%;
            {cover}
            background-size: cover;
            background-position: center;
        }}
        .option-content {{
            padding: 24px;
            text-align: center;
        }}
        .option-icon {{
            font-size: 32px;
            margin-bottom: 12px;
        }}
        .option-title {{
            font-weight: 600;
            font-size: 20px;
            margin-bottom: 8px;
        }}
        .option-description {{
            color: #AAA;
            font-size: 14px;
        }}
        .disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-link">← Back to Dashboard</a>
    
    <div class="header">
        <div class="course-icon">{icon}</div>
        <h1>{title}</h1>
    </div>

    <div class="options-container">
{options_html}
    </div>
</body>
</html>
"""
    
    # Ensure the intermediate pages directory exists
    os.makedirs(INTERMEDIATE_PAGES_DIR, exist_ok=True)
    
    # Write the intermediate page
    intermediate_path = os.path.join(INTERMEDIATE_PAGES_DIR, f"{safe_filename}.html")
    with open(intermediate_path, 'w', encoding='utf-8') as f:
        f.write(intermediate_html)
    
    # Return the relative path to this intermediate page
    return f"{INTERMEDIATE_PAGES_DIR}/{safe_filename}.html"

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
    resources_by_course = {}  # Dictionary to group resources by course name

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
            
            # Group resources by course name
            if title not in resources_by_course:
                resources_by_course[title] = {
                    "title": title,
                    "icon": icon,
                    "cover": cover,
                    "links": [],
                    "type": "Notion"
                }
            
            # Custom description for Deep Learning HTML
            description = "Deep Learning LAB" if title == "Deep Learning" else "HTML notes and course materials"
            resources_by_course[title]["links"].append((link, description, "📚"))
    else:
        print(f"Warning: {INPUT_FILE} not found. Skipping HTML parsing.")

    # 2. SCAN FOR LOCAL PDF FILES
    for file in os.listdir('.'):
        if file.lower().endswith('.pdf'):
            title = os.path.splitext(file)[0]
            pdf_link = urllib.parse.quote(file)
            
            # Generate gradient cover based on filename
            cover = get_fallback_cover(title)
            
            # Check if this PDF should be merged with an existing course
            # Special case: "DL" merges with "Deep Learning"
            merge_with = None
            if title == "DL":
                merge_with = "Deep Learning"
            elif title == "ML":
                merge_with = None  # ML stays separate for now
            elif title == "MOEA and RL":
                merge_with = None  # Stays separate
            
            if merge_with and merge_with in resources_by_course:
                # Merge this PDF into existing course
                # Custom description for DL PDF
                pdf_description = "Deep Learning Theory" if title == "DL" else f"PDF - {title}"
                resources_by_course[merge_with]["links"].append((pdf_link, pdf_description, "📕"))
            else:
                # Create new entry for this PDF
                if title not in resources_by_course:
                    resources_by_course[title] = {
                        "title": title,
                        "icon": "📕",
                        "cover": cover,
                        "links": [],
                        "type": "PDF"
                    }
                resources_by_course[title]["links"].append((pdf_link, f"PDF - {title}", "📕"))

    # 3. CREATE INTERMEDIATE PAGES AND CARDS
    for course_name, course_data in resources_by_course.items():
        # Get GitHub link from dictionary
        github_link = GITHUB_LINKS.get(course_name, "")
        
        # Create intermediate page with all links for this course
        intermediate_link = create_intermediate_page(
            course_data["title"],
            course_data["icon"],
            course_data["cover"],
            course_data["links"],
            github_link=github_link
        )
        
        cards.append({
            "title": course_data["title"],
            "link": intermediate_link,
            "icon": course_data["icon"],
            "cover": course_data["cover"],
            "type": course_data["type"]
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