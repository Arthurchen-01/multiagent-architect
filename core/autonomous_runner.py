"""
Autonomous Execution Engine (AutoRunner) for MultiAgent Architect
Enables autonomous step-by-step execution without manual copy-paste.
Features:
- State Machine persisted on disk (tasks/runner_state.json)
- Automatic step iteration [Step 1/N -> Step N/N]
- Autonomous self-healing loop via 156.225.28.106:7864 gateway when errors occur
- Resume capability: survives reboots, context resets, and disconnects
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

STATE_FILE = Path(__file__).parent.parent / "tasks" / "runner_state.json"
GATEWAY_URL = "http://156.225.28.106:7864/v1/chat/completions"


class AutonomousRunner:
    def __init__(self, task_name, steps=None):
        self.task_name = task_name
        self.state_file = STATE_FILE
        self.state = self.load_or_init_state(task_name, steps)

    def load_or_init_state(self, task_name, steps=None):
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("task_name") == task_name and data.get("status") != "COMPLETED":
                        print(f"[*] Resuming existing task state: {task_name} at step {data.get('current_step_index', 0) + 1}")
                        return data
            except Exception:
                pass

        # Initialize fresh state
        initial_state = {
            "task_name": task_name,
            "status": "RUNNING",
            "current_step_index": 0,
            "total_steps": len(steps) if steps else 0,
            "steps": [
                {
                    "index": i,
                    "name": s["name"],
                    "description": s.get("description", ""),
                    "status": "PENDING",
                    "retries": 0,
                    "output": None,
                    "error": None,
                    "started_at": None,
                    "completed_at": None
                }
                for i, s in enumerate(steps or [])
            ],
            "started_at": time.time(),
            "updated_at": time.time()
        }
        self.save_state(initial_state)
        return initial_state

    def save_state(self, state=None):
        if state:
            self.state = state
        self.state["updated_at"] = time.time()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def query_ai_for_remediation(self, step_name, error_msg, context=""):
        """Call wb2api gateway 7864 for self-healing repair instruction"""
        prompt = (
            f"You are the MultiAgent Architect autonomous remediation engine.\n"
            f"Task: {self.task_name}\n"
            f"Step: {step_name}\n"
            f"Error Encountered:\n{error_msg}\n"
            f"Context: {context}\n\n"
            f"Provide a concise JSON response with fix instruction:\n"
            f'{{"analysis": "brief reason", "remediation_command": "exact command to run", "retry_recommended": true}}'
        )
        try:
            req_data = json.dumps({
                "model": "deepseek-v4.1-flash",
                "messages": [
                    {"role": "system", "content": "You are a Linux and distributed systems repair engineer. Respond only with JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }).encode("utf-8")

            req = urllib.request.Request(
                GATEWAY_URL,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as res:
                body = json.loads(res.read().decode("utf-8"))
                content = body["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            return {"analysis": f"Gateway fallback: {e}", "remediation_command": None, "retry_recommended": False}

    def run_pipeline(self, step_handlers):
        """Execute each step in order, self-healing on failure, persisting state"""
        print("=" * 65)
        print(f" [AUTORUNNER] STARTING TASK: {self.task_name}")
        print(f" Total Steps: {len(self.state['steps'])}")
        print("=" * 65)

        start_idx = self.state["current_step_index"]
        for idx in range(start_idx, len(self.state["steps"])):
            step_record = self.state["steps"][idx]
            step_name = step_record["name"]
            handler = step_handlers.get(step_name)

            print(f"\n-> [{idx + 1}/{len(self.state['steps'])}] Executing Step: {step_name}")
            print(f"  Description: {step_record['description']}")

            step_record["status"] = "RUNNING"
            step_record["started_at"] = time.time()
            self.state["current_step_index"] = idx
            self.save_state()

            success = False
            max_retries = 3

            while not success and step_record["retries"] < max_retries:
                try:
                    # Run the actual step handler
                    result = handler(self)
                    step_record["output"] = str(result)
                    step_record["status"] = "SUCCESS"
                    step_record["completed_at"] = time.time()
                    success = True
                    print(f"  [OK] Step {idx + 1} ({step_name}) succeeded.")
                except Exception as e:
                    step_record["retries"] += 1
                    error_str = str(e)
                    step_record["error"] = error_str
                    print(f"  [FAIL] Step {idx + 1} failed on attempt {step_record['retries']}: {error_str}")

                    if step_record["retries"] < max_retries:
                        print("  [*] [SELF-HEALING] Querying 156.225.28.106:7864 for auto-remediation...")
                        fix = self.query_ai_for_remediation(step_name, error_str)
                        print(f"  [*] [DIAGNOSIS]: {fix.get('analysis', 'N/A')}")
                        time.sleep(2)
                    else:
                        step_record["status"] = "FAILED"
                        self.state["status"] = "BLOCKED"
                        self.save_state()
                        print(f"\n[!] Pipeline blocked at step {idx + 1} ({step_name}) after {max_retries} attempts.")
                        return False

            self.save_state()

        self.state["status"] = "COMPLETED"
        self.save_state()
        print("\n" + "=" * 65)
        print(f" [AUTORUNNER] ALL {len(self.state['steps'])} STEPS COMPLETED SUCCESSFULLY!")
        print(f" Persistent State Log: {self.state_file}")
        print("=" * 65)
        return True
