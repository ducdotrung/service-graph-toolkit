import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class DocumentationTests(unittest.TestCase):
    def test_readme_relative_links_exist(self):
        for target in re.findall(r"\[[^]]+\]\(([^)#]+)", (ROOT / "README.md").read_text()):
            if "://" not in target: self.assertTrue((ROOT / target).exists(), target)
    def test_projects_have_manifests(self):
        for p in (ROOT / "projects").iterdir():
            if p.is_dir(): self.assertTrue((p / "project.yaml").exists()); self.assertTrue((p / "inventory.yaml").exists())
