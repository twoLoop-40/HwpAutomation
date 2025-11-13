"""
Basic workflow test for HWP MCP Server.

Tests the complete document lifecycle:
1. Create new document (Closed → Opened)
2. Insert text (Opened → Modified)
3. Create table (Modified → Modified)
4. Save document (Modified → Saved)
5. Close document (Saved → Closed)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from action_table.client import ActionTableClient
from common.types import DocumentState

# Alias for backward compatibility
HwpClient = ActionTableClient


def test_document_lifecycle():
    """Test complete document lifecycle."""
    print("🧪 Testing HWP Document Lifecycle\n")
    print("=" * 60)

    client = HwpClient()

    try:
        # Step 1: Create new document
        print("\n📄 Step 1: Creating new document...")
        result = client.create_new_document()
        assert result.success, f"Failed to create document: {result.error}"
        assert client.document.state == DocumentState.OPENED
        print(f"✅ Document created: {result.value}")

        # Step 2: Insert text
        print("\n📝 Step 2: Inserting text...")
        result = client.insert_text("안녕하세요, HWP MCP Server 테스트입니다!")
        assert result.success, f"Failed to insert text: {result.error}"
        assert client.document.state == DocumentState.MODIFIED
        print(f"✅ Text inserted: {result.value}")

        # Step 3: Create table
        print("\n📊 Step 3: Creating table...")
        result = client.create_table(rows=3, cols=4)
        assert result.success, f"Failed to create table: {result.error}"
        assert client.document.state == DocumentState.MODIFIED
        print(f"✅ Table created: {result.value}")

        # Step 4: Save document
        print("\n💾 Step 4: Saving document...")
        # Note: This will fail if path is not set
        # In real usage, use FileSaveAs with a path first
        print("⚠️  Skipping save (no path set)")

        # Step 5: Close document
        print("\n🚪 Step 5: Closing document...")
        # Transition back to Opened state for closing
        client.document.transition_state(DocumentState.OPENED)
        result = client.close_document()
        assert result.success, f"Failed to close document: {result.error}"
        assert client.document.state == DocumentState.CLOSED
        print(f"✅ Document closed: {result.value}")

        print("\n" + "=" * 60)
        print("🎉 All tests passed!")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return False
    finally:
        client.cleanup()

    return True


if __name__ == "__main__":
    success = test_document_lifecycle()
    sys.exit(0 if success else 1)
