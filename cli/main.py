"""
Command-line Interface for MultiAgent Architect
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state_machine import TaskManager
from core.arbiter_engine import ArbiterEngine, ReviewReport
from core.proof_of_execution import ProofValidator
from core.git_guard import GitGuard
from core.fleet_sync import FleetSync


def cmd_status(args):
    tm = TaskManager()
    status = tm.get_status()
    print("=" * 60)
    print(" [*] MULTIAGENT ARCHITECT - PIPELINE STATUS")
    print("=" * 60)
    counts = status["counts"]
    print(f"Total Tasks:   {counts['total']}")
    print(f"  [Pending]:   {counts['pending']}")
    print(f"  [Running]:   {counts['running']}")
    print(f"  [Done]:      {counts['done']}")
    print(f"  [Blocked]:   {counts['blocked']}")
    print("-" * 60)
    if status["running_tasks"]:
        print("Active Worker Locks (Running):")
        for t in status["running_tasks"]:
            print(f"  -> [RUNNING] {t}")
    else:
        print("No workers currently active.")
    if status["pending_tasks"]:
        print("Available in Queue (Pending):")
        for t in status["pending_tasks"][:5]:
            print(f"  -> [PENDING] {t}")
    print("=" * 60)


def cmd_claim(args):
    tm = TaskManager()
    claimed = tm.claim_task(args.worker_id, args.task_id)
    if claimed:
        print(f"[OK] Worker '{args.worker_id}' successfully claimed task: {claimed.name}")
    else:
        print(f"[FAIL] Failed to claim task. No tasks available or task already claimed.")


def cmd_complete(args):
    tm = TaskManager()
    done = tm.complete_task(
        worker_id=args.worker_id,
        task_id=args.task_id,
        test_result=args.test_result,
        changed_files=args.files.split(",") if args.files else [],
        code_hash_sha256=args.hash or "N/A",
    )
    if done:
        print(f"[DONE] Task '{args.task_id}' verified and moved to DONE: {done.name}")
    else:
        print(f"[FAIL] Failed to complete task '{args.task_id}'. Not found in running queue.")


def cmd_arbitrate(args):
    engine = ArbiterEngine()
    try:
        decision = engine.arbitrate(args.target_id)
        print("=" * 60)
        print(" [ARBITER] VERDICT REPORT")
        print("=" * 60)
        print(f"Target:       {decision.target_id}")
        print(f"Verdict:      {decision.verdict}")
        print(f"Score:        {decision.final_score}/100")
        print(f"Consensus:    {decision.consensus_status}")
        print(f"Reviewers:    {decision.reviewer_verdicts}")
        if decision.resolved_conflicts:
            print("Conflicts Resolved:")
            for c in decision.resolved_conflicts:
                print(f"  - {c}")
        if decision.mandatory_remediation:
            print("Mandatory Remediation Required:")
            for r in decision.mandatory_remediation:
                print(f"  - {r}")
        print(f"Signature:    {decision.signature}")
        print("=" * 60)
    except Exception as e:
        print(f"[ERROR] Arbitration error: {e}")


def cmd_git_check(args):
    guard = GitGuard()
    info = guard.check_worktree_status()
    print("=" * 60)
    print(" [GIT] REPOSITORY HYGIENE")
    print("=" * 60)
    print(f"Head Commit:    {info.get('head')}")
    print(f"Is Shallow:     {info.get('is_shallow')} (Warning if True!)")
    print(f"Worktree Clean: {info.get('clean')}")
    print(f"Dirty Files:    {info.get('uncommitted_count')}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="MultiAgent Architect CLI")
    subparsers = parser.add_subparsers(dest="command")

    # status
    p_status = subparsers.add_parser("status", help="Show task state machine status")
    p_status.set_defaults(func=cmd_status)

    # claim
    p_claim = subparsers.add_parser("claim", help="Atomically claim a task for a worker")
    p_claim.add_argument("worker_id", help="Worker ID (e.g. srv-1023, local-w1)")
    p_claim.add_argument("--task-id", dest="task_id", default=None, help="Specific task ID to claim")
    p_claim.set_defaults(func=cmd_claim)

    # complete
    p_comp = subparsers.add_parser("complete", help="Complete a task with exit guard data")
    p_comp.add_argument("worker_id", help="Worker ID")
    p_comp.add_argument("task_id", help="Task ID")
    p_comp.add_argument("--result", dest="test_result", default="PASS", help="Test execution result")
    p_comp.add_argument("--files", dest="files", default="", help="Comma-separated changed files")
    p_comp.add_argument("--hash", dest="hash", default="", help="SHA-256 hash of output")
    p_comp.set_defaults(func=cmd_complete)

    # arbitrate
    p_arb = subparsers.add_parser("arbitrate", help="Run 3-reviewer arbitration")
    p_arb.add_argument("target_id", help="Target spec/task ID")
    p_arb.set_defaults(func=cmd_arbitrate)

    # git-check
    p_git = subparsers.add_parser("git-check", help="Check git repository hygiene")
    p_git.set_defaults(func=cmd_git_check)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
