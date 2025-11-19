"""
모든 HWP 프로세스 강제 종료
"""
import subprocess
import time

print("모든 HWP 프로세스 종료 중...")

# Windows taskkill 사용
subprocess.run(["taskkill", "/F", "/IM", "Hwp.exe"], capture_output=True)
subprocess.run(["taskkill", "/F", "/IM", "HwpApi.exe"], capture_output=True)

time.sleep(2)

# 확인
result = subprocess.run(["tasklist"], capture_output=True, text=True, encoding='cp949', errors='ignore')
hwp_count = result.stdout.lower().count('hwp.exe')

print(f"남은 HWP 프로세스: {hwp_count}개")

if hwp_count == 0:
    print("✓ 모든 HWP 프로세스 종료 완료!")
else:
    print(f"⚠️  아직 {hwp_count}개 프로세스가 남아있습니다")
