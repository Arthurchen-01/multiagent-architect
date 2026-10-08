import os
import re

roots = ['D:\\']
local_git_repos = []

for root in roots:
    for dirpath, dirnames, filenames in os.walk(root):
        if '.git' in dirnames:
            git_dir = os.path.join(dirpath, '.git')
            config_file = os.path.join(git_dir, 'config')
            remote_url = None
            if os.path.isfile(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                        cfg = f.read()
                        m = re.search(r'url\s*=\s*(.+)', cfg)
                        if m:
                            remote_url = m.group(1).strip()
                except Exception:
                    pass
            local_git_repos.append((dirpath, remote_url))
            # Don't recurse into subdirectories of a git repo (unless submodule, but usually fine to skip)
            dirnames[:] = [d for d in dirnames if d != '.git']
        else:
            dirnames[:] = [d for d in dirnames if d not in ['node_modules', 'venv', '.venv', '$RECYCLE.BIN', 'AppData', '__pycache__']]

print(f"Total Local Git Repos Found: {len(local_git_repos)}")
with open(r'D:\multiagent-architect\scratch\all_local_git_repos.txt', 'w', encoding='utf-8') as out:
    for path, remote in sorted(local_git_repos, key=lambda x: str(x[1])):
        out.write(f"{remote} | {path}\n")

print("Saved to D:\\multiagent-architect\\scratch\\all_local_git_repos.txt")
