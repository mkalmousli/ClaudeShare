"""Guards for the project's hard rules, so they cannot silently regress."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERBATIM_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="main.js"></script>
</head>
</html>
"""
SOURCE_SUFFIXES = {".py", ".js", ".html", ".toml", ".yml", ".md", ".css", ".sh"}


def tracked() -> list[Path]:
    names = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.split()
    return [ROOT / n for n in names if (ROOT / n).is_file()]


def own_sources() -> list[Path]:
    return [p for p in tracked() if "vendor" not in p.parts and p.name != "uv.lock" and p.suffix in SOURCE_SUFFIXES | {""}]


def test_every_source_file_is_at_most_100_lines():
    long = [f"{p.relative_to(ROOT)} ({len(p.read_text().splitlines())})" for p in own_sources()
            if p.suffix in {".py", ".js"} or p.name in {"Dockerfile", "docker-compose.yml"}
            if len(p.read_text().splitlines()) > 100]
    assert not long, long


def test_no_shell_scripts_html_or_css_besides_index():
    files = tracked()
    assert not [p for p in files if p.suffix in {".sh", ".css"}]
    assert [p.relative_to(ROOT).as_posix() for p in files if p.suffix == ".html"] == ["frontend/index.html"]
    assert (ROOT / "frontend/index.html").read_text() == VERBATIM_HTML


def test_frontend_js_obeys_dom_and_style_rules():
    banned = {"innerHTML": r"innerHTML", "outerHTML": r"outerHTML", "insertAdjacentHTML": r"insertAdjacentHTML",
              "style tag": r"<style", "html string": r"<\w+[ >]", "min/max width": r"(min|max)-?[Ww]idth|(min|max)-?[Hh]eight",
              "hover css": r":hover", "css file": r"\.css\b"}
    hits = []
    for path in (ROOT / "frontend").rglob("*.js"):
        if "vendor" in path.parts:
            continue
        text = path.read_text()
        hits += [f"{path.name}: {why}" for why, pattern in banned.items() if re.search(pattern, text)]
    assert not hits, hits


def test_interactive_elements_disable_tap_highlight():
    widgets = (ROOT / "frontend/widgets.js").read_text()
    assert widgets.count('webkitTapHighlightColor = "transparent"') >= 2
