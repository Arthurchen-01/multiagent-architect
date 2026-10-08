import os
import re

def scan_dir(root, max_depth=3):
    repos = []
    root = os.path.abspath(root)
    root_sep_count = root.count(os.sep)

    for dirpath, dirnames, filenames in os.walk(root):
        cur_depth = dirpath.count(os.sep) - root_sep_count
        if cur_depth > max_depth:
            dirnames.clear()
            continue

        if '.git' in dirnames:
            config_file = os.path.join(dirpath, '.git', 'config')
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
            repos.append((dirpath, remote_url))
            dirnames.clear()
        else:
            dirnames[:] = [d for d in dirnames if d not in [
                'node_modules', 'venv', '.venv', '$RECYCLE.BIN', 'AppData', '__pycache__', 'dist', 'build'
            ]]

    return repos

all_repos = scan_dir('D:\\', max_depth=3)
print(f"Total Local Git Repos Found: {len(all_repos)}")
out_file = r'D:\multiagent-architect\scratch\fast_git_repos.txt'
with open(out_file, 'w', encoding='utf-8') as f:
    for path, remote in sorted(all_repos, key=lambda x: str(x[1])):
        f.write(f"{remote} | {path}\n")

print("Done! Check fast_git_repos.txt")
