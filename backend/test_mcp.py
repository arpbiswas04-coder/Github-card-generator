import asyncio
import json
import os
from mcp_server import scrape_github, analyze_profile, generate_card_html
from dotenv import load_dotenv

load_dotenv()

async def test_end_to_end():
    username = "torvalds"
    print(f"--- Testing end-to-end for: {username} ---")
    
    # 1. Scrape GitHub
    print("Step 1: Scraping GitHub...")
    try:
        github_data = await scrape_github(username)
        if "error" in github_data:
            print(f"Error scraping github: {github_data['error']}")
            return
        print("Scrape successful.")
    except Exception as e:
        print(f"Scrape failed with exception: {e}")
        return

    # 2. Analyze Profile
    print("Step 2: Analyzing Profile with Gemini...")
    try:
        # Check if GOOGLE_API_KEY is set
        if not os.getenv("GOOGLE_API_KEY"):
            print("Error: GOOGLE_API_KEY not found in .env")
            return
            
        analysis = await analyze_profile(github_data)
        print("Analysis successful.")
    except Exception as e:
        print(f"Analysis failed with exception: {e}")
        return

    # 3. Generate HTML
    print("Step 3: Generating HTML Card...")
    try:
        html = generate_card_html(username, github_data, analysis)
        print("HTML generation successful.")
    except Exception as e:
        print(f"HTML generation failed with exception: {e}")
        return

    # 4. Results
    print("\n--- Final Results ---")
    print(f"Card Theme: {analysis.get('card_theme')}")
    print(f"Developer Vibe: {analysis.get('developer_vibe')}")
    
if __name__ == "__main__":
    asyncio.run(test_end_to_end())
