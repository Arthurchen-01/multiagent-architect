"""
Unit tests for Fleet Sync & Code Drift Detection
"""

import tempfile
from pathlib import Path
from core.fleet_sync import FleetSync


def test_fleet_sync_drift_detection():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Create local file
        server_py = tmp_path / "server.py"
        server_py.write_text("print('v1.7.15 with fresh gate')", encoding="utf-8")
        local_hash = FleetSync.hash_file(server_py)

        # 1. Aligned remote node
        aligned_nodes = {
            "node_1030A": {"server.py": local_hash},
            "node_1030B": {"server.py": local_hash},
        }
        res_aligned = FleetSync.compare_nodes([server_py], aligned_nodes)
        assert res_aligned["aligned"] is True
        assert res_aligned["drift_count"] == 0

        # 2. Drifting remote node (e.g. node 1011 running old code)
        drift_nodes = {
            "node_1030A": {"server.py": local_hash},
            "node_1011": {"server.py": "old_hash_outdated_version"},
        }
        res_drift = FleetSync.compare_nodes([server_py], drift_nodes)
        assert res_drift["aligned"] is False
        assert res_drift["drift_count"] == 1
        assert res_drift["drifts"][0]["server"] == "node_1011"
        assert res_drift["drifts"][0]["status"] == "HASH_MISMATCH"
