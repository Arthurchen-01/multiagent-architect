"""
Fleet Sync & Code Drift Detection
Compares files across nodes and environments via cryptographic SHA-256 hashes.
Prevents the classic bug where different nodes run divergent versions of code.
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Any


class FleetSync:
    @staticmethod
    def hash_file(file_path: Path) -> str:
        """Returns hex SHA-256 of file contents."""
        if not file_path.exists() or not file_path.is_file():
            return "FILE_NOT_FOUND"
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    @classmethod
    def compare_nodes(
        cls,
        files: List[Path],
        remote_node_hashes: Dict[str, Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Compares local file hashes with hashes from multiple remote nodes.
        remote_node_hashes format: { "server_name": { "filename": "sha256..." } }
        """
        local_hashes = {f.name: cls.hash_file(f) for f in files}
        drifts = []

        for server, srv_hashes in remote_node_hashes.items():
            for fname, local_sha in local_hashes.items():
                remote_sha = srv_hashes.get(fname)
                if not remote_sha:
                    drifts.append({
                        "server": server,
                        "file": fname,
                        "status": "MISSING_ON_REMOTE",
                        "local_sha": local_sha,
                        "remote_sha": None,
                    })
                elif remote_sha != local_sha:
                    drifts.append({
                        "server": server,
                        "file": fname,
                        "status": "HASH_MISMATCH",
                        "local_sha": local_sha,
                        "remote_sha": remote_sha,
                    })

        is_aligned = len(drifts) == 0
        return {
            "aligned": is_aligned,
            "drift_count": len(drifts),
            "drifts": drifts,
            "local_hashes": local_hashes,
        }
