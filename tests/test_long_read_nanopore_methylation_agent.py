"""
Automated Pytest Test Suite for Long Read Nanopore Methylation Agent.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main, _resolve_safe_path


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_input_validation_rejects_path_traversal():
    """Ensure path traversal attempts are rejected in input fields."""
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="../etc/passwd", target_identifier="KEY-01", primary_metric=10.0)
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="T1", target_identifier="/etc/passwd", primary_metric=10.0)
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=10.0, status_descriptor="..\\windows\\system32")


def test_input_validation_rejects_empty_strings():
    """Ensure empty or whitespace-only strings are rejected."""
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="   ", target_identifier="KEY-01", primary_metric=10.0)
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="T1", target_identifier="", primary_metric=10.0)


def test_input_validation_enforces_max_length():
    """Ensure string fields enforce maximum length constraints."""
    long_string = "A" * 200
    with pytest.raises(Exception):
        SystemTaskPayload(task_id=long_string, target_identifier="KEY-01", primary_metric=10.0)


def test_resolve_safe_path_rejects_traversal():
    """Ensure _resolve_safe_path rejects paths outside working directory."""
    with pytest.raises(ValueError):
        _resolve_safe_path("../etc/passwd")
    with pytest.raises(ValueError):
        _resolve_safe_path("/etc/passwd")


def test_resolve_safe_path_accepts_local():
    """Ensure _resolve_safe_path accepts paths within working directory."""
    result = _resolve_safe_path("sample.csv", must_exist=True)
    assert result.exists()


def test_audit_trail_generates_random_key_without_env():
    """Ensure AuditTrail generates a secure random key when AUDIT_SECRET_KEY is not set."""
    # Temporarily remove env var if present
    original = os.environ.pop("AUDIT_SECRET_KEY", None)
    try:
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            trail = AuditTrail()
            # Should have issued a warning about the random key
            assert any("AUDIT_SECRET_KEY" in str(warning.message) for warning in w)
        # Key should be set (random hex)
        assert len(trail.secret_key) > 0
    finally:
        if original is not None:
            os.environ["AUDIT_SECRET_KEY"] = original


def test_batch_cli_with_csv():
    """Test batch processing with a valid CSV file."""
    csv_content = "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\nTASK-B1,TARGET-B1,28.4,14.2,True,DISCORDANT\nTASK-B2,TARGET-B2,12.0,4.1,False,NOMINAL\n"
    # Create temp files inside the project directory so path validation passes
    project_dir = Path(__file__).parent.parent
    input_path = project_dir / "_test_batch_input.csv"
    output_path = project_dir / "_test_batch_output.csv"
    try:
        input_path.write_text(csv_content, encoding="utf-8")
        result = main(["batch", "-i", str(input_path), "-o", str(output_path)])
        assert result == 0
        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        assert "overall_urgency" in content
        assert "TASK-B1" in content
    finally:
        if input_path.exists():
            input_path.unlink()
        if output_path.exists():
            output_path.unlink()


def test_batch_cli_with_invalid_rows():
    """Test batch processing skips invalid rows gracefully."""
    csv_content = "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\nTASK-B1,TARGET-B1,not_a_number,14.2,True,DISCORDANT\nTASK-B2,TARGET-B2,12.0,4.1,False,NOMINAL\n"
    project_dir = Path(__file__).parent.parent
    input_path = project_dir / "_test_batch_input2.csv"
    output_path = project_dir / "_test_batch_output2.csv"
    try:
        input_path.write_text(csv_content, encoding="utf-8")
        result = main(["batch", "-i", str(input_path), "-o", str(output_path)])
        assert result == 0
        assert output_path.exists()
    finally:
        if input_path.exists():
            input_path.unlink()
        if output_path.exists():
            output_path.unlink()
