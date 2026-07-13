import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("graph", ROOT / "scripts" / "graph.py")
graph = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graph)

class GraphProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original_projects, self.original_work = graph.PROJECTS, graph.WORK
        graph.PROJECTS, graph.WORK = Path(self.temp.name) / "projects", Path(self.temp.name) / "work"
        graph.PROJECTS.mkdir()
    def tearDown(self):
        graph.PROJECTS, graph.WORK = self.original_projects, self.original_work
        self.temp.cleanup()
    def write_project(self, name, inventory):
        p = graph.PROJECTS / name; p.mkdir()
        (p / "project.yaml").write_text(f"schema_version: 1\nid: {name}\nname: Test\n")
        (p / "inventory.yaml").write_text(inventory)
    def test_valid_project(self):
        self.write_project("demo", "repos:\n  repo: {path: services/api}\nservices:\n  api: {repo: repo}\nedges: []\n")
        graph.validate("demo")
    def test_rejects_unsafe_and_unknown_references(self):
        self.write_project("bad", "repos:\n  repo: {path: ../secret}\nservices:\n  api: {repo: missing}\nedges:\n  - {from: api, to: absent, kind: http}\n")
        with self.assertRaises(ValueError) as error: graph.validate("bad")
        self.assertIn("unsafe path", str(error.exception)); self.assertIn("unknown repo", str(error.exception)); self.assertIn("unknown service", str(error.exception))
    def test_bundled_projects_validate(self):
        graph.PROJECTS, graph.WORK = self.original_projects, self.original_work
        graph.validate("example-platform"); graph.validate("sock-shop")
