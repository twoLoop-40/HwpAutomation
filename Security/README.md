# HWP 보안 모듈 설정 가이드

## 문제 상황

한글 오토메이션(Automation API)을 사용할 때 로컬 파일에 접근하거나 저장하려고 하면 **보안 승인 메시지**가 나타납니다. 이 메시지는 사용자의 수동 승인을 요구하므로 자동화 스크립트가 중단됩니다.

### 증상
- 파일 삽입 시 보안 승인 창이 표시됨
- 파일 저장 시 보안 승인 요청
- 자동화 스크립트가 승인 대기 상태에서 멈춤
- **결과 파일이 생성되지만 내용이 비어있음**

## 해결 방법: 보안 모듈 등록

`FilePathCheckerModuleExample.dll`을 등록하면 보안 승인 메시지를 우회할 수 있습니다.

---

## 설정 방법

### 방법 1: 코드에서 직접 등록 (권장)

Python 코드에서 `RegisterModule()`을 호출하여 등록:

```python
from pathlib import Path
from src.automation.client import AutomationClient

client = AutomationClient()

# 보안 모듈 경로
security_dll = Path(__file__).parent / "Security" / "FilePathCheckerModuleExample.dll"

# 보안 모듈 등록
result = client.register_security_module(str(security_dll))
if result.success:
    print(f"✅ 보안 모듈 등록 완료: {result.value['path']}")
else:
    print(f"❌ 보안 모듈 등록 실패: {result.error}")

# 이제 파일 작업 수행
# ...
```

**장점**:
- 레지스트리 수정 불필요
- 스크립트 실행 시마다 자동 등록
- 이식성 좋음 (다른 환경에서도 작동)

---

### 방법 2: 레지스트리에 등록 (시스템 전역)

#### 1단계: DLL 파일 배치

`FilePathCheckerModuleExample.dll`을 특정 위치에 복사:

```
C:\Program Files\Hwp\Security\FilePathCheckerModuleExample.dll
```

또는 프로젝트 내:

```
C:\Users\joonho.lee\Projects\AutoHwp\Security\FilePathCheckerModuleExample.dll
```

#### 2단계: 레지스트리 등록

**레지스트리 경로**:
```
HKEY_CURRENT_USER\SOFTWARE\HNC\HwpAutomation\Modules
```

**등록할 값**:
- **키 이름**: `FilePathCheckDLL`
- **값 형식**: `REG_SZ` (문자열)
- **값 데이터**: DLL 전체 경로

**PowerShell로 등록**:
```powershell
# 레지스트리 키 생성 (없으면)
$regPath = "HKCU:\SOFTWARE\HNC\HwpAutomation\Modules"
if (!(Test-Path $regPath)) {
    New-Item -Path $regPath -Force
}

# DLL 경로 등록
$dllPath = "C:\Users\joonho.lee\Projects\AutoHwp\Security\FilePathCheckerModuleExample.dll"
Set-ItemProperty -Path $regPath -Name "FilePathCheckDLL" -Value $dllPath
```

**수동 등록** (`레지스트리.JPG` 참조):
1. `regedit` 실행
2. `HKEY_CURRENT_USER\SOFTWARE\HNC\HwpAutomation\Modules` 이동
3. 새 문자열 값 추가:
   - 이름: `FilePathCheckDLL`
   - 데이터: DLL 전체 경로

#### 3단계: 코드에서 호출

```python
# 레지스트리에 등록된 모듈 사용
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModuleExample")
```

**장점**:
- 한 번 설정하면 모든 스크립트에서 사용 가능
- 코드에서 경로 지정 불필요

**단점**:
- 레지스트리 수정 필요 (관리자 권한)
- 이식성 낮음

---

## 파일 구조

```
AutoHwp/
├── Security/
│   ├── README.md                            # 이 파일
│   ├── SecurityModule.md                    # 원본 설명
│   ├── 보안모듈(Automation).zip              # 원본 압축 파일
│   ├── FilePathCheckerModuleExample.dll     # 보안 모듈 DLL
│   └── HwpAutomation/                       # 소스 코드 (참고용)
│       └── FilePathCheckerModuleExample/
├── Scripts/
│   └── merge_problems_automation.py         # 보안 모듈 사용 예제
└── src/
    └── automation/
        └── client.py                        # register_security_module() 구현
```

---

## 사용 예제

### 예제 1: 기본 사용

