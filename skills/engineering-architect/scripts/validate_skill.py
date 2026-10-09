#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_skill.py — 校验一个 Agent Skills 技能包是否符合开放标准，并扫一遍指纹泄漏。

只读、不联网、只用标准库。

用法：
    python scripts/validate_skill.py [技能目录]
    （不传参数时，默认校验本脚本所在的那个技能目录）

退出码：
    0 = 没有 FAIL（可能有 WARN）
    1 = 存在 FAIL

依据：https://agentskills.io/specification  +  Claude 官方 Skill authoring best practices
"""

from __future__ import annotations

import os
import re
import sys

# ---------------------------------------------------------------- 常量

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
XML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
INTERNAL_PATH_RE = re.compile(r"(?:references|assets|scripts)/[^\s`)\]\u3002\uff0c\u3001\"']+")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")

MAX_NAME = 64
MAX_DESC = 1024
MAX_BODY_LINES = 500
BODY_WARN_LINES = 420

# 指纹扫描：跳过 scripts/ 目录（脚本本身要写正则，会自伤）
FINGERPRINT_SKIP_DIRS = {"scripts"}

FINGERPRINT_PATTERNS = [
    ("公网/内网 IPv4", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "FAIL"),
    ("Windows 绝对路径", re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/]"), "FAIL"),
    ("用户目录路径", re.compile(r"[A-Za-z]:[\\/]Users[\\/]", re.IGNORECASE), "FAIL"),
    ("MAC 地址", re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"), "FAIL"),
    (
        "疑似凭据",
        re.compile(
            r"(ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}"
            r"|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
        ),
        "FAIL",
    ),
]

IP_ALLOWLIST = {"127.0.0.1", "0.0.0.0", "255.255.255.255"}


def is_private_ip(text: str) -> bool:
    parts = text.split(".")
    if len(parts) != 4:
        return False
    try:
        octets = [int(p) for p in parts]
    except ValueError:
        return False
    if any(o > 255 for o in octets):
        return False
    a, b = octets[0], octets[1]
    if a == 10:
        return True
    if a == 192 and b == 168:
        return True
    if a == 172 and 16 <= b <= 31:
        return True
    if a == 169 and b == 254:
        return True
    return False


# ---------------------------------------------------------------- 报告

class Report:
    def __init__(self) -> None:
        self.fails: list[str] = []
        self.warns: list[str] = []
        self.oks: list[str] = []

    def fail(self, msg: str) -> None:
        self.fails.append(msg)

    def warn(self, msg: str) -> None:
        self.warns.append(msg)

    def ok(self, msg: str) -> None:
        self.oks.append(msg)

    def dump(self) -> int:
        for m in self.oks:
            print("  OK   " + m)
        for m in self.warns:
            print("  WARN " + m)
        for m in self.fails:
            print("  FAIL " + m)
        print("-" * 68)
        print(
            "结果：OK=%d  WARN=%d  FAIL=%d"
            % (len(self.oks), len(self.warns), len(self.fails))
        )
        if self.fails:
            print("校验未通过。")
            return 1
        print("校验通过。")
        return 0


# ---------------------------------------------------------------- 解析

def split_frontmatter(text: str) -> tuple[str, str, int]:
    """返回 (frontmatter, body, body_start_line)。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return "", text, 1
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return "", text, 1
    fm = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:])
    return fm, body, end + 2


def parse_simple_yaml(fm: str) -> dict:
    """只支持本 skill 用得到的子集：key: value、折叠标量 > 与 |。"""
    out: dict = {}
    lines = fm.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_.-]+):\s*(.*)$", raw)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", "|", ">-", "|-", ">+", "|+"):
            block: list[str] = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt.strip() and not nxt.startswith((" ", "\t")):
                    break
                block.append(nxt.strip())
                i += 1
            if val.startswith("|"):
                out[key] = "\n".join(block).strip()
            else:
                out[key] = " ".join(x for x in block if x).strip()
            continue
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        out[key] = val
        i += 1
    return out


