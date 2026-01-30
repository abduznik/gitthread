# gitthread

Ingest GitHub Issues and Pull Requests into LLM-friendly text dumps.

gitthread is a companion tool to gitingest that focuses on the conversational context of GitHub Issues and Pull Requests.

## Credits

This project is inspired by and uses the library from [gitingest](https://github.com/cyclotruc/gitingest). Special thanks to the gitingest team for their amazing work on codebase ingestion.

## Features

- Issue & PR Ingestion: Extract title, body, and all comments from any public GitHub issue or PR.
- Smart Linking: Automatically detects and ingests linked issues (e.g., #123 or "fixes #123") in PR descriptions.
- Repository Context: Integrates with gitingest to provide a summary of the repository structure.
- LLM-Friendly: Outputs clean Markdown formatted for easy consumption by LLMs.
- CLI & Web: Use it in your terminal or via a web interface.

## Installation

```bash
pip install gitthread
```

## Usage

### CLI

```bash
gitthread https://github.com/user/repo/issues/1
```

## License

MIT