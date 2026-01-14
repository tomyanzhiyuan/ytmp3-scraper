# Contributing to YouTube MP3 Scraper

First off, thank you for considering contributing to YouTube MP3 Scraper! It's people like you that make open source such a great community.

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if applicable**
- **Include your environment details** (OS, Python version, Node version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the proposed enhancement**
- **Explain why this enhancement would be useful**
- **List any alternatives you've considered**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install dependencies** following the README
3. **Make your changes** with clear, descriptive commits
4. **Test your changes** thoroughly
5. **Update documentation** if needed
6. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- FFmpeg
- Conda (recommended) or pip + npm

### Quick Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ytmp3-scraper.git
cd ytmp3-scraper

# Using Conda (recommended)
conda env create -f environment.yml
conda activate ytmp3-scraper

# Or using pip + npm
cd backend && pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..
```

### Running in Development

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Using Docker

```bash
# Build and run
docker compose up --build

# Development mode (hot reload for backend)
docker compose --profile dev up backend-dev
```

## Style Guidelines

### Python (Backend)

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints for function parameters and return values
- Write docstrings for all public functions
- Keep functions focused and small
- Use `ruff` for linting: `ruff check .`

### TypeScript (Frontend)

- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks
- Keep components small and focused
- Use meaningful variable and function names

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests when relevant

## Project Structure

```
ytmp3-scraper/
├── backend/              # FastAPI backend
│   ├── main.py          # API routes and app setup
│   ├── models.py        # Pydantic models
│   ├── downloader.py    # yt-dlp download logic
│   ├── video_scraper.py # Channel scraping
│   └── youtube_api_scraper.py
├── frontend/             # React frontend
│   └── src/
│       ├── App.tsx      # Main component
│       ├── api.ts       # API client
│       └── components/  # UI components
└── output/              # Downloaded files (gitignored)
```

## Questions?

Feel free to open an issue with the "question" label or reach out to the maintainers.

Thank you for contributing! 🎉

