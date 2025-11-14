"""Test processing a single file step by step"""
from pathlib import Path
import time
from src.automation.client import AutomationClient
from AppV1.column import convert_to_single_column
from AppV1.para_scanner import scan_paras, remove_empty_paras

# Create clients
target_client = AutomationClient()
source_client = AutomationClient()

target_hwp = target_client.hwp
source_hwp = source_client.hwp

# Register modules
target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
source_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# Test file
test_file = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905").glob("*.hwp")
test_file = [f for f in test_file if not f.name.startswith('[문항')][0]

print(f"Test file: {test_file.name}")
print(f"Exists: {test_file.exists()}")

# Step 1: Open
print("\nStep 1: Opening...")
result = source_client.open_document(str(test_file))
print(f"Open result: success={result.success}, error={result.error if not result.success else 'None'}")
print(f"PageCount after open: {source_hwp.PageCount}")

if source_hwp.PageCount < 1:
    print("FAIL: Empty document!")
    exit(1)

# Step 2: Convert to single column
print("\nStep 2: Converting to 1 column...")
convert_to_single_column(source_hwp)
print(f"PageCount after convert: {source_hwp.PageCount}")

# Step 3: Scan paras
print("\nStep 3: Scanning paras...")
paras = scan_paras(source_hwp)
print(f"Total paras: {len(paras)}")
print(f"Empty paras: {sum(1 for p in paras if p.is_empty)}")

# Step 4: Remove empty
print("\nStep 4: Removing empty paras...")
removed = remove_empty_paras(source_hwp, paras)
print(f"Removed: {removed}")

# Open template FIRST (before opening source)
print("\nStep 5a: Opening template FIRST...")
template = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
# Wait - template should be opened BEFORE processing source!
# Let me restructure...

# Actually, open template first, then process source
print("\nRestructuring: Opening template at start...")
template_result = target_client.open_document(str(template))
print(f"Template open: success={template_result.success}")
print(f"Template pages: {target_hwp.PageCount}")

# Step 5: Copy from source
print("\nStep 5: Copying from source...")
source_hwp.Run("MoveDocBegin")
source_hwp.Run("SelectAll")
source_hwp.Run("Copy")
time.sleep(0.2)

# Step 6: Paste to target
print("\nStep 6: Pasting to target...")
target_hwp.Run("MoveDocBegin")
target_hwp.Run("MoveParaBegin")
target_hwp.Run("Paste")
time.sleep(0.2)

print(f"Template pages after paste: {target_hwp.PageCount}")
print(f"SUCCESS: Content pasted!" if target_hwp.PageCount > 2 else "FAIL: Nothing pasted!")

# NOW close source
source_client.close_document()

# Cleanup
target_client.close_document()
source_client.cleanup()
target_client.cleanup()