def iter_text_files(skill_dir: str):
    for root, dirs, files in os.walk(skill_dir):
        rel_root = os.path.relpath(root, skill_dir)
        parts = [] if rel_root == "." else rel_root.split(os.sep)
        if parts and parts[0] in FINGERPRINT_SKIP_DIRS:
            continue
        dirs[:] = [d for d in dirs if not (not parts and d in FINGERPRINT_SKIP_DIRS)]
        for f in sorted(files):
            if f.lower().endswith((".md", ".txt", ".json", ".yaml", ".yml")):
                yield os.path.join(root, f)


def rel(skill_dir: str, path: str) -> str:
    return os.path.relpath(path, skill_dir).replace(os.sep, "/")


# ---------------------------------------------------------------- 各检查

def check_frontmatter(skill_dir: str, text: str, rep: Report) -> dict:
    fm, body, body_start = split_frontmatter(text)
    if not fm:
        rep.fail("SKILL.md 缺少 YAML frontmatter（文件必须以 --- 开头并有结束 ---）")
        return {}
    data = parse_simple_yaml(fm)

    name = str(data.get("name", "")).strip()
    if not name:
        rep.fail("frontmatter 缺 name")
    else:
        if len(name) > MAX_NAME:
            rep.fail("name 超过 %d 字符：%d" % (MAX_NAME, len(name)))
        if not NAME_RE.match(name):
            rep.fail("name 只能用小写字母/数字/连字符，且不能以连字符开头结尾、不能连续连字符：%r" % name)
        dir_name = os.path.basename(os.path.normpath(skill_dir))
        if name != dir_name:
            rep.fail("name(%r) 必须与所在目录名(%r)一致" % (name, dir_name))
        if NAME_RE.match(name) and name == dir_name:
            rep.ok("name 合法且与目录同名：%s" % name)

    desc = str(data.get("description", "")).strip()
    if not desc:
        rep.fail("frontmatter 缺 description")
    else:
        if len(desc) > MAX_DESC:
            rep.fail("description 超过 %d 字符：%d" % (MAX_DESC, len(desc)))
        if XML_TAG_RE.search(desc):
            rep.fail("description 里含 XML 标签")
        if len(desc) < 60:
            rep.warn("description 偏短（%d 字符），可能触发不稳" % len(desc))
        if not desc:
            rep.fail("description 为空")
        if len(desc) <= MAX_DESC and not XML_TAG_RE.search(desc):
            rep.ok("description 合法：%d 字符" % len(desc))

    body_lines = len([l for l in body.splitlines() if l.strip()])
    if body_lines > MAX_BODY_LINES:
        rep.fail("SKILL.md 正文 %d 行，超过 %d 行上限，应拆到 references/" % (body_lines, MAX_BODY_LINES))
    elif body_lines > BODY_WARN_LINES:
        rep.warn("SKILL.md 正文 %d 行，接近 %d 行上限" % (body_lines, MAX_BODY_LINES))
    else:
        rep.ok("SKILL.md 正文 %d 行（上限 %d）" % (body_lines, MAX_BODY_LINES))

    return {"data": data, "body": body, "body_start": body_start, "body_lines": body_lines}


def extract_internal_refs(text: str) -> set[str]:
    refs = set()
    for m in INTERNAL_PATH_RE.finditer(text):
        refs.add(m.group(0).rstrip("/"))
    for m in MD_LINK_RE.finditer(text):
        target = m.group(1).strip()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        refs.add(target.lstrip("./"))
    return refs


