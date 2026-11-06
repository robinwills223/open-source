"""Markdown link and anchor verifier enforcing GitHub heading-slug rules.
Usage: python tools/check_links.py [directory_or_file]
Exit codes: 0 = valid, 1 = broken links.
"""
import re, sys
from pathlib import Path


def github_slug(text: str) -> str:
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    cleaned = re.sub(r"[`*_{}\[\]()#+!]", "", cleaned)
    cleaned = re.sub(r"[^\w\s-]", "", cleaned).strip().lower()
    return re.sub(r" ", "-", cleaned)


def extract_headings(file_path: Path) -> set[str]:
    if file_path.suffix.lower() != ".md" or not file_path.is_file():
        return set()
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    with open(file_path, "r", encoding="utf-8") as f:
        in_code = False
        for line in f:
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if not in_code and (m := re.match(r"^(#{1,6})\s+(.*)", line)):
                base = github_slug(m.group(2).strip())
                slug = base if counts.get(base, 0) == 0 else f"{base}-{counts[base]}"
                counts[base] = counts.get(base, 0) + 1
                slugs.add(slug)
                slugs.add(re.sub(r"-+", "-", slug))
    return slugs


def check_markdown_links(root_dir: Path) -> list[tuple[str, int, str, str]]:
    targets = []
    if (root_dir / "docs").is_dir():
        targets.extend((root_dir / "docs").glob("*.md"))
    if (root_dir / "AGENTS.md").is_file():
        targets.append(root_dir / "AGENTS.md")
    if (root_dir / "README.md").is_file():
        targets.append(root_dir / "README.md")

    headings = {p.resolve(): extract_headings(p) for p in targets}
    broken: list[tuple[str, int, str, str]] = []
    link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    for p in targets:
        with open(p, "r", encoding="utf-8") as f:
            in_code = False
            for line_no, line in enumerate(f, start=1):
                if line.strip().startswith("```"):
                    in_code = not in_code
                    continue
                if in_code:
                    continue
                for match in link_re.finditer(line):
                    t = match.group(2).strip()
                    if t.startswith(("http://", "https://", "mailto:", "file://", "ftp://")):
                        continue
                    parts = t.split("#", 1)
                    rel, anchor = parts[0], parts[1] if len(parts) > 1 else None
                    tgt_file = (p.parent / rel).resolve() if rel else p.resolve()
                    if not tgt_file.exists():
                        broken.append((str(p), line_no, t, f"File does not exist: {tgt_file}"))
                    elif anchor:
                        if tgt_file not in headings:
                            headings[tgt_file] = extract_headings(tgt_file)
                        if anchor not in headings[tgt_file]:
                            broken.append((str(p), line_no, t, f"Anchor #{anchor} not found in {tgt_file.name}"))
    return broken


def main() -> int:
    root = Path(__file__).resolve().parent.parent if len(sys.argv) < 2 else Path(sys.argv[1]).resolve()
    broken = check_markdown_links(root)
    if not broken:
        print(f"PASS: All markdown links and anchors in {root} are valid.")
        return 0
    print(f"FAIL: Found {len(broken)} broken link(s):")
    for f, line, t, r in broken:
        print(f"  {f}:{line}: '{t}' -> {r}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
