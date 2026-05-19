import importlib
import sys
import tempfile
import unittest
from pathlib import Path

from nomia.models import ISSUE_CODE_CHANGED, ISSUE_RULE_CONTENT_CHANGED
from nomia.services.checker import check
from nomia.services.validator import validate

sys.dont_write_bytecode = True


class RuleDriftTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.tempdir.name)
        self.package = self.project_root / "sample_app"
        self.package.mkdir()
        (self.package / "__init__.py").write_text("", encoding="utf-8")
        self.config_path = self.project_root / "nomia.yaml"

    def tearDown(self) -> None:
        self._forget_sample_modules()
        self.tempdir.cleanup()

    def _forget_sample_modules(self) -> None:
        importlib.invalidate_caches()

        for module_name in list(sys.modules):
            if module_name == "sample_app" or module_name.startswith("sample_app."):
                del sys.modules[module_name]

    def _write_app(self, expression: str) -> None:
        (self.package / "app.py").write_text(
            "\n".join(
                [
                    "from nomia import rule",
                    "",
                    "",
                    '@rule("discount.eligibility")',
                    "def is_eligible(customer):",
                    f"    return {expression}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        self._forget_sample_modules()

    def _write_config(self, rule_body: str) -> None:
        self.config_path.write_text(
            "\n".join(
                [
                    "sources:",
                    "  - sample_app",
                    "",
                    "rules:",
                    rule_body,
                    "",
                ]
            ),
            encoding="utf-8",
        )
        self._forget_sample_modules()

    def _validate(self) -> dict:
        return validate(config_path=str(self.config_path))

    def _check(self) -> list[dict]:
        return check(config_path=str(self.config_path))

    def test_no_changes_reports_up_to_date(self) -> None:
        self._write_app("customer.active")
        self._write_config(
            "\n".join(
                [
                    '  - id: discount.eligibility',
                    "    description: Customer must be active.",
                ]
            )
        )

        self._validate()

        self.assertEqual(self._check(), [])

    def test_changing_only_yaml_description_reports_rule_content_drift(self) -> None:
        self._write_app("customer.active")
        self._write_config(
            "\n".join(
                [
                    '  - id: discount.eligibility',
                    "    description: Customer must be active.",
                ]
            )
        )
        self._validate()

        self._write_config(
            "\n".join(
                [
                    '  - id: discount.eligibility',
                    "    description: Customer must be active and verified.",
                ]
            )
        )

        self.assertEqual(
            self._check(),
            [
                {
                    "type": ISSUE_RULE_CONTENT_CHANGED,
                    "rule_id": "discount.eligibility",
                    "message": "Rule content changed since last validation",
                }
            ],
        )

    def test_changing_only_implementation_reports_code_drift(self) -> None:
        self._write_app("customer.active")
        self._write_config(
            "\n".join(
                [
                    '  - id: discount.eligibility',
                    "    description: Customer must be active.",
                ]
            )
        )
        self._validate()

        self._write_app("customer.active and customer.verified")

        issues = self._check()

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["type"], ISSUE_CODE_CHANGED)
        self.assertEqual(issues[0]["rule_id"], "discount.eligibility")
        self.assertEqual(issues[0]["function"], "sample_app.app.is_eligible")

    def test_changing_unrelated_yaml_formatting_does_not_report_drift(self) -> None:
        self._write_app("customer.active")
        self._write_config(
            "\n".join(
                [
                    '  - id: discount.eligibility',
                    "    description: Customer must be active.",
                    "    severity: high",
                    "    tags:",
                    "      - billing",
                    "      - discount",
                ]
            )
        )
        self._validate()

        self._write_config(
            "\n".join(
                [
                    "  - tags: [billing, discount]",
                    "    severity: high",
                    "    description: >",
                    "      Customer must be active.",
                    '    id: "discount.eligibility"',
                ]
            )
        )

        self.assertEqual(self._check(), [])


if __name__ == "__main__":
    unittest.main()