def check_references(skill_dir: str, parsed: dict, rep: Report) -> None:
    if not parsed:
        return
    body = parsed["body"]
    refs = extract_internal_refs(body)

    missing = []
    for r in sorted(refs):
        if r.endswith("/"):
            continue
        p = os.path.join(skill_dir, r.replace("/", os.sep))
        if not os.path.exists(p):
            missing.append(r)
    if missing:
        for r in missing:
            rep.fail("SKILL.md 引用了不存在的文件：%s" % r)
    else:
        rep.ok("SKILL.md 引用的文件全部存在（%d 个）" % len(refs))

    # 每个技能内文件都要能从 SKILL.md 直接指到（一层深）
    all_files = []
    for sub in ("references", "assets", "scripts"):
        d = os.path.join(skill_dir, sub)
        if os.path.isdir(d):
            for root, _dirs, files in os.walk(d):
                for f in files:
                    all_files.append(rel(skill_dir, os.path.join(root, f)))

    reachable = {r.rstrip("/") for r in refs}
    orphans = [f for f in all_files if f not in reachable]
    if orphans:
        for f in orphans:
            rep.warn("文件没有被 SKILL.md 直接引用（渐进式披露要求一层深）：%s" % f)
    else:
        rep.ok("所有技能内文件都能从 SKILL.md 一层直达")

    # 反向检查：references/ 里再指向别的技能文件 = 链条变深
    nested = []
    for f in all_files:
        if not f.endswith((".md", ".txt")):
            continue
        p = os.path.join(skill_dir, f.replace("/", os.sep))
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except OSError:
            continue
        for r in extract_internal_refs(content):
            if r.rstrip("/") in all_files and r.rstrip("/") != f:
                nested.append("%s → %s" % (f, r))
    for n in sorted(set(nested)):
        rep.warn("交叉引用（链条变深，SKILL.md 已能直达，可接受但要留意）：%s" % n)


def check_fingerprints(skill_dir: str, rep: Report) -> None:
    findings: list[str] = []
    for path in iter_text_files(skill_dir):
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        for idx, line in enumerate(lines, 1):
            for label, pattern, level in FINGERPRINT_PATTERNS:
                for m in pattern.finditer(line):
                    hit = m.group(0)
                    if label == "公网/内网 IPv4":
                        if hit in IP_ALLOWLIST:
                            continue
                        if not is_private_ip(hit):
                            continue  # 公网 IP 只提醒
                        level = "FAIL"
                    masked = hit if len(hit) <= 6 else hit[:4] + "***"
                    findings.append(
                        "%s [%s] %s:%d  %s" % (level, label, rel(skill_dir, path), idx, masked)
                    )
    if findings:
        for f in findings:
            if f.startswith("FAIL"):
                rep.fail("指纹泄漏 → " + f[5:])
            else:
                rep.warn("疑似指纹 → " + f[5:])
    else:
        rep.ok("指纹扫描：干净（无 IP / 绝对路径 / MAC / 凭据）")


def check_assets_json(skill_dir: str, rep: Report) -> None:
    import json

    d = os.path.join(skill_dir, "assets")
    if not os.path.isdir(d):
        return
    bad = []
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            p = os.path.join(d, f)
            try:
                with open(p, encoding="utf-8") as fh:
                    json.load(fh)
            except Exception as exc:  # noqa: BLE001
                bad.append("%s (%s)" % (f, exc))
    if bad:
        for b in bad:
            rep.fail("JSON 资源无法解析：%s" % b)
    else:
        rep.ok("assets 下的 JSON 资源全部可解析")


# ---------------------------------------------------------------- main

def main(argv: list[str]) -> int:
    if len(argv) > 1:
        skill_dir = os.path.abspath(argv[1])
    else:
        skill_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

    print("校验技能包：%s" % os.path.basename(os.path.normpath(skill_dir)))
    print("-" * 68)

    rep = Report()
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        rep.fail("找不到 SKILL.md")
        return rep.dump()

    with open(skill_md, encoding="utf-8", errors="replace") as fh:
        text = fh.read()

    parsed = check_frontmatter(skill_dir, text, rep)
    check_references(skill_dir, parsed, rep)
    check_assets_json(skill_dir, rep)
    check_fingerprints(skill_dir, rep)
    return rep.dump()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
