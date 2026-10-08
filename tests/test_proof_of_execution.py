"""
Unit tests for Proof of Execution Engine
"""

import tempfile
import hashlib
from pathlib import Path
from core.proof_of_execution import ProofValidator


def test_proof_validator_manifest():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        validator = ProofValidator(raw_data_dir=tmp_path / "raw", audit_dir=tmp_path / "audit")

        # Fake valid headers
        headers = {
            "cf-ray": "8c34f9a0b12-NRT",
            "date": "Wed, 07 Oct 2026 05:00:00 GMT",
            "etag": '"5d41402abc4b2a76b9719d911017c592"',
        }

        # Fake raw payload
        raw_payload = b"<html><head><title>Rakuten Live</title></head><body>Price: 5000</body></html>"

        # Fake snapshot file (with valid PNG header)
        snap_file = tmp_path / "screenshot.png"
        snap_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 3000)

        manifest = validator.build_proof_manifest(
            task_id="TASK-CRAWL-001",
            worker_node="huayu-1024",
            headers=headers,
            raw_payload=raw_payload,
            screenshot_path=snap_file,
        )

        assert manifest.headers_verified is True
        assert manifest.visual_snapshot_verified is True
        assert manifest.payload_sha256 == hashlib.sha256(raw_payload).hexdigest()

        # Audit file exists
        audit_file = tmp_path / "audit" / "PROOF_TASK-CRAWL-001.json"
        assert audit_file.exists()
