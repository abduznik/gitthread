import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class GitHubThread:
    owner: str
    repo: str
    type: str  # 'issues' or 'pull'
    number: int

def parse_github_url(url: str) -> Optional[GitHubThread]:
    # Pattern for GitHub Issues and Pull Requests
    pattern = r"github\.com/([^/]+)/([^/]+)/(issues|pull)/(\d+)"
    match = re.search(pattern, url)
    
    if match:
        return GitHubThread(
            owner=match.group(1),
            repo=match.group(2),
            type=match.group(3),
            number=int(match.group(4))
        )
    return None
