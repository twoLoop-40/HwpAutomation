"""
Test using EXACT pattern from test_merge_40_problems_clean.py
Just for 1 file to isolate the issue
"""
from pathlib import Path
import time
from src.automation.client import AutomationClient

# EXACT pattern from working test

# Client setup
target_client = AutomationClient()
source_client = AutomationClient()

target_hwp = target_client.hwp
source_hwp = source_client.hwp

# Security
target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
source_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# Hide windows
try:
    target_hwp.XHwpWindows.Item(0).Visible = False
    source_hwp.XHwpWindows.Item(0).Visible = False
except:
    pass

# Open template
template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
print(f'Opening template: {template_file}')
result = target_client.open_document(str(template_file))
print(f'Template open: {result.success}')
print(f'Template pages: {target_hwp.PageCount}')

target_hwp.SetPos(0, 0, 0)
time.sleep(0.1)

# Get first problem file
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
problem_file = [f for f in all_files if not f.name.startswith('[문항')][0]

print(f'\nProcessing file...')

# Open problem file
result = source_client.open_document(str(problem_file))
print(f'Problem open: {result.success}')
print(f'Problem pages: {source_hwp.PageCount}')

# Convert to 1 column
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
time.sleep(0.15)

print('Copied from source')

# Close source
source_hwp.Run("Cancel")
source_client.close_document()

print('Source closed')

# Paste
target_hwp.Run("Paste")
time.sleep(0.15)

print(f'Template pages after paste: {target_hwp.PageCount}')
print(f'SUCCESS!' if target_hwp.PageCount > 2 else 'FAILED - nothing pasted')

# Save
output = Path("test_exact_pattern_result.hwp")
target_hwp.SaveAs(str(output.absolute()))
print(f'Saved: {output} ({output.stat().st_size} bytes)')

# Cleanup
target_client.close_document()
source_client.cleanup()
target_client.cleanup()
