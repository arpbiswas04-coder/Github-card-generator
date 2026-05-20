import os
import json
import httpx
import google.generativeai as genai
from mcp.server.fastmcp import FastMCP
from typing import Dict, List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("GitHub-Dev-Card-Generator")

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro") 

@mcp.tool()
async def scrape_github(username: str) -> dict:
    """Fetch GitHub stats and top repos for a given user."""
    async with httpx.AsyncClient() as client:
        # Fetch user info
        user_resp = await client.get(f"https://api.github.com/users/{username}")
        if user_resp.status_code != 200:
            return {"error": "User not found"}
        
        user_data = user_resp.json()
        
        # Fetch repos
        repos_resp = await client.get(f"https://api.github.com/users/{username}/repos?sort=stars&per_page=10")
        repos_data = repos_resp.json() if repos_resp.status_code == 200 else []
        
        top_6_repos = []
        languages = {}
        
        for repo in repos_data[:6]:
            top_6_repos.append({
                "name": repo.get("name"),
                "stars": repo.get("stargazers_count"),
                "language": repo.get("language"),
                "description": repo.get("description")
            })
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1

        return {
            "name": user_data.get("name") or username,
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "public_repos": user_data.get("public_repos"),
            "followers": user_data.get("followers"),
            "avatar_url": user_data.get("avatar_url"),
            "top_6_repos": top_6_repos,
            "languages": languages
        }

