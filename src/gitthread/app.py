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

# Custom CSS for dark theme and gitingest-like aesthetic
st.markdown("""
    <style>
    /* Dark Theme Base */
    .stApp {
        background-color: #0f1117;
        color: #e5e7eb;
    }
    .main .block-container {
        padding-top: 5rem;
    }
    
    /* Header Styling */
    h1 {
        text-align: center;
        font-size: 4rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
        color: white !important;
    }
    .subtitle {
        text-align: center;
        font-size: 1.25rem;
        color: #9ca3af;
        margin-bottom: 3rem;
    }
    
    /* Input Styling */
    .stTextInput input {
        background-color: #1f2937 !important;
        color: white !important;
        border: 1px solid #374151 !important;
    }
    
    /* Button Styling */
    .stButton button {
        width: 100%;
        background-color: white !important;
        color: black !important;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: none;
    }
    .stButton button:hover {
        background-color: #d1d5db !important;
    }
    
    /* Result Box */
    .result-box {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 0.5rem;
        padding: 1rem;
        font-family: monospace;
        color: #d1d5db;
    }

    /* Checkbox labels */
    .stCheckbox label {
        color: #e5e7eb !important;
    }
    
    /* Secondary Buttons (Copy/Download) */
    div.stDownloadButton > button, div.stButton > button.copy-btn {
        background-color: #374151 !important;
        color: white !important;
        width: auto !important;
        padding: 0.25rem 1rem !important;
        font-size: 0.875rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>gitthread</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Ingest GitHub Issues and Pull Requests into LLM-friendly text dumps.</p>", unsafe_allow_html=True)

url = st.text_input("GitHub Issue or PR URL", placeholder="https://github.com/user/repo/issues/1")
col1, col2 = st.columns(2)
with col1:
    include_repo_context = st.checkbox("Include Repository Summary", value=True)
with col2:
    include_full_repo = st.checkbox("Include Full Repository Content", value=False)

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
                    
                    # Fetch Thread Data
                    data = ingestor.ingest_thread(thread_info)
                    md_output = format_thread_to_markdown(data)
                    
                    # Fetch Repo Context if requested
                    if include_repo_context or include_full_repo:
                        repo_url = f"https://github.com/{thread_info.owner}/{thread_info.repo}"
                        summary, tree, content = ingest(repo_url, token=token)
                        
                        md_output += f"\n\n# Repository Context: {thread_info.owner}/{thread_info.repo}\n"
                        md_output += f"## Summary\n{summary}\n"
                        md_output += f"## Directory Structure\n```text\n{tree}\n```\n"
                        
                        if include_full_repo:
                            md_output += f"\n## Full Repository Content\n{content}\n"
                    
                    st.session_state['output'] = md_output
                    st.session_state['repo_name'] = thread_info.repo
                    st.session_state['number'] = thread_info.number
                    st.success("Ingestion complete!")
                    
                except Exception as e:
                    st.error(f"Error: {e}")

if 'output' in st.session_state:
    md_output = st.session_state['output']
    
    # Action Buttons on Top
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
            # Simple trick for copying in streamlit
            st.write(f'<script>navigator.clipboard.writeText({repr(md_output)});</script>', unsafe_allow_html=True)
            st.toast("Copied to clipboard!")

    st.subheader("Result")
    st.code(md_output, language="markdown")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #6b7280; font-size: 0.875rem;'>Inspired by <a href='https://gitingest.com' target='_blank'>gitingest</a></div>", unsafe_allow_html=True)