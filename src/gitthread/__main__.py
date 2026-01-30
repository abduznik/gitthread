import click
import os
from .parser import parse_github_url
from .ingestor import GHIngestor, format_thread_to_markdown
from gitingest import ingest
from dotenv import load_dotenv

load_dotenv()

@click.command()
@click.argument('url')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub Personal Access Token')
@click.option('--output', help='Output file path')
@click.option('--no-repo', is_flag=True, help='Do not include repository summary')
def main(url, token, output, no_repo):
    """gitthread: Ingest GitHub Issues and PRs for LLMs"""
    
    thread_info = parse_github_url(url)
    if not thread_info:
        click.echo(f"Error: Invalid GitHub Issue/PR URL: {url}", err=True)
        return

    ingestor = GHIngestor(token=token)
    
    click.echo(f"Ingesting thread: {url}...")
    try:
        data = ingestor.ingest_thread(thread_info)
    except Exception as e:
        click.echo(f"Error fetching thread: {e}", err=True)
        return

    md_output = format_thread_to_markdown(data)
    
    if not no_repo:
        repo_url = f"https://github.com/{thread_info.owner}/{thread_info.repo}"
        click.echo(f"Ingesting repository summary: {repo_url}...")
        try:
            # We only need the summary and tree for context
            summary, tree, _ = ingest(repo_url, token=token)
            
            repo_context = f"\n\n# Repository Context: {thread_info.owner}/{thread_info.repo}\n"
            repo_context += f"## Summary\n{summary}\n"
            repo_context += f"## Directory Structure\n```text\n{tree}\n```\n"
            
            md_output += repo_context
        except Exception as e:
            click.echo(f"Warning: Could not fetch repository summary: {e}", err=True)

    if output:
        with open(output, 'w') as f:
            f.write(md_output)
        click.echo(f"Output written to {output}")
    else:
        click.echo(md_output)

if __name__ == "__main__":
    main()