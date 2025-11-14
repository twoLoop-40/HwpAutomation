"""Test if clipboard works between two HWP COM instances"""
import win32com.client
import time

# Test clipboard sharing between two HWP instances
hwp1 = win32com.client.Dispatch('HWPFrame.HwpObject')
hwp2 = win32com.client.Dispatch('HWPFrame.HwpObject')

hwp1.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
hwp2.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')

# Insert text in hwp1
hwp1.HAction.GetDefault('InsertText', hwp1.HParameterSet.HInsertText.HSet)
hwp1.HParameterSet.HInsertText.Text = 'Test from HWP1'
hwp1.HAction.Execute('InsertText', hwp1.HParameterSet.HInsertText.HSet)
time.sleep(0.1)

# Copy from hwp1
hwp1.Run('SelectAll')
time.sleep(0.05)
hwp1.Run('Copy')
time.sleep(0.2)

# Try paste in hwp2
hwp2.Run('Paste')
time.sleep(0.2)

# Check if paste worked
hwp1_text = hwp1.GetText()
hwp2_text = hwp2.GetText()

print(f'HWP1 text: [{hwp1_text}]')
print(f'HWP2 text: [{hwp2_text}]')
print(f'Clipboard shared: {hwp2_text == hwp1_text}')

hwp1.Quit()
hwp2.Quit()
