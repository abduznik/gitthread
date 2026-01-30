import click

@click.command()
@click.argument('url', required=False)
def main(url):
    """gitthread: Ingest GitHub Issues and PRs for LLMs"""
    if not url:
        click.echo("Usage: gitthread <github-issue-or-pr-url>")
        return
    click.echo(f"Ingesting: {url} (Placeholder)")

if __name__ == "__main__":
    main()
