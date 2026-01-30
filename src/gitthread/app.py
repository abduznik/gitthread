import streamlit as st
import os
import sys
import asyncio
import gitingest.utils.query_parser_utils

# Ensure the 'src' directory is in sys.path for Streamlit Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# --- CRITICAL FIX: Allow tokens in URLs ---
# This overrides the validation so we can pass 'https://TOKEN@github.com'
gitingest.utils.query_parser_utils._validate_host = lambda host: None

from gitthread.parser import parse_github_url
from gitthread.ingestor import GHIngestor, format_thread_to_markdown
from gitingest import ingest_async
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="gitthread - Ingest GitHub Issues & PRs",
    page_icon="🧵",
    layout="centered"
)

# Custom CSS for dark theme and gitingest-like aesthetic
st.markdown("""
    <style>
    .stApp { background-color: #0f1117; color: #e5e7eb; }
    .main .block-container { padding-top: 5rem; }
    h1 { text-align: center; font-size: 4rem !important; font-weight: 800 !important; margin-bottom: 0.5rem !important; color: white !important; }
    .subtitle { text-align: center; font-size: 1.25rem; color: #9ca3af; margin-bottom: 3rem; }
    .stTextInput input { background-color: #1f2937 !important; color: white !important; border: 1px solid #374151 !important; }
    .stButton button { width: 100%; background-color: white !important; color: black !important; font-weight: bold; padding: 0.75rem; border-radius: 0.5rem; border: none; }
    .stButton button:hover { background-color: #d1d5db !important; }
    .stCheckbox label { color: #e5e7eb !important; }
    div.stDownloadButton > button { background-color: #374151 !important; color: white !important; width: auto !important; padding: 0.25rem 1rem !important; font-size: 0.875rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>gitthread</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Ingest GitHub Issues and Pull Requests into LLM-friendly text dumps.</p>", unsafe_allow_html=True)

url = st.text_input("GitHub Issue or PR URL", placeholder="https://github.com/user/repo/issues/1")

# Advanced Options
with st.expander("Advanced Options & Token"):
    user_token = st.text_input("GitHub Personal Access Token (Optional)", type="password", help="Providing a token allows for higher rate limits and access to private repositories.")
    col1, col2 = st.columns(2)
    with col1:
        include_repo_context = st.checkbox("Include Repository Summary", value=True)
    with col2:
        include_full_repo = st.checkbox("Include Full Repository Content", value=False)

async def perform_ingestion(url_info, token, repo_context, full_repo):
    # API OPERATIONS (Use clean token for PyGithub)
    clean_token = token.strip() if token else None
    ingestor = GHIngestor(token=clean_token)
    
    tasks = []
    # Task 1: Fetch Thread (Uses API)
    tasks.append(asyncio.to_thread(ingestor.ingest_thread, url_info))
    
    # Task 2: Fetch Repo (Uses Git Binary)
    if repo_context or full_repo:
        if clean_token:
            # We manually embed the token into the URL: https://git:TOKEN@github.com/...
            # Using 'git' as the username is the standard compatibility convention for PATs.
            repo_url = f"https://git:{clean_token}@github.com/{url_info.owner}/{url_info.repo}"
            
            # PASS NONE: We renamed the Env Var, so gitingest won't find it there.
            # Passing None here ensures it adds ZERO headers.
            use_token_arg = None 
        else:
            # Public repo / No token case
            repo_url = f"https://github.com/{url_info.owner}/{url_info.repo}"
            use_token_arg = None

        tasks.append(ingest_async(repo_url, token=use_token_arg))
    
    results = await asyncio.gather(*tasks)
    
    thread_data = results[0]
    md_output = format_thread_to_markdown(thread_data)
    
    if len(results) > 1:
        summary, tree, content = results[1]
        md_output += f"\n\n# Repository Context: {url_info.owner}/{url_info.repo}\n"
        md_output += f"## Summary\n{summary}\n"
        md_output += f"## Directory Structure\n```text\n{tree}\n```\n"
        if full_repo:
            md_output += f"\n## Full Repository Content\n{content}\n"
            
    return md_output

if st.button("Ingest"):
    if not url:
        st.error("Please enter a URL")
    else:
        thread_info = parse_github_url(url)
        if not thread_info:
            st.error("Invalid GitHub Issue/PR URL")
        else:
            with st.spinner("Ingesting concurrently..."):
                try:
                    # 1. Get the token safely (UI input takes priority, then Env Var)
                    # We DO NOT set os.environ here. This keeps requests isolated.
                    env_token = os.getenv("GIT_THREAD_TOKEN") or os.getenv("GITHUB_TOKEN")
                    token = user_token if user_token and user_token.strip() else env_token
                    
                    # 2. Run Ingestion
                    # We pass the token directly. The logic in perform_ingestion handles sanitization and URL embedding.
                    md_result = asyncio.run(perform_ingestion(
                        thread_info, 
                        token, 
                        include_repo_context, 
                        include_full_repo
                    ))
                    
                    # 3. Success State
                    st.session_state['output'] = md_result
                    st.session_state['repo_name'] = thread_info.repo
                    st.session_state['number'] = thread_info.number
                    st.success("Ingestion complete!")
                except Exception as e:
                    st.error(f"Error: {e}")

if 'output' in st.session_state:
    md_output = st.session_state['output']
    btn_col1, btn_col2, _ = st.columns([1, 1, 2])
    with btn_col1:
        st.download_button(
            label="Download .md",
            data=md_output,
            file_name=f"gitthread_{st.session_state['repo_name']}_{st.session_state['number']}.md",
            mime="text/markdown"
        )
    with btn_col2:
        if st.button("Copy to Clipboard"):
            st.write(f'<script>navigator.clipboard.writeText({repr(md_output)});</script>', unsafe_allow_html=True)
            st.toast("Copied to clipboard!")

    st.subheader("Result")
    st.code(md_output, language="markdown")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #6b7280; font-size: 0.875rem;'>Inspired by <a href='https://gitingest.com' target='_blank'>gitingest</a></div>", unsafe_allow_html=True)
