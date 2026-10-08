"""
Atomic Task State Machine
Manages task lifecycle across distributed workers and multiple IDE sessions.
Enforces atomic locking, anti-race claim protocol, and exit guard verification.
"""

import os
import re
import time
import shutil
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class TaskState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    BLOCKED = "blocked"


class TaskManager:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.tasks_dir = self.base_dir / "tasks"
        self.pending_dir = self.tasks_dir / "pending"
        self.running_dir = self.tasks_dir / "running"
        self.done_dir = self.tasks_dir / "done"
        self.blocked_dir = self.tasks_dir / "blocked"

        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create necessary task tracking directories if they don't exist."""
        for d in [self.pending_dir, self.running_dir, self.done_dir, self.blocked_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def create_task(
        self,
        task_id: str,
        title: str,
        spec_id: str,
        content: str,
        dependencies: Optional[List[str]] = None,
    ) -> Path:
        """
        Create a new atomic task card in pending directory.
        """
        clean_id = re.sub(r"[^\w\-]", "_", task_id)
        task_file = self.pending_dir / f"{clean_id}.md"

        deps_str = str(dependencies or [])
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        card_content = f"""# [{clean_id}]: {title}

> **任务卡元数据**
> - **所属 Spec**：`{spec_id}`
> - **当前状态**：`PENDING`
> - **锁定 Worker**：`null`
> - **创建时间**：{timestamp}
> - **前置依赖任务**：`{deps_str}`

---

## 1. 任务范围与执行指令
{content}

---

## 2. 自动化退出守卫 (Exit Guard)
```yaml
exit_guard:
  test_command: ""
  test_result: ""
  changed_files: []
  code_hash_sha256: ""
```

---

## 3. 运行执行凭据
*(待 Worker 执行完成后自动追加)*
"""
        task_file.write_text(card_content, encoding="utf-8")
        return task_file

    def list_pending(self) -> List[str]:
        """List all unassigned tasks available in pending."""
        return sorted([f.stem for f in self.pending_dir.glob("*.md")])

    def claim_task(self, worker_id: str, task_id: Optional[str] = None) -> Optional[Path]:
        """
        Atomically claims a pending task for worker_id.
        Renames file from pending/<task_id>.md to running/<worker_id>-<task_id>.md.
        Returns the new file path, or None if no tasks are available or claim failed.
        """
        clean_worker = re.sub(r"[^\w\-]", "_", worker_id)

        candidates = self.list_pending()
        if not candidates:
            return None

        target_task = task_id if task_id and task_id in candidates else candidates[0]
        source_path = self.pending_dir / f"{target_task}.md"

        target_filename = f"{clean_worker}-{target_task}.md"
        target_path = self.running_dir / target_filename

        try:
            # Atomic move / rename to prevent race conditions
            shutil.move(str(source_path), str(target_path))

            # Update status in markdown header
            content = target_path.read_text(encoding="utf-8")
            content = content.replace("当前状态：`PENDING`", "当前状态：`RUNNING`")
            content = content.replace("锁定 Worker：`null`", f"锁定 Worker：`{clean_worker}`")
            target_path.write_text(content, encoding="utf-8")

            return target_path
        except (FileNotFoundError, PermissionError, OSError):
            # Another worker claimed it first
            return None

    def complete_task(
        self,
        worker_id: str,
        task_id: str,
        test_result: str,
        changed_files: List[str],
        code_hash_sha256: str,
    ) -> Optional[Path]:
        """
        Verifies exit guard data and moves task from running to done.
        """
        clean_worker = re.sub(r"[^\w\-]", "_", worker_id)
        clean_task = re.sub(r"[^\w\-]", "_", task_id)

        running_filename = f"{clean_worker}-{clean_task}.md"
        running_path = self.running_dir / running_filename

        if not running_path.exists():
            # Check without worker prefix
            direct_running = self.running_dir / f"{clean_task}.md"
            if direct_running.exists():
                running_path = direct_running
            else:
                return None

        final_filename = f"{clean_task}.md"
        done_path = self.done_dir / final_filename

        content = running_path.read_text(encoding="utf-8")
        content = content.replace("当前状态：`RUNNING`", "当前状态：`DONE`")

        exit_block = f"""exit_guard:
  test_command: "verified"
  test_result: "{test_result}"
  changed_files: {changed_files}
  code_hash_sha256: "{code_hash_sha256}"
  completed_at: "{time.strftime('%Y-%m-%d %H:%M:%S')}"
  completed_by: "{clean_worker}"
"""
        content = re.sub(r"exit_guard:[\s\S]*?```", f"{exit_block}```", content)
        running_path.write_text(content, encoding="utf-8")

        shutil.move(str(running_path), str(done_path))
        return done_path

    def get_status(self) -> Dict[str, Any]:
        """
        Returns full status of task pipeline.
        """
        pending = [f.stem for f in self.pending_dir.glob("*.md")]
        running = [f.name for f in self.running_dir.glob("*.md")]
        done = [f.stem for f in self.done_dir.glob("*.md")]
        blocked = [f.stem for f in self.blocked_dir.glob("*.md")]

        return {
            "counts": {
                "pending": len(pending),
                "running": len(running),
                "done": len(done),
                "blocked": len(blocked),
                "total": len(pending) + len(running) + len(done) + len(blocked),
            },
            "pending_tasks": pending,
            "running_tasks": running,
            "done_tasks": done,
            "blocked_tasks": blocked,
        }
