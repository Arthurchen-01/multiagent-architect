"""
Unit tests for Hierarchical Tree Topology & Skill Validation
Verifies L4 recursive task tree structure, YAML schema, and cascading roll-up mechanics.
"""

import tempfile
import yaml
from pathlib import Path
from core.state_machine import TaskManager, TaskState


def test_pipeline_yaml_l4_topology():
    repo_root = Path(__file__).parent.parent
    pipeline_file = repo_root / ".spec" / "pipeline.yaml"
    assert pipeline_file.exists(), "pipeline.yaml must exist"

    data = yaml.safe_load(pipeline_file.read_text(encoding="utf-8"))
    assert "topologies" in data, "topologies key must be in pipeline.yaml"
    topologies = data["topologies"]
    assert "L4_hierarchical_tree" in topologies, "L4_hierarchical_tree must be defined in topologies"

    l4 = topologies["L4_hierarchical_tree"]
    stages = l4.get("stages", [])
    assert len(stages) == 5, f"L4_hierarchical_tree must have 5 stages, found {len(stages)}"

    stage_ids = [s["id"] for s in stages]
    assert stage_ids == [
        "macro_spec",
        "department_delegation",
        "line_specialist_breakdown",
        "atomic_worker_execution",
        "cascading_verification",
    ]


def test_hierarchical_skill_frontmatter_and_sections():
    repo_root = Path(__file__).parent.parent
    skill_file = repo_root / "skills" / "hierarchical-tree-architect" / "SKILL.md"
    assert skill_file.exists(), "SKILL.md must exist in skills/hierarchical-tree-architect"

    content = skill_file.read_text(encoding="utf-8")
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    assert "name: hierarchical-tree-architect" in content
    assert "四层树状递归分解模型" in content
    assert "抽象屏障铁律" in content
    assert "父子工单命名与目录结构规范" in content
    assert "架构师执行三步法" in content


def test_hierarchical_rollup_execution_simulation():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tm = TaskManager(base_dir=Path(tmp_dir))

        # 1. Create Root Task
        root_id = "ROOT_SAMURAI_UPGRADE"
        tm.create_task(
            task_id=root_id,
            title="Samurai System 3-in-1 Architecture Upgrade",
            spec_id="SPEC-004",
            content="Top-level project upgrade integrating babra-copy, babra-samurai and data vault.",
        )

        # 2. Decompose into Departments
        dept_fe = "DEPT_FRONTEND"
        dept_data = "DEPT_DATA"
        tm.create_task(
            task_id=dept_fe,
            title="Frontend Department Integration",
            spec_id="SPEC-004-FE",
            content="Coordinate UI components and design token imports.",
            dependencies=[root_id],
        )
        tm.create_task(
            task_id=dept_data,
            title="Data Department Migration",
            spec_id="SPEC-004-DATA",
            content="Extract schema and read-only database connections.",
            dependencies=[root_id],
        )

        # 3. Decompose FE into Leaf Tasks
        leaf_1 = "LEAF_FE_TOKENS"
        leaf_2 = "LEAF_DATA_SCHEMA"
        tm.create_task(
            task_id=leaf_1,
            title="Import theme tokens",
            spec_id="SPEC-004-FE-01",
            content="Deploy design_tokens.json and theme.tokens.css.",
            dependencies=[dept_fe],
        )
        tm.create_task(
            task_id=leaf_2,
            title="Map Readonly Data Vault",
            spec_id="SPEC-004-DATA-01",
            content="Define AGENTS.md passport with 100% read-only policy.",
            dependencies=[dept_data],
        )

        # 4. Atomic Execution of Leaf Tasks
        c1 = tm.claim_task(worker_id="worker_01", task_id=leaf_1)
        assert c1 is not None
        tm.complete_task(
            worker_id="worker_01",
            task_id=leaf_1,
            test_result="PASS",
            changed_files=["src/theme/design_tokens.json"],
            code_hash_sha256="abc123hash",
        )

        c2 = tm.claim_task(worker_id="worker_02", task_id=leaf_2)
        assert c2 is not None
        tm.complete_task(
            worker_id="worker_02",
            task_id=leaf_2,
            test_result="PASS",
            changed_files=["AGENTS.md"],
            code_hash_sha256="def456hash",
        )

        # 5. Verify Leaf Tasks are in done directory
        done_files = [f.stem for f in tm.done_dir.glob("*.md")]
        assert leaf_1 in done_files
        assert leaf_2 in done_files

        # 6. Cascading Roll-up: when all leaves under dept are done, dept passes
        fe_leaves = [leaf_1]
        data_leaves = [leaf_2]
        fe_done = all(leaf in done_files for leaf in fe_leaves)
        data_done = all(leaf in done_files for leaf in data_leaves)
        assert fe_done is True
        assert data_done is True

        # Complete departments
        tm.claim_task(worker_id="lead_fe", task_id=dept_fe)
        tm.complete_task(
            worker_id="lead_fe",
            task_id=dept_fe,
            test_result="PASS",
            changed_files=["frontend_manifest.json"],
            code_hash_sha256="fe789hash",
        )

        tm.claim_task(worker_id="lead_data", task_id=dept_data)
        tm.complete_task(
            worker_id="lead_data",
            task_id=dept_data,
            test_result="PASS",
            changed_files=["data_manifest.json"],
            code_hash_sha256="data012hash",
        )

        # Complete root
        done_files = [f.stem for f in tm.done_dir.glob("*.md")]
        assert all(dept in done_files for dept in [dept_fe, dept_data])
        tm.claim_task(worker_id="chief_architect", task_id=root_id)
        tm.complete_task(
            worker_id="chief_architect",
            task_id=root_id,
            test_result="PASS",
            changed_files=["system_upgrade.manifest"],
            code_hash_sha256="root345hash",
        )

        done_files = [f.stem for f in tm.done_dir.glob("*.md")]
        assert root_id in done_files
