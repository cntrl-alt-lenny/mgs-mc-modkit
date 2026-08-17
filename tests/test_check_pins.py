"""The pin-freshness checker itself — it must never edit install.py, and it
must keep working if a repo name or version constant is refactored."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_pins                                        # noqa: E402
import install                                           # noqa: E402


def test_pins_read_from_install_not_hardcoded():
    """Every reported pin must come from install.py, so a bump can't drift."""
    rows = check_pins.pinned()
    by_repo = {r["repo"]: r["pin"] for r in rows}
    assert by_repo["ShizCalev/MGSHDFix"] == install.HDFIX_VERSION
    assert by_repo["nuggslet/MGSM2Fix"] == install.M2FIX_TAG
    assert (by_repo["ShizCalev/MGS2-Community-Bugfix-Compilation"]
            == install.GAMES["mgs2"]["bugfix_version"])
    assert (by_repo["ShizCalev/MGS3-Community-Bugfix-Compilation"]
            == install.GAMES["mgs3"]["bugfix_version"])


def test_every_pinned_repo_matches_its_download_url():
    """Guards against checking a repo we don't actually install from."""
    urls = " ".join([install.HDFIX_URL, install.M2FIX_URL,
                     install.GAMES["mgs2"]["bugfix_url"],
                     install.GAMES["mgs3"]["bugfix_url"]])
    for row in check_pins.pinned():
        assert row["repo"] in urls, row["repo"]


def test_tag_comparison_ignores_v_prefix():
    """Upstream is inconsistent: '3.6' vs 'v3.6' must not read as an update."""
    assert check_pins.norm("v3.6") == check_pins.norm("3.6")
    assert check_pins.norm("4.0.2") != check_pins.norm("3.1.0")


def test_reports_updates_without_touching_install_py(monkeypatch, tmp_path):
    before = Path(install.__file__).read_bytes()
    monkeypatch.setattr(check_pins, "latest_tag", lambda repo: "99.0.0")
    rows, errors = check_pins.check()
    assert errors == []
    assert all(r["outdated"] for r in rows)               # all look outdated
    assert Path(install.__file__).read_bytes() == before  # alert-only
    assert check_pins.main() == 1                         # exit 1 = update


def test_current_pins_report_clean(monkeypatch):
    monkeypatch.setattr(check_pins, "latest_tag",
                        lambda repo: {r["repo"]: r["pin"]
                                      for r in check_pins.pinned()}[repo])
    assert check_pins.main() == 0                         # exit 0 = current


def test_api_failure_is_never_mistaken_for_clean(monkeypatch):
    """A network failure must not silently read as 'all up to date'."""
    def boom(repo):
        raise TimeoutError("api down")
    monkeypatch.setattr(check_pins, "latest_tag", boom)
    rows, errors = check_pins.check()
    assert rows == [] and len(errors) == 4
    assert check_pins.main() == 2                         # exit 2 = check failed
