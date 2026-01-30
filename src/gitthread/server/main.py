from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse
import os
from ..parser import parse_github_url
from ..ingestor import GHIngestor, format_thread_to_markdown
from gitingest import ingest
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="gitthread")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Optional: Add static files if needed
# app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ingest")
async def ingest_thread_web(request: Request, url: str = Form(...), include_repo: bool = Form(True)):
    thread_info = parse_github_url(url)
    if not thread_info:
        raise HTTPException(status_code=400, detail="Invalid GitHub Issue/PR URL")

    token = os.getenv("GITHUB_TOKEN")
    ingestor = GHIngestor(token=token)
    
    try:
        data = ingestor.ingest_thread(thread_info)
        md_output = format_thread_to_markdown(data)
        
        if include_repo:
            repo_url = f"https://github.com/{thread_info.owner}/{thread_info.repo}"
            summary, tree, _ = ingest(repo_url, token=token)
            
            repo_context = f"\n\n# Repository Context: {thread_info.owner}/{thread_info.repo}\n"
            repo_context += f"## Summary\n{summary}\n"
            repo_context += f"## Directory Structure\n```text\n{tree}\n```\n"
            md_output += repo_context
            
        return PlainTextResponse(md_output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
