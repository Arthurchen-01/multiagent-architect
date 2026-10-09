"""
Unit test for Engineering Architect skill package (v0.1.0.0).
Verifies SKILL.md structure, engineering loop sections, asset templates, references, and validation runner.
"""

from pathlib import Path
import subprocess
import sys


def test_engineering_architect_skill_manifest():
    repo_root = Path(__file__).parent.parent
    skill_dir = repo_root / "skills" / "engineering-architect"
    assert skill_dir.exists(), f"Skill directory {skill_dir} must exist"

    skill_file = skill_dir / "SKILL.md"
    assert skill_file.exists(), "SKILL.md must exist in skills/engineering-architect"

    content = skill_file.read_text(encoding="utf-8")
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    assert "name: engineering-architect" in content
    assert "开工闸门" in content
    assert "规模路由" in content
    assert "三条腿核实" in content
    assert "换厂复核" in content
    assert "交付闸门" in content
    assert "五种工作模式" in content
    assert "反模式" in content
    assert "加载地图" in content
    assert "自检" in content


def test_engineering_architect_assets_and_references():
    repo_root = Path(__file__).parent.parent
    skill_dir = repo_root / "skills" / "engineering-architect"

    assets = [
        "decision-record-template.md",
        "pattern-card-template.md",
        "report-template.md",
        "trigger-eval.json",
    ]
    for a in assets:
        p = skill_dir / "assets" / a
        assert p.exists(), f"Asset {a} must exist in assets/"
        assert p.stat().st_size > 0, f"Asset {a} cannot be empty"

    references = [
        "coach-mode.md",
        "diagnosis-tree.md",
        "pattern-library.md",
        "project-memory.md",
        "sources.md",
    ]
    for r in references:
        p = skill_dir / "references" / r
        assert p.exists(), f"Reference {r} must exist in references/"
        assert p.stat().st_size > 0, f"Reference {r} cannot be empty"


def test_engineering_architect_validation_runner():
    repo_root = Path(__file__).parent.parent
    script_path = repo_root / "skills" / "engineering-architect" / "scripts" / "validate_skill.py"
    target_skill = repo_root / "skills" / "engineering-architect"

    assert script_path.exists(), "validate_skill.py must exist"

    proc = subprocess.run(
        [sys.executable, str(script_path), str(target_skill)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    assert proc.returncode == 0, f"validate_skill.py returned non-zero code {proc.returncode}\n{proc.stdout}\n{proc.stderr}"
    assert "FAIL=0" in proc.stdout, f"Expected 0 failures, got stdout:\n{proc.stdout}"
