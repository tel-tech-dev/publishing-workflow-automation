import json
from pathlib import Path


def test_config_example_has_required_keys():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "config.example.json").read_text(encoding="utf-8"))
    required = {"workspace_dir", "issue_output_dir", "photo_archive_dir", "chromedriver_path", "openoffice_path"}
    assert required.issubset(data)
