# 💳 GitHub Dev Card Generator

An AI-powered developer card generator that orchestrates intelligent agents to analyze GitHub profiles and render high-fidelity, interactive developer cards with curated aesthetic themes. Powered by **Google ADK (Agent Development Kit)**, **FastMCP**, and **FastAPI** with a stunning frontend experience.

---

## 🔒 Security Notice: Safe & Secure Setup
Your sensitive API credentials are **100% safe**. The project employs a strict `.gitignore` policy that completely excludes local configuration files (`.env`, `backend/.env`) and temporary folders from being committed or pushed to remote repositories. The backend is designed to securely load these configurations at runtime via environment variables.

---

## ✨ Features

- **🤖 Intelligent Agent Orchestration**: Powered by **Google ADK** to sequence actions dynamically:
  1. Scrapes GitHub user profiles, repos, and language statistics.
  2. Analyzes the developer's profile via Gemini to determine their distinct vibe, skills, and fun facts.
  3. Generates high-fidelity modern CSS-themed HTML card templates.
  4. Saves card outputs locally.
- **⚡ Bulletproof Fallbacks**: If Gemini API quotas are exhausted, the FastAPI server seamlessly executes a direct fallback generator keeping the application functional.
- **🎨 Premium Visual Aesthetics**: Generates cards across **5 distinct developer archetypes**:
  - `hacker`: Dark cyber-grid with toxic neon green accents.
  - `builder`: Clean, premium light SaaS card with deep purple/indigo gradients.
  - `researcher`: Sophisticated dark slate-blue with cosmic indigo glow.
  - `designer`: Sophisticated amber/pink warm glassmorphism aesthetic.
  - `open-source-hero`: Deep emerald glassmorphism showing true community spirit.
- **🐳 Container Ready**: Fully prepared with multi-service **Docker Compose** configuration for rapid deployment.

---

## 🛠️ Technology Stack

- **Backend**: FastAPI, FastMCP, Google ADK, Google GenAI SDK, Httpx, Uvicorn, Pydantic, Python 3.11+
- **Frontend**: Responsive modern HTML5, CSS3, and dynamic interactive Vanilla JavaScript (Vanilla CSS glassmorphism and subtle micro-animations).
- **Deployment**: Docker & Docker Compose

---

## 📂 Project Structure

```text
github-card-generator/
├── backend/
│   ├── .env                 # Local secrets (ignored by Git)
│   ├── agent.py             # Google ADK LLM Agent setup
│   ├── main.py              # FastAPI endpoint routing and fallback logic
│   ├── mcp_server.py        # FastMCP server exposing toolsets (scrapers, generators)
│   ├── requirements.txt     # Python backend dependencies
│   ├── Dockerfile           # Backend container instructions
│   └── static/              # Card directory and assets
├── frontend/
│   ├── index.html           # Beautiful, responsive single-page web app
│   └── Dockerfile           # Nginx server container setup for the frontend
├── docker-compose.yml       # Production-ready orchestrator for services
├── .env.example             # Template for API keys
└── .gitignore               # Strict git exclusion rules
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher installed.
- A Gemini API Key from [Google AI Studio](https://aistudio.google.com/).
- (Optional) A GitHub Personal Access Token (for higher API rate limits).

### 1. Local Development Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/arpbiswas04-coder/Github-card-generator.git
   cd Github-card-generator
   ```

2. **Configure Environment Variables**:
   Copy `.env.example` to `backend/.env` and replace the placeholders:
   ```bash
   cp .env.example backend/.env
   ```
   Open `backend/.env` and fill in your keys:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   GITHUB_TOKEN=your_github_token_here
   PORT=8080
   ```

3. **Install Dependencies & Start Backend**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   pip install -r requirements.txt
   python main.py
   ```
   The backend server will launch at `http://localhost:8080`.

4. **Launch Frontend**:
   Simply open `frontend/index.html` in your browser, or serve it using any simple local server.

---

### 2. Run with Docker Compose (Recommended)

To spin up the entire frontend and backend cluster automatically:
```bash
docker-compose up --build
```
- **Frontend**: Accessible at `http://localhost:3000`
- **Backend API**: Accessible at `http://localhost:8080`

---

## 💡 How it Works (Under the Hood)

1. The FastAPI backend receives the `/generate` request with a GitHub username.
2. The request is passed to the **Google ADK LlmAgent**, which is equipped with custom tools served by **FastMCP**.
3. The agent calls:
   - `scrape_github` to retrieve the developer's user statistics and repository metadata.
   - `analyze_profile` using `gemini-pro` to output a structured JSON analysis (determining developer vibe, skills, fun facts, and custom theme).
   - `generate_card_html` to build the complete, self-contained HTML/CSS block.
   - `save_card` to store the card in the static assets path.
4. The generated card is sent back and instantly rendered inside the interactive React-like frontend interface with entrance animations and glassmorphism.

---

## 📜 License
This project is open-source and available under the MIT License.
