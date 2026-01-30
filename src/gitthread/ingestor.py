import os
from github import Github
from .parser import GitHubThread, parse_github_url
import re

class GHIngestor:
    def __init__(self, token: str = None):
        self.gh = Github(token) if token else Github()
        self.seen_threads = set()

    def ingest_thread(self, thread: GitHubThread, recursive: bool = True):
        repo = self.gh.get_repo(f"{thread.owner}/{thread.repo}")
        
        if thread.type == 'issues':
            item = repo.get_issue(number=thread.number)
            is_pr = False
        else:
            item = repo.get_pull(number=thread.number)
            is_pr = True

        data = {
            "title": item.title,
            "url": item.html_url,
            "author": item.user.login,
            "body": item.body,
            "created_at": item.created_at.isoformat(),
            "comments": [],
            "linked_issues": []
        }

        # Fetch comments
        comments = item.get_comments()
        for comment in comments:
            data["comments"].append({
                "author": comment.user.login,
                "body": comment.body,
                "created_at": comment.created_at.isoformat()
            })

        # Smart linking for PRs
        if recursive and item.body:
            linked = self.find_linked_issues(item.body, thread.owner, thread.repo)
            for l_thread in linked:
                thread_id = (l_thread.owner, l_thread.repo, l_thread.type, l_thread.number)
                if thread_id not in self.seen_threads:
                    self.seen_threads.add(thread_id)
                    data["linked_issues"].append(self.ingest_thread(l_thread, recursive=False))

        return data

    def find_linked_issues(self, text, owner, repo):
        # Look for #num or owner/repo#num
        found = []
        # Same repo #num
        matches = re.findall(r"(?:^|\s)#(\d+)", text)
        for m in matches:
            found.append(GitHubThread(owner=owner, repo=repo, type='issues', number=int(m)))
        
        # Cross repo owner/repo#num
        matches = re.findall(r"([a-zA-Z0-9._-]+)/([a-zA-Z0-9._-]+)#(\d+)", text)
        for o, r, n in matches:
            found.append(GitHubThread(owner=o, repo=r, type='issues', number=int(n)))
            
        return found

def format_thread_to_markdown(data):
    md = []
    md.append(f"# {data['title']}")
    md.append(f"**URL:** {data['url']}")
    md.append(f"**Author:** {data['author']}")
    md.append(f"**Date:** {data['created_at']}")
    md.append("\n## Description\n")
    md.append(data['body'] or "No description provided.")
    md.append("\n---\n")
    
    if data['comments']:
        md.append("## Conversation\n")
        for comment in data['comments']:
            md.append(f"### {comment['author']} commented on {comment['created_at']}")
            md.append(comment['body'])
            md.append("\n---\n")
            
    if data['linked_issues']:
        md.append("## Linked Issues\n")
        for linked in data['linked_issues']:
            md.append(f"### Linked: {linked['title']}")
            md.append(f"**URL:** {linked['url']}")
            md.append(linked['body'] or "")
            md.append("\n---\n")
            
    return "\n".join(md)
