import streamlit as st
import os
from gitthread.parser import parse_github_url
from gitthread.ingestor import GHIngestor, format_thread_to_markdown
from gitingest import ingest
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="gitthread - Ingest GitHub Issues & PRs",
    page_icon="🧵",
    layout="centered"
)

# Custom CSS for gitingest-like aesthetic
st.markdown("""
    <style>
    .stApp {
        background-color: #f9fafb;
    }
    .main .block-container {
        padding-top: 5rem;
    }
    h1 {
        text-align: center;
        font-size: 4rem !important;
        font-weight: 800 !important;
        margin-bottom: 1rem !important;
    }
    .subtitle {
        text-align: center;
        font-size: 1.25rem;
        color: #4b5563;
        margin-bottom: 3rem;
    }
    .stButton button {
        width: 100%;
        background-color: black;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: none;
    }
    .stButton button:hover {
        background-color: #1f2937;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>gitthread</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Ingest GitHub Issues and Pull Requests into LLM-friendly text dumps.</p>", unsafe_allow_html=True)

url = st.text_input("GitHub Issue or PR URL", placeholder="https://github.com/user/repo/issues/1")
include_repo = st.checkbox("Include Repository Context (gitingest)", value=True)

if st.button("Ingest"):
    if not url:
        st.error("Please enter a URL")
    else:
        thread_info = parse_github_url(url)
        if not thread_info:
            st.error("Invalid GitHub Issue/PR URL")
        else:
            with st.spinner("Ingesting..."):
                try:
                    token = os.getenv("GITHUB_TOKEN") or st.secrets.get("GITHUB_TOKEN")
                    ingestor = GHIngestor(token=token)
                    
                    data = ingestor.ingest_thread(thread_info)
                    md_output = format_thread_to_markdown(data)
                    
                    if include_repo:
                        repo_url = f"https://github.com/{thread_info.owner}/{thread_info.repo}"
                        summary, tree, _ = ingest(repo_url, token=token)
                        
                        repo_context = f"\n\n# Repository Context: {thread_info.owner}/{thread_info.repo}\n"
                        repo_context += f"## Summary\n{summary}\n"
                        repo_context += f"## Directory Structure\n```text\n{tree}\n```\n"
                        md_output += repo_context
                    
                    st.success("Ingestion complete!")
                    
                    st.subheader("Result")
                    st.code(md_output, language="markdown")
                    
                    st.download_button(
                        label="Download as .md",
                        data=md_output,
                        file_name=f"gitthread_{thread_info.repo}_{thread_info.number}.md",
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #6b7280; font-size: 0.875rem;'>Inspired by <a href='https://gitingest.com' target='_blank'>gitingest</a></div>", unsafe_allow_html=True)

