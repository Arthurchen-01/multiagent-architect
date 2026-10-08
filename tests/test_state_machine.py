"""
Unit tests for TaskManager State Machine & Atomic Locking
"""

import tempfile
import shutil
from pathlib import Path
from core.state_machine import TaskManager


def test_task_lifecycle_and_claim_lock():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tm = TaskManager(base_dir=Path(tmp_dir))

        # 1. Create task
        task_file = tm.create_task(
            task_id="TASK-001",
            title="Implement User Auth Schema",
            spec_id="SPEC-AUTH-001",
            content="Define User entity and DB migration.",
        )
        assert task_file.exists()
        assert tm.list_pending() == ["TASK-001"]

        # 2. Worker 1 claims task
        claimed_path = tm.claim_task(worker_id="worker_alpha", task_id="TASK-001")
        assert claimed_path is not None
        assert claimed_path.name == "worker_alpha-TASK-001.md"
        assert claimed_path.exists()
        assert not task_file.exists()  # Pending file was atomically renamed
        assert tm.list_pending() == []

        # 3. Worker 2 attempts to claim the same task -> should fail (return None)
        collision_claim = tm.claim_task(worker_id="worker_beta", task_id="TASK-001")
        assert collision_claim is None

        # 4. Worker 1 completes the task with Exit Guard data
        done_path = tm.complete_task(
            worker_id="worker_alpha",
            task_id="TASK-001",
            test_result="PASS (4 tests passed)",
            changed_files=["src/auth.ts", "tests/auth.test.ts"],
            code_hash_sha256="abc123def456",
        )
        assert done_path is not None
        assert done_path.exists()
        assert done_path.name == "TASK-001.md"
        assert not claimed_path.exists()

        status = tm.get_status()
        assert status["counts"]["pending"] == 0
        assert status["counts"]["running"] == 0
        assert status["counts"]["done"] == 1
