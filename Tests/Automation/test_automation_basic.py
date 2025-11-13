"""Basic workflow tests for HWP Automation API.

Based on Specs/AutomationMCP.idr formal specification.
"""

import pytest
from pathlib import Path
from src.automation.client import AutomationClient


class TestAutomationBasicWorkflow:
    """Test basic Automation API workflows."""

    @pytest.fixture
    def client(self):
        """Create automation client."""
        client = AutomationClient()
        yield client
        client.cleanup()

    def test_get_documents_collection(self, client):
        """Test getting documents collection."""
        result = client.get_documents()
        assert result.success, f"Failed to get documents: {result.error}"
        assert "count" in result.value

    def test_get_hwp_version(self, client):
        """Test getting HWP version property."""
        result = client.get_hwp_property("Version")
        assert result.success, f"Failed to get version: {result.error}"
        assert "Version" in result.value

    def test_get_hwp_is_empty(self, client):
        """Test getting IsEmpty property."""
        result = client.get_hwp_property("IsEmpty")
        assert result.success, f"Failed to get IsEmpty: {result.error}"
        assert "IsEmpty" in result.value

    def test_open_nonexistent_file(self, client):
        """Test opening non-existent file."""
        result = client.open_document("nonexistent.hwp")
        assert not result.success
        assert "not found" in result.error.lower() or "not exist" in result.error.lower()

    @pytest.mark.skipif(
        not Path("test_sample.hwp").exists(),
        reason="Requires test_sample.hwp file"
    )
    def test_open_and_get_properties(self, client):
        """Test opening document and getting properties."""
        # Open document
        result = client.open_document("test_sample.hwp")
        assert result.success, f"Failed to open document: {result.error}"

        doc = result.value.get("document")
        assert doc is not None

        # Get Path property
        path_result = client.get_document_property(doc, "Path")
        assert path_result.success, f"Failed to get Path: {path_result.error}"

        # Get IsModified property
        modified_result = client.get_document_property(doc, "IsModified")
        assert modified_result.success, f"Failed to get IsModified: {modified_result.error}"

        # Close document
        close_result = client.close_document(doc, save_changes=False)
        assert close_result.success, f"Failed to close document: {close_result.error}"

    def test_get_windows_collection(self, client):
        """Test getting windows collection."""
        result = client.get_windows()
        assert result.success, f"Failed to get windows: {result.error}"
        assert "count" in result.value
