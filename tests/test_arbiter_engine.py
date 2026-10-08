"""
Unit tests for 3-Reviewer + 1-Arbiter Arbitration Engine
"""

import tempfile
from pathlib import Path
from core.arbiter_engine import ArbiterEngine, ReviewReport


def test_unanimous_approval():
    with tempfile.TemporaryDirectory() as tmp_dir:
        engine = ArbiterEngine(base_dir=Path(tmp_dir))

        # 3 Reviewers submit APPROVED
        engine.save_review(ReviewReport(
            reviewer_id="sec_guard",
            target_id="SPEC-001",
            verdict="APPROVED",
            score=95,
            signature="hash1",
        ))
        engine.save_review(ReviewReport(
            reviewer_id="perf_guru",
            target_id="SPEC-001",
            verdict="APPROVED",
            score=90,
            signature="hash2",
        ))
        engine.save_review(ReviewReport(
            reviewer_id="inv_checker",
            target_id="SPEC-001",
            verdict="APPROVED",
            score=98,
            signature="hash3",
        ))

        decision = engine.arbitrate("SPEC-001")
        assert decision.verdict == "APPROVED"
        assert decision.consensus_status == "UNANIMOUS"
        assert decision.final_score > 90.0


def test_rejection_by_blocking_issues():
    with tempfile.TemporaryDirectory() as tmp_dir:
        engine = ArbiterEngine(base_dir=Path(tmp_dir))

        # Security fails with a blocker
        engine.save_review(ReviewReport(
            reviewer_id="sec_guard",
            target_id="SPEC-002",
            verdict="REJECTED",
            score=30,
            blocking_issues=["SQL injection in raw query at line 55"],
            signature="hash1",
        ))
        engine.save_review(ReviewReport(
            reviewer_id="perf_guru",
            target_id="SPEC-002",
            verdict="APPROVED",
            score=90,
            signature="hash2",
        ))
        engine.save_review(ReviewReport(
            reviewer_id="inv_checker",
            target_id="SPEC-002",
            verdict="APPROVED",
            score=85,
            signature="hash3",
        ))

        decision = engine.arbitrate("SPEC-002")
        assert decision.verdict == "REJECTED"
        assert decision.consensus_status == "REJECTED_BY_BLOCKERS"
        assert len(decision.mandatory_remediation) == 1
