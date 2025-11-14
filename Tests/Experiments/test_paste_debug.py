"""Debug clipboard issue"""
from pathlib import Path
import time
from src.automation.client import AutomationClient

# Create two clients
target_client = AutomationClient()
source_client = AutomationClient()

target_hwp = target_client.hwp
source_hwp = source_client.hwp

# Register modules
target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
source_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# Open a test file in source
test_file = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905/2023 학교별기출_확통_1학기_주교재_1학기중간_건국대사대부고_14_3_8.hwp")
print(f"Opening: {test_file.name}")
result = source_client.open_document(str(test_file))
print(f"Open result: {result.success}")

# Convert to single column
source_hwp.HAction.GetDefault("MultiColumn", source_hwp.HParameterSet.HColDef.HSet)
col_def = source_hwp.HParameterSet.HColDef
col_def.Count = 1
col_def.HSet.SetItem("ApplyClass", 832)
col_def.HSet.SetItem("ApplyTo", 6)
source_hwp.HAction.Execute("MultiColumn", col_def.HSet)
time.sleep(0.1)

# Copy
source_hwp.Run("MoveDocBegin")
source_hwp.Run("SelectAll")
source_hwp.Run("Copy")
time.sleep(0.2)

print("Content copied from source")

# Check source page count
source_pages = source_hwp.PageCount
print(f"Source pages: {source_pages}")

# Open template in target
template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
result = target_client.open_document(str(template_file))
print(f"Template open result: {result.success}")

# Check template initial pages
template_pages_initial = target_hwp.PageCount
print(f"Template initial pages: {template_pages_initial}")

# Move to body start
target_hwp.Run("MoveDocBegin")
time.sleep(0.05)
target_hwp.Run("MoveParaBegin")
time.sleep(0.05)

# Paste
print("Attempting paste...")
target_hwp.Run("Paste")
time.sleep(0.2)

# Check pages after paste
template_pages_after = target_hwp.PageCount
print(f"Template pages after paste: {template_pages_after}")
print(f"Pages increased: {template_pages_after > template_pages_initial}")

# Save for inspection
output = Path("test_paste_debug_result.hwp")
target_hwp.SaveAs(str(output.absolute()))
print(f"Saved to: {output}")
print(f"File size: {output.stat().st_size} bytes")

# Cleanup
source_client.close_document()
target_client.close_document()
source_client.cleanup()
target_client.cleanup()
