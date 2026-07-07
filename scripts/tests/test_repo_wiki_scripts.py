import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]


def run_script(script_name, *args, cwd=None):
    return subprocess.run(
        [sys.executable, str(SKILL_ROOT / "scripts" / script_name), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


class RepoWikiScriptsTest(unittest.TestCase):
    def test_init_repo_wiki_creates_default_layout(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = run_script("init_repo_wiki.py", str(root))

            self.assertEqual(result.returncode, 0, result.stderr)
            wiki = root / "wiki"
            self.assertTrue((wiki / "index.md").exists())
            self.assertTrue((wiki / "SCHEMA.md").exists())
            self.assertTrue((wiki / "overview.md").exists())
            self.assertTrue((wiki / "log.md").exists())
            self.assertTrue((wiki / "source-map.md").exists())
            for directory in ["components", "flows", "apis", "runbooks", "queries", "questions", "decisions"]:
                self.assertTrue((wiki / directory).is_dir())
            self.assertTrue((wiki / "apis" / "http-endpoints.md").exists())
            self.assertTrue((wiki / "components" / "config-and-cache.md").exists())
            self.assertTrue((wiki / "components" / "external-dependencies.md").exists())
            self.assertTrue((wiki / "flows" / "auth-and-identity.md").exists())
            self.assertTrue((wiki / "flows" / "business-flows.md").exists())
            self.assertTrue((wiki / "flows" / "field-propagation.md").exists())
            self.assertTrue((wiki / "flows" / "runtime-observability.md").exists())
            self.assertTrue((wiki / "runbooks" / "request-troubleshooting.md").exists())
            self.assertTrue((wiki / "questions" / "idl-source-location.md").exists())
            self.assertTrue((wiki / "questions" / "operations-metadata.md").exists())

    def test_init_system_wiki_creates_cross_repo_layout(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = run_script("init_repo_wiki.py", str(root), "--mode", "system")

            self.assertEqual(result.returncode, 0, result.stderr)
            wiki = root / "system-wiki"
            self.assertTrue((wiki / "index.md").exists())
            self.assertTrue((wiki / "service-catalog.md").exists())
            self.assertTrue((wiki / "dependency-graph.md").exists())
            self.assertTrue((wiki / "log.md").exists())
            for directory in ["repos", "contracts", "request-flows", "field-flows", "runbooks", "questions"]:
                self.assertTrue((wiki / directory).is_dir())

    def test_init_knowledge_repo_creates_repo_and_system_layout(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = run_script(
                "init_repo_wiki.py",
                str(root),
                "--mode",
                "knowledge",
                "--repo",
                "https://code.example.com/example/mock_feed_service",
                "--repo",
                "/opt/mock/repos/mock_shared_lib",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / "sources.yaml").exists())
            self.assertTrue((root / "repos" / "mock_feed_service" / "wiki" / "index.md").exists())
            self.assertTrue((root / "repos" / "mock_feed_service" / "wiki" / "apis" / "http-endpoints.md").exists())
            self.assertTrue((root / "repos" / "mock_feed_service" / "wiki" / "components" / "external-dependencies.md").exists())
            self.assertTrue((root / "repos" / "mock_feed_service" / "wiki" / "runbooks" / "request-troubleshooting.md").exists())
            self.assertTrue((root / "repos" / "mock_shared_lib" / "wiki" / "index.md").exists())
            self.assertTrue((root / "repos" / "mock_shared_lib" / "wiki" / "flows" / "auth-and-identity.md").exists())
            self.assertTrue((root / "repos" / "mock_shared_lib" / "wiki" / "flows" / "field-propagation.md").exists())
            self.assertTrue((root / "system" / "wiki" / "index.md").exists())
            self.assertTrue((root / "system" / "wiki" / "service-catalog.md").exists())
            self.assertIn("mock_feed_service", (root / "sources.yaml").read_text())
            self.assertIn("source_type: git", (root / "sources.yaml").read_text())
            self.assertIn("source_type: local", (root / "sources.yaml").read_text())

    def test_wiki_lint_reports_missing_source_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wiki = root / "docs" / "repo-wiki"
            (wiki / "components").mkdir(parents=True)
            (wiki / "index.md").write_text("- [Missing](components/missing.md)\n")
            (wiki / "components" / "missing.md").write_text(
                "---\n"
                "title: Missing\n"
                "type: component\n"
                "status: active\n"
                "source_files:\n"
                "  - src/missing.py\n"
                "---\n"
                "# Missing\n"
            )

            result = run_script("wiki_lint.py", str(wiki), cwd=root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("source file does not exist", result.stdout)
            self.assertIn("components/missing.md", result.stdout)

    def test_wiki_lint_passes_for_valid_minimal_wiki(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "service.py").write_text("def run():\n    return True\n")
            wiki = root / "docs" / "repo-wiki"
            (wiki / "components").mkdir(parents=True)
            (wiki / "index.md").write_text("- [Service](components/service.md)\n")
            (wiki / "components" / "service.md").write_text(
                "---\n"
                "title: Service\n"
                "type: component\n"
                "status: active\n"
                "source_files:\n"
                "  - src/service.py\n"
                "---\n"
                "# Service\n"
            )

            result = run_script("wiki_lint.py", str(wiki), cwd=root)

            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("0 issue", result.stdout)

    def test_wiki_lint_defaults_to_wiki_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wiki = root / "wiki"
            wiki.mkdir()
            (wiki / "index.md").write_text("# Index\n")

            result = run_script("wiki_lint.py", cwd=root)

            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("0 issue", result.stdout)

    def test_wiki_lint_quality_mode_reports_thin_api_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "handler.py").write_text("def handle():\n    return True\n")
            wiki = root / "docs" / "repo-wiki"
            (wiki / "apis").mkdir(parents=True)
            (wiki / "index.md").write_text("- [HTTP](apis/http.md)\n")
            (wiki / "apis" / "http.md").write_text(
                "---\n"
                "title: HTTP Endpoints\n"
                "type: api\n"
                "status: active\n"
                "source_files:\n"
                "  - src/handler.py\n"
                "---\n"
                "# HTTP Endpoints\n"
                "## Surface\n"
                "GET /v1/items\n"
            )

            result = run_script("wiki_lint.py", str(wiki), "--quality", cwd=root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("API reference is missing endpoint field table", result.stdout)
            self.assertIn("API reference is missing IDL source section", result.stdout)
            self.assertIn("API reference is missing request/response examples", result.stdout)

    def test_wiki_lint_quality_mode_does_not_require_signature_example(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "auth.py").write_text("def check_signature():\n    return True\n")
            wiki = root / "docs" / "repo-wiki"
            (wiki / "flows").mkdir(parents=True)
            (wiki / "index.md").write_text("- [Auth](flows/auth.md)\n")
            (wiki / "flows" / "auth.md").write_text(
                "---\n"
                "title: Signature Auth\n"
                "type: flow\n"
                "status: active\n"
                "source_files:\n"
                "  - src/auth.py\n"
                "tags:\n"
                "  - auth\n"
                "  - signature\n"
                "---\n"
                "# Signature Auth\n"
                "## Entry Points\n"
                "## Identity Sources\n"
                "The request signature is checked by middleware.\n"
                "## Failure Modes\n"
            )

            result = run_script("wiki_lint.py", str(wiki), "--quality", cwd=root)

            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertNotIn("signature page is missing executable signature example", result.stdout)

    def test_wiki_lint_quality_mode_reports_missing_operational_details(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "service.py").write_text("def serve():\n    return True\n")
            wiki = root / "docs" / "repo-wiki"
            (wiki / "runbooks").mkdir(parents=True)
            (wiki / "index.md").write_text("- [Ops](runbooks/ops.md)\n")
            (wiki / "runbooks" / "ops.md").write_text(
                "---\n"
                "title: Service Operations\n"
                "type: runbook\n"
                "status: active\n"
                "source_files:\n"
                "  - src/service.py\n"
                "---\n"
                "# Service Operations\n"
                "## Symptoms\n"
                "## Fast Checks\n"
                "## Logs And Metrics\n"
                "## Mitigations\n"
                "## Escalation\n"
            )

            result = run_script("wiki_lint.py", str(wiki), "--quality", cwd=root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("runbook is missing owners section", result.stdout)
            self.assertIn("runbook is missing metrics dashboards section", result.stdout)
            self.assertIn("runbook is missing alerts section", result.stdout)
            self.assertIn("runbook is missing common error logs section", result.stdout)

    def test_wiki_lint_quality_mode_reports_thin_field_propagation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "flow.py").write_text("def flow():\n    return True\n")
            wiki = root / "docs" / "repo-wiki"
            (wiki / "flows").mkdir(parents=True)
            (wiki / "index.md").write_text("- [Fields](flows/fields.md)\n")
            (wiki / "flows" / "fields.md").write_text(
                "---\n"
                "title: Field Propagation\n"
                "type: flow\n"
                "status: active\n"
                "source_files:\n"
                "  - src/flow.py\n"
                "tags:\n"
                "  - field-propagation\n"
                "---\n"
                "# Field Propagation\n"
            )

            result = run_script("wiki_lint.py", str(wiki), "--quality", cwd=root)

            self.assertEqual(result.returncode, 1)
            self.assertIn("field propagation page is missing field matrix section", result.stdout)
            self.assertIn("field propagation page is missing downstream request mapping section", result.stdout)

    def test_changed_files_maps_changed_sources_to_wiki_pages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wiki = root / "docs" / "repo-wiki"
            (wiki / "components").mkdir(parents=True)
            (wiki / "components" / "service.md").write_text(
                "---\n"
                "title: Service\n"
                "type: component\n"
                "status: active\n"
                "source_files:\n"
                "  - src/service.py\n"
                "---\n"
                "# Service\n"
            )

            result = run_script(
                "changed_files.py",
                "--wiki",
                str(wiki),
                "--changed",
                "src/service.py",
                "src/other.py",
                cwd=root,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["changed_files"], ["src/service.py", "src/other.py"])
            self.assertEqual(payload["affected_pages"], ["components/service.md"])
            self.assertEqual(payload["unmapped_changed_files"], ["src/other.py"])

    def test_changed_files_maps_related_files_for_karpathy_pages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wiki = root / "wiki"
            (wiki / "entities").mkdir(parents=True)
            (wiki / "entities" / "service.md").write_text(
                "---\n"
                "title: Service\n"
                "type: entity\n"
                "status: active\n"
                "related_files:\n"
                "  - src/service.py\n"
                "---\n"
                "# Service\n"
            )

            result = run_script(
                "changed_files.py",
                "--wiki",
                str(wiki),
                "--changed",
                "src/service.py",
                cwd=root,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["affected_pages"], ["entities/service.md"])
            self.assertEqual(payload["unmapped_changed_files"], [])

    def test_wiki_inventory_outputs_page_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wiki = root / "docs" / "repo-wiki"
            (wiki / "flows").mkdir(parents=True)
            (wiki / "flows" / "request.md").write_text(
                "---\n"
                "title: Request Flow\n"
                "type: flow\n"
                "status: active\n"
                "source_files:\n"
                "  - src/request.py\n"
                "tags:\n"
                "  - request\n"
                "---\n"
                "# Request Flow\n"
            )

            result = run_script("wiki_inventory.py", str(wiki))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["page_count"], 1)
            self.assertEqual(payload["pages"][0]["path"], "flows/request.md")
            self.assertEqual(payload["pages"][0]["title"], "Request Flow")
            self.assertEqual(payload["pages"][0]["source_files"], ["src/request.py"])


if __name__ == "__main__":
    unittest.main()
