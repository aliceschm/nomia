import json

from typer.testing import CliRunner

import nomia.cli
from nomia.cli import app


runner = CliRunner()


FAILED_ISSUES = [
    {
        "type": "rule_removed",
        "rule_id": "commission.default",
    },
    {
        "type": "implementation_removed",
        "rule_id": "discount_eligibility",
        "function": "example_app.app.calculate_bonis",
    },
    {
        "type": "not_validated",
        "rule_id": "discount_eligibility",
        "function": "example_app.app.calculate_discount",
    },
]


def _stub_check(monkeypatch, issues):
    def fake_check(config_path=None, verbose=False):
        return issues

    monkeypatch.setattr(nomia.cli, "check", fake_check)


def test_check_default_format_failed_alignment(monkeypatch):
    _stub_check(monkeypatch, FAILED_ISSUES)

    result = runner.invoke(app, ["check"])

    assert result.exit_code == 0
    assert result.output == (
        "Alignment check failed\n"
        "\n"
        "3 items require review:\n"
        "  - Rule removed: commission.default\n"
        "  - Implementation removed: calculate_bonis\n"
        "  - Pending validation: calculate_discount\n"
        "\n"
        "Next step:\n"
        "  Review changes and run `nomia validate`.\n"
    )
    assert "implementation_removed" not in result.output
    assert "not_validated" not in result.output
    assert "rule_removed" not in result.output


def test_check_compact_format_failed_alignment(monkeypatch):
    _stub_check(monkeypatch, FAILED_ISSUES)

    result = runner.invoke(app, ["check", "--format", "compact"])

    assert result.exit_code == 0
    assert result.output == (
        "Alignment check failed: 3 items require review\n"
        "\n"
        "- Rule removed: commission.default\n"
        "- Implementation removed: calculate_bonis\n"
        "- Pending validation: calculate_discount\n"
    )


def test_check_detailed_format_failed_alignment(monkeypatch):
    _stub_check(monkeypatch, FAILED_ISSUES)

    result = runner.invoke(app, ["check", "--format", "detailed"])

    assert result.exit_code == 0
    assert "Alignment check failed" in result.output
    assert "Rule removed\n  Rule: commission.default" in result.output
    assert "Function: example_app.app.calculate_bonis" in result.output
    assert "Function: example_app.app.calculate_discount" in result.output
    assert "Meaning: This association has not been validated yet." in result.output
    assert "run `nomia validate` after confirming the alignment" in result.output


def test_check_json_format_failed_alignment(monkeypatch):
    _stub_check(monkeypatch, FAILED_ISSUES)

    result = runner.invoke(app, ["check", "--format", "json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "status": "failed",
        "issue_count": 3,
        "issues": FAILED_ISSUES,
    }


def test_check_strict_failed_alignment_exits_one(monkeypatch):
    _stub_check(monkeypatch, FAILED_ISSUES)

    result = runner.invoke(app, ["check", "--strict"])

    assert result.exit_code == 1
    assert "Alignment check failed" in result.output
    assert "3 items require review" in result.output


def test_check_strict_outputs_same_findings_as_default(monkeypatch):
    _stub_check(monkeypatch, FAILED_ISSUES)

    default_result = runner.invoke(app, ["check"])
    strict_result = runner.invoke(app, ["check", "--strict"])

    assert default_result.exit_code == 0
    assert strict_result.exit_code == 1
    assert strict_result.output == default_result.output


def test_check_successful_alignment_default_format(monkeypatch):
    _stub_check(monkeypatch, [])

    result = runner.invoke(app, ["check"])

    assert result.exit_code == 0
    assert result.output == "Nomia is up to date.\n"


def test_check_strict_successful_alignment_exits_zero(monkeypatch):
    _stub_check(monkeypatch, [])

    result = runner.invoke(app, ["check", "--strict"])

    assert result.exit_code == 0
    assert result.output == "Nomia is up to date.\n"


def test_check_successful_alignment_json_format(monkeypatch):
    _stub_check(monkeypatch, [])

    result = runner.invoke(app, ["check", "--format", "json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "status": "passed",
        "issue_count": 0,
        "issues": [],
    }


def test_check_invalid_format_argument(monkeypatch):
    _stub_check(monkeypatch, FAILED_ISSUES)

    result = runner.invoke(app, ["check", "--format", "xml"])

    assert result.exit_code != 0
    assert "Invalid value for '--format'" in result.output


def test_check_runtime_error_exits_two(monkeypatch):
    def fake_check(config_path=None, verbose=False):
        raise FileNotFoundError("No configuration file found.")

    monkeypatch.setattr(nomia.cli, "check", fake_check)

    result = runner.invoke(app, ["check"])

    assert result.exit_code == 2
    assert "Error: No configuration file found." in result.output
