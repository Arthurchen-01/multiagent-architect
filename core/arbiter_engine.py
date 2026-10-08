"""
Arbiter Engine (3 Reviewers + 1 Arbiter)
Orchestrates multi-agent parallel audits, resolves conflicts, and generates
authoritative verdicts and dynamic next-stage task cards.
Pure standard library implementation (zero external dependency).
"""

import json
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


@dataclass
class ReviewReport:
    reviewer_id: str
    target_id: str
    verdict: str  # APPROVED or REJECTED
    score: int
    signature: str
    blocking_issues: List[str] = field(default_factory=list)
    advisory_notes: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ArbiterDecision:
    decision_id: str
    target_id: str
    verdict: str  # APPROVED, REJECTED, CONDITIONAL_PASS
    final_score: float
    consensus_status: str  # UNANIMOUS, SPLIT_RESOLVED, REJECTED_BY_BLOCKERS
    reviewer_verdicts: Dict[str, str]
    resolved_conflicts: List[str]
    mandatory_remediation: List[str]
    spawned_tasks: List[str]
    timestamp: str
    signature: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ArbiterEngine:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.reviews_dir = self.base_dir / "reviews"
        self.reviews_dir.mkdir(parents=True, exist_ok=True)

    def save_review(self, report: ReviewReport) -> Path:
        """Save an individual reviewer's report to the reviews directory."""
        file_path = self.reviews_dir / f"{report.target_id}_{report.reviewer_id}.json"
        file_path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return file_path

    def load_reviews_for_target(self, target_id: str) -> List[ReviewReport]:
        """Load all reviews submitted for a specific target_id."""
        reports = []
        for p in self.reviews_dir.glob(f"{target_id}_*.json"):
            if "ARBITER" in p.name:
                continue
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                reports.append(ReviewReport(
                    reviewer_id=data["reviewer_id"],
                    target_id=data["target_id"],
                    verdict=data["verdict"],
                    score=data["score"],
                    signature=data.get("signature", ""),
                    blocking_issues=data.get("blocking_issues", []),
                    advisory_notes=data.get("advisory_notes", []),
                    timestamp=data.get("timestamp", ""),
                ))
            except Exception:
                pass
        return reports

    def arbitrate(
        self,
        target_id: str,
        required_reviewers: Optional[List[str]] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> ArbiterDecision:
        """
        Executes arbitration over submitted reviews.
        Resolves conflicts between security, performance, and invariants.
        Emits ARBITER_DECISION.json.
        """
        if required_reviewers is None:
            required_reviewers = ["sec_guard", "perf_guru", "inv_checker"]

        if weights is None:
            # Default weights: Invariants 40%, Security 35%, Performance 25%
            weights = {
                "inv_checker": 0.40,
                "sec_guard": 0.35,
                "perf_guru": 0.25,
            }

        reviews = self.load_reviews_for_target(target_id)
        reviews_by_id = {r.reviewer_id: r for r in reviews}

        missing = [rid for rid in required_reviewers if rid not in reviews_by_id]
        if missing:
            raise ValueError(f"Cannot arbitrate {target_id}: Missing reviews from {missing}")

        all_blocking: List[str] = []
        reviewer_verdicts: Dict[str, str] = {}
        weighted_score: float = 0.0
        total_weight: float = sum(weights.get(rid, 1.0) for rid in required_reviewers)

        for rid in required_reviewers:
            r = reviews_by_id[rid]
            reviewer_verdicts[rid] = r.verdict
            w = weights.get(rid, 1.0)
            weighted_score += r.score * (w / total_weight)
            all_blocking.extend(r.blocking_issues)

        resolved_conflicts: List[str] = []
        verdicts_set = set(reviewer_verdicts.values())

        if "REJECTED" in verdicts_set and all_blocking:
            final_verdict = "REJECTED"
            consensus = "REJECTED_BY_BLOCKERS"
        elif len(verdicts_set) == 1 and "APPROVED" in verdicts_set:
            final_verdict = "APPROVED"
            consensus = "UNANIMOUS"
        else:
            if weighted_score >= 80.0:
                final_verdict = "APPROVED"
                consensus = "SPLIT_RESOLVED"
                resolved_conflicts.append(
                    f"Weighted score ({weighted_score:.1f} >= 80) passed despite minor dissent from {[k for k, v in reviewer_verdicts.items() if v == 'REJECTED']}"
                )
            else:
                final_verdict = "REJECTED"
                consensus = "SPLIT_RESOLVED"
                resolved_conflicts.append(
                    f"Weighted score ({weighted_score:.1f} < 80) insufficient to override rejection."
                )

        decision_id = f"ARB-{int(time.time())}-{target_id}"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        sig_data = f"{decision_id}|{final_verdict}|{weighted_score}|{timestamp}"
        signature = hashlib.sha256(sig_data.encode("utf-8")).hexdigest()

        decision = ArbiterDecision(
            decision_id=decision_id,
            target_id=target_id,
            verdict=final_verdict,
            final_score=round(weighted_score, 2),
            consensus_status=consensus,
            reviewer_verdicts=reviewer_verdicts,
            resolved_conflicts=resolved_conflicts,
            mandatory_remediation=all_blocking if final_verdict == "REJECTED" else [],
            spawned_tasks=[],
            timestamp=timestamp,
            signature=signature,
        )

        decision_file = self.reviews_dir / f"{target_id}_ARBITER_DECISION.json"
        decision_file.write_text(json.dumps(decision.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return decision
