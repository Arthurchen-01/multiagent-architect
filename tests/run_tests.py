import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import unittest

# Import test functions
from tests.test_state_machine import test_task_lifecycle_and_claim_lock
from tests.test_arbiter_engine import test_unanimous_approval, test_rejection_by_blocking_issues
from tests.test_proof_of_execution import test_proof_validator_manifest
from tests.test_fleet_sync import test_fleet_sync_drift_detection

class MultiAgentArchitectSuite(unittest.TestCase):
    def test_01_state_machine(self):
        test_task_lifecycle_and_claim_lock()

    def test_02_arbiter_approval(self):
        test_unanimous_approval()

    def test_03_arbiter_rejection(self):
        test_rejection_by_blocking_issues()

    def test_04_proof_of_execution(self):
        test_proof_validator_manifest()

    def test_05_fleet_sync(self):
        test_fleet_sync_drift_detection()

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(MultiAgentArchitectSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