@mcp.tool()
async def analyze_profile(github_data: dict) -> dict:
    """Analyze GitHub profile using Gemini to determine vibe and skills."""
    prompt = f"""
    Analyze this GitHub profile data and provide a personality assessment for a developer card.
    Data: {json.dumps(github_data)}
    
    Return ONLY a JSON object with:
    - developer_vibe: (1 sentence personality)
    - top_skills: (list of 3 string skills)
    - fun_fact: (something clever inferred from their repos)
    - card_theme: (one of: "hacker", "builder", "researcher", "designer", "open-source-hero")
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        return json.loads(content)
    except Exception as e:
        print(f"Gemini error: {e}. Using fallback analysis.")
        langs = list(github_data.get("languages", {}).keys())
        primary_lang = langs[0] if langs else "Code"
        return {
            "developer_vibe": f"A prolific {primary_lang} architect with a passion for open source.",
            "top_skills": langs[:3] if langs else ["Python", "JavaScript", "C++"],
            "fun_fact": f"Has managed to build {github_data.get('public_repos')} projects while growing a following of {github_data.get('followers')} developers.",
            "card_theme": "open-source-hero" if github_data.get("followers", 0) > 100 else "builder"
        }

@mcp.tool()
def generate_card_html(username: str, github_data: dict, analysis: dict) -> str:
    """Generate a fully self-contained premium HTML dev card with modern SaaS aesthetics."""
    theme = analysis.get("card_theme", "builder")
    
    # Premium Theme Configuration for the 5 requested categories
    theme_configs = {
        "hacker": {
            "bg": "#0a0a0c",
            "accent": "#00ff9d",
            "secondary": "#00e5ff",
            "text": "#e0e0e6",
            "muted": "#888891",
            "glow": "rgba(0, 255, 157, 0.2)"
        },
        "builder": {
            "bg": "#ffffff",
            "accent": "#4f46e5",
            "secondary": "#9333ea",
            "text": "#18181b",
            "muted": "#71717a",
            "glow": "rgba(79, 70, 229, 0.15)"
        },
        "researcher": {
            "bg": "#0f172a",
            "accent": "#818cf8",
            "secondary": "#c084fc",
            "text": "#f8fafc",
            "muted": "#94a3b8",
            "glow": "rgba(129, 140, 248, 0.2)"
        },
        "designer": {
            "bg": "#fafafa",
            "accent": "#f59e0b",
            "secondary": "#ec4899",
            "text": "#1c1917",
            "muted": "#78716c",
            "glow": "rgba(245, 158, 11, 0.15)"
        },
        "open-source-hero": {
            "bg": "#022c22",
            "accent": "#10b981",
            "secondary": "#34d399",
            "text": "#ecfdf5",
            "muted": "#6ee7b7",
            "glow": "rgba(16, 185, 129, 0.25)"
        }
    }
    
    c = theme_configs.get(theme, theme_configs["builder"])
    is_dark = theme not in ["builder", "designer"]

    skills_html = "".join([
        f'<span class="skill-badge">{skill}</span>' 
        for skill in analysis.get("top_skills", [])
    ])

    repos_html = "".join([
        f'''
        <div class="repo-mini-card">
            <div class="repo-header">
                <span class="repo-name">{repo["name"]}</span>
                <span class="repo-stars">⭐ {repo["stars"]}</span>
            </div>
            <p class="repo-desc">{repo["description"][:60] if repo["description"] else "No description available..."}</p>
            <div class="repo-footer">
                <span class="repo-lang">{repo["language"] or "Misc"}</span>
            </div>
        </div>
        ''' for repo in github_data.get("top_6_repos", [])[:3]
    ])

    html = f"""
    <div class="premium-card-container" id="card-{username}">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            
            .premium-card-container {{
                --card-width: 380px;
                --accent-color: {c["accent"]};
                --secondary-color: {c["secondary"]};
                --bg-main: {c["bg"]};
                --text-main: {c["text"]};
                --text-muted: {c["muted"]};
                --glow-color: {c["glow"]};
                
                width: var(--card-width);
                position: relative;
                font-family: 'Inter', system-ui, sans-serif;
                color: var(--text-main);
                perspective: 1200px;
                animation: cardEntrance 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
            }}

            @keyframes cardEntrance {{
                from {{ opacity: 0; transform: translateY(40px) rotateX(-10deg); }}
                to {{ opacity: 1; transform: translateY(0) rotateX(0); }}
            }}

            .premium-card-inner {{
                position: relative;
                width: 100%;
                background: var(--bg-main);
                border: 1px solid rgba(128, 128, 128, 0.25);
                border-radius: 32px;
                padding: 32px;
                overflow: hidden;
                box-shadow: 0 30px 60px rgba(0,0,0,0.3), 0 0 40px var(--glow-color);
                transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
                backdrop-filter: blur(12px);
                z-index: 1;
            }}

            .premium-card-inner:hover {{
                transform: translateY(-8px) rotateX(3deg) rotateY(3deg);
                border-color: var(--accent-color);
            }}

            /* Ambient Animated Background */
            .ambient-blob {{
                position: absolute;
                width: 250px;
                height: 250px;
                filter: blur(80px);
                border-radius: 50%;
                z-index: -1;
                opacity: 0.35;
                animation: pulseGlow 8s infinite alternate;
            }}
            .blob-1 {{ top: -80px; right: -80px; background: var(--accent-color); }}
            .blob-2 {{ bottom: -80px; left: -80px; background: var(--secondary-color); animation-delay: -4s; }}

            @keyframes pulseGlow {{
                0% {{ transform: scale(1) translate(0, 0); opacity: 0.3; }}
                100% {{ transform: scale(1.2) translate(15px, 15px); opacity: 0.5; }}
            }}

            .card-header {{
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                margin-bottom: 28px;
            }}

            .avatar-wrapper {{
                position: relative;
                padding: 6px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--accent-color), var(--secondary-color));
                margin-bottom: 18px;
                box-shadow: 0 0 25px var(--glow-color);
                transition: all 0.4s ease;
            }}
            .avatar-wrapper:hover {{ transform: rotate(10deg) scale(1.08); }}

            .avatar-img {{
                width: 95px;
                height: 95px;
                border-radius: 50%;
                background: var(--bg-main);
                border: 4px solid var(--bg-main);
                display: block;
            }}

            .name-h2 {{
                font-size: 1.7rem;
                font-weight: 800;
                margin: 0;
                letter-spacing: -0.8px;
                background: linear-gradient(to bottom, var(--text-main), var(--text-muted));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}

            .username-sub {{
                font-size: 0.9rem;
                color: var(--text-muted);
                margin-top: 4px;
                font-weight: 600;
                opacity: 0.8;
            }}

            .vibe-box {{
                font-style: italic;
                font-size: 0.95rem;
                line-height: 1.6;
                color: var(--text-main);
                margin: 20px 0;
                padding: 16px;
                background: rgba(128, 128, 128, 0.08);
                border-radius: 16px;
                border-left: 4px solid var(--accent-color);
                box-shadow: inset 0 0 10px rgba(0,0,0,0.05);
            }}

            .skills-flex {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 10px;
                margin-bottom: 28px;
            }}

            .skill-badge {{
                padding: 8px 16px;
                background: rgba(128, 128, 128, 0.1);
                border: 1px solid rgba(128, 128, 128, 0.2);
                border-radius: 100px;
                font-size: 0.8rem;
                font-weight: 700;
                color: var(--text-main);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }}
            .skill-badge:hover {{
                background: var(--accent-color);
                color: { "#000" if not is_dark else "#fff" };
                transform: translateY(-3px) scale(1.05);
                box-shadow: 0 8px 20px var(--glow-color);
                border-color: transparent;
            }}

            .stats-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                margin-bottom: 28px;
            }}

            .stat-card {{
                background: rgba(128, 128, 128, 0.08);
                padding: 18px;
                border-radius: 20px;
                text-align: center;
                border: 1px solid rgba(128, 128, 128, 0.15);
                transition: all 0.3s ease;
            }}
            .stat-card:hover {{
                background: rgba(128, 128, 128, 0.12);
                transform: translateY(-4px);
                border-color: var(--secondary-color);
            }}

            .stat-value {{ font-size: 1.4rem; font-weight: 800; display: block; }}
            .stat-label {{ font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px; margin-top: 6px; display: block; font-weight: 700; }}

            .repos-section {{ text-align: left; }}
            .section-title {{
                font-size: 0.8rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 2px;
                color: var(--text-muted);
                margin-bottom: 16px;
                padding-left: 6px;
                opacity: 0.7;
            }}

            .repo-mini-card {{
                background: rgba(128, 128, 128, 0.06);
                border: 1px solid rgba(128, 128, 128, 0.15);
                border-radius: 18px;
                padding: 16px;
                margin-bottom: 12px;
                transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            }}
            .repo-mini-card:hover {{
                background: rgba(128, 128, 128, 0.1);
                border-color: var(--accent-color);
                transform: scale(1.03) translateX(4px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }}

            .repo-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
            .repo-name {{ font-weight: 800; font-size: 0.95rem; color: var(--text-main); }}
            .repo-stars {{ font-size: 0.85rem; font-weight: 600; color: var(--accent-color); }}
            .repo-desc {{ font-size: 0.85rem; color: var(--text-muted); margin: 0 0 10px 0; line-height: 1.5; }}
            .repo-lang {{ font-size: 0.75rem; font-weight: 700; color: var(--secondary-color); }}

            .fun-fact {{
                margin-top: 24px;
                font-size: 0.8rem;
                text-align: center;
                color: var(--text-muted);
                opacity: 0.8;
                font-weight: 500;
                padding: 10px;
                border-top: 1px dashed rgba(128, 128, 128, 0.2);
            }}
        </style>
        
        <div class="premium-card-inner">
            <div class="ambient-blob blob-1"></div>
            <div class="ambient-blob blob-2"></div>
            
            <div class="card-header">
                <div class="avatar-wrapper">
                    <img src="{github_data.get("avatar_url")}" class="avatar-img" alt="avatar" />
                </div>
                <h2 class="name-h2">{github_data.get("name")}</h2>
                <div class="username-sub">@{username}</div>
            </div>

            <div class="vibe-box">
                "{analysis.get("developer_vibe")}"
            </div>

            <div class="skills-flex">
                {skills_html}
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <span class="stat-value">{github_data.get("public_repos")}</span>
                    <span class="stat-label">Projects</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">{github_data.get("followers")}</span>
                    <span class="stat-label">Followers</span>
                </div>
            </div>

            <div class="repos-section">
                <div class="section-title">Top Repositories</div>
                {repos_html}
            </div>

            <div class="fun-fact">
                💡 {analysis.get("fun_fact")}
            </div>
        </div>
    </div>
    """
    return html

@mcp.tool()
def save_card(username: str, html: str) -> str:
    """Save the HTML to static/cards/{username}.html and return path."""
    output_dir = Path("static/cards")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = output_dir / f"{username}.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return f"/static/cards/{username}.html"

if __name__ == "__main__":
    mcp.run()
