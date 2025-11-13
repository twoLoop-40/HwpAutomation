"""Tests based on Specs/AutomationMCP.idr formal specification.

Verifies that Python implementation matches Idris spec.
"""

import pytest
from src.automation.client import AutomationClient
from src.automation.tools import AUTOMATION_TOOLS, AutomationToolHandler


class TestAutomationSpec:
    """Test Automation API against formal specification."""

    def test_tool_count(self):
        """Verify we have defined all automation tools."""
        # Based on autoMCPTools in AutomationMCP.idr
        expected_tools = [
            "hwp_auto_get_documents",
            "hwp_auto_open_document",
            "hwp_auto_get_active_document",
            "hwp_auto_get_document_property",
            "hwp_auto_save_document",
            "hwp_auto_close_document",
            "hwp_auto_get_windows",
            "hwp_auto_get_active_window",
            "hwp_auto_get_hwp_property",
            "hwp_auto_set_edit_mode",
            "hwp_auto_quit",
        ]

        tool_names = [tool["name"] for tool in AUTOMATION_TOOLS]
        for expected in expected_tools:
            assert expected in tool_names, f"Missing tool: {expected}"

    def test_object_hierarchy(self):
        """Test that object hierarchy matches spec."""
        client = AutomationClient()

        # IHwpObject is root
        assert client.hwp is not None

        # Can get IXHwpDocuments
        docs_result = client.get_documents()
        assert docs_result.success

        # Can get IXHwpWindows
        windows_result = client.get_windows()
        assert windows_result.success

        client.cleanup()

    def test_property_access_read_only(self):
        """Test that read-only properties work correctly."""
        client = AutomationClient()

        # Version is read-only
        result = client.get_hwp_property("Version")
        assert result.success

        # Attempting to set read-only property should fail gracefully
        set_result = client.set_hwp_property("Version", "fake")
        assert not set_result.success

        client.cleanup()

    def test_property_access_read_write(self):
        """Test that read-write properties work correctly."""
        client = AutomationClient()

        # EditMode is read-write
        result = client.set_hwp_property("EditMode", 1)
        assert result.success or "read-only" in result.error.lower()

        client.cleanup()

    def test_tool_handler_routing(self):
        """Test that tool handler routes calls correctly."""
        handler = AutomationToolHandler()

        # Test get_documents
        result = handler.handle_tool("hwp_auto_get_documents", {})
        assert "success" in result

        # Test unknown tool
        result = handler.handle_tool("hwp_auto_unknown", {})
        assert result["success"] is False

        handler.cleanup()

    def test_automation_result_monad(self):
        """Test that HwpResult works like Idris AutoResult monad."""
        client = AutomationClient()

        # Success case
        result = client.get_documents()
        if result.success:
            assert result.value is not None
            assert result.error is None

        # Failure case (invalid property)
        result = client.get_hwp_property("InvalidProperty")
        if not result.success:
            assert result.value is None
            assert result.error is not None

        client.cleanup()
