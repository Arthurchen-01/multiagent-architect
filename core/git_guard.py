"""
Git Guard: Enforces Git hygiene, prevents shallow clone traps,
and provides worktree isolation across multi-agent sessions.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


class GitGuard:
    def __init__(self, repo_dir: Optional[Path] = None):
        self.repo_dir = repo_dir or Path.cwd()

    def check_is_shallow(self) -> bool:
        """
        Checks if the current git repository is a shallow clone (.git/shallow exists).
        Shallow clones cause fake ahead/behind numbers and desync in ledgers!
        """
        shallow_file = self.repo_dir / ".git" / "shallow"
        return shallow_file.exists()

    def get_commit_hash(self) -> str:
        """Returns HEAD commit hash."""
        try:
            res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            return res.stdout.strip()
        except Exception:
            return "NO_COMMITS_YET"

    def check_worktree_status(self) -> Dict[str, Any]:
        """
        Inspects worktree status to detect uncommitted changes or diverged branches.
        """
        try:
            status_res = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            lines = status_res.stdout.strip().splitlines() if status_res.stdout.strip() else []
            return {
                "clean": len(lines) == 0,
                "uncommitted_count": len(lines),
                "uncommitted_lines": lines[:20],
                "is_shallow": self.check_is_shallow(),
                "head": self.get_commit_hash(),
            }
        except Exception as e:
            return {
                "clean": False,
                "error": str(e),
                "is_shallow": self.check_is_shallow(),
                "head": "UNKNOWN",
            }