```python
from pathlib import Path
from src.automation.client import AutomationClient

# 프로젝트 루트
project_root = Path(__file__).parent.parent

# 클라이언트 생성
client = AutomationClient()

# 보안 모듈 등록
security_dll = project_root / "Security" / "FilePathCheckerModuleExample.dll"
client.register_security_module(str(security_dll))

# 파일 작업 수행 (보안 승인 메시지 없음)
hwp = client.hwp
hwp.HAction.Run("FileNew")

# 파일 삽입
hwp.HAction.GetDefault("InsertFile", hwp.HParameterSet.HInsertFile.HSet)
hwp.HParameterSet.HInsertFile.filename = "C:/path/to/file.hwp"
hwp.HAction.Execute("InsertFile", hwp.HParameterSet.HInsertFile.HSet)

# 저장
hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
hwp.HParameterSet.HFileOpenSave.filename = "C:/output.hwp"
hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
```

### 예제 2: 에러 처리

```python
result = client.register_security_module(str(security_dll))

if not result.success:
    print(f"⚠️  보안 모듈 등록 실패: {result.error}")
    print("   파일 작업 시 수동 승인이 필요할 수 있습니다.")
    # 계속 진행하거나 종료
else:
    print(f"✅ 보안 모듈 등록 성공")
    # 파일 작업 수행
```

### 예제 3: Scripts/merge_problems_automation.py

실제 사용 예제는 `Scripts/merge_problems_automation.py` 참조:

```python
# 0. 보안 모듈 등록 (파일 접근 승인 메시지 방지)
print("[0/7] 보안 모듈 등록 중...")
try:
    hwp = client.hwp
    security_dll_path = project_root / "Security" / "FilePathCheckerModuleExample.dll"

    if security_dll_path.exists():
        hwp.RegisterModule("FilePathCheckDLL", str(security_dll_path.absolute()))
        print(f"✅ 보안 모듈 등록 완료: {security_dll_path.name}")
    else:
        print(f"⚠️  보안 모듈 파일을 찾을 수 없습니다")
except Exception as e:
    print(f"⚠️  보안 모듈 등록 실패: {e}")
```

---

## 보안 모듈 작동 원리

`FilePathCheckerModuleExample.dll`은 COM 인터페이스를 구현하여:

1. **파일 경로 검증**: 접근할 파일 경로의 유효성 확인
2. **보안 확인**: 파일에 대한 보안 검사 수행
3. **자동 승인**: 검증이 통과되면 자동으로 승인 처리

### 소스 코드 (참고용)

`HwpAutomation/FilePathCheckerModuleExample/FilePathCheckerModuleExample.cpp`에서 확인 가능:

```cpp
// IHwpFilePathChecker 인터페이스 구현
STDMETHODIMP CFilePathCheckerModuleExample::IsAllowedPath(
    BSTR path,
    VARIANT_BOOL* pResult
) {
    // 경로 검증 로직
    *pResult = VARIANT_TRUE;  // 모든 경로 허용
    return S_OK;
}
```

---

## 문제 해결

### Q1: "보안 모듈 등록 실패" 오류

**원인**: DLL 파일 경로가 잘못되었거나 파일이 없음

**해결**:
```bash
# DLL 파일 존재 확인
ls Security/FilePathCheckerModuleExample.dll

# 압축 해제 (필요 시)
cd Security
unzip -o "보안모듈(Automation).zip" FilePathCheckerModuleExample.dll
```

### Q2: 등록했는데도 보안 메시지가 나타남

**원인**: `RegisterModule()` 호출 전에 파일 작업 수행

**해결**: 반드시 파일 작업 **전에** 보안 모듈 등록

```python
# ❌ 잘못된 순서
hwp.HAction.Run("FileNew")
client.register_security_module(...)  # 너무 늦음

# ✅ 올바른 순서
client.register_security_module(...)  # 먼저 등록
hwp.HAction.Run("FileNew")            # 그 다음 작업
```

### Q3: DLL 로드 오류 (예: 32bit/64bit 불일치)

**원인**: HWP와 Python 비트 버전 불일치

**해결**:
- HWP 2020 이상: 64bit 사용
- Python도 64bit 사용 확인:
  ```python
  import sys
  print(sys.maxsize > 2**32)  # True면 64bit
  ```

---

## 참고 자료

- `SecurityModule.md`: 한컴 제공 원본 설명
- `HwpAutomation/`: 보안 모듈 소스 코드 (C++)
- `레지스트리.JPG`: 레지스트리 등록 방법 스크린샷
- HWP Automation 매뉴얼: `HwpBooks/HwpAutomation_2504.pdf`

---

## 라이선스 및 주의사항

⚠️ **중요**: 이 보안 모듈은 한컴오피스에서 제공하는 예제 코드입니다.

- **용도**: 개발 및 테스트 목적
- **프로덕션 사용 시**: 자체 보안 검증 로직 구현 권장
- **보안**: 모든 파일 접근을 자동 승인하므로 신뢰할 수 있는 환경에서만 사용

---

**Updated**: 2025-11-13
**Version**: 1.0
