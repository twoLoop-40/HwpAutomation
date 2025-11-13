# FileChecker 보안 모듈 등록 가이드

## 필수 사항 ⚠️

**모든 HWP 자동화 스크립트에서 파일을 열거나 저장할 때 반드시 FileChecker 모듈을 등록해야 합니다.**

등록하지 않으면 파일 접근 시 보안 승인 대화상자가 표시되어 스크립트가 멈춥니다.

---

## 사용법

### 기본 패턴

```python
import win32com.client as win32

# HWP 인스턴스 생성
hwp = win32.DispatchEx("HWPFrame.HwpObject")

# 보안 모듈 등록 (파일 접근 승인 대화상자 방지)
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# 이후 파일 열기/저장 가능
hwp.Open("파일경로.hwp", "HWP", "")
```

### AutomationClient 사용 시

```python
from src.automation.client import AutomationClient

client = AutomationClient()
hwp = client.hwp

# 보안 모듈 등록
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# 파일 작업
client.open_document("파일경로.hwp")
```

---

## 등록 시점

**HWP 인스턴스 생성 직후, 파일 작업 전에 등록**

```python
# ✅ 올바른 순서
hwp = win32.DispatchEx("HWPFrame.HwpObject")
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")  # 먼저 등록
hwp.Open("test.hwp", "HWP", "")

# ❌ 잘못된 순서
hwp = win32.DispatchEx("HWPFrame.HwpObject")
hwp.Open("test.hwp", "HWP", "")  # 등록 전에 열기 → 대화상자 표시됨
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
```

---

## 왜 필요한가?

한글(HWP)은 보안상의 이유로 외부 프로그램이 파일에 접근할 때 사용자 승인을 요구합니다.

- **등록 안 함**: 파일 열기/저장 시 대화상자 표시 → 스크립트 멈춤
- **등록 함**: 대화상자 없이 파일 접근 가능 → 자동화 성공

`FilePathCheckerModule`은 한글에 내장된 보안 모듈로, 이를 등록하면 로컬 파일 접근을 자동으로 승인합니다.

---

## 참고 사항

### 매개변수

```python
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
#                  ^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^
#                  모듈 타입           모듈 이름
```

- **모듈 타입**: `"FilePathCheckDLL"` (고정)
- **모듈 이름**: `"FilePathCheckerModule"` (고정)

### 창 숨기기

보안 모듈 등록과 함께 창 숨기기도 설정하면 완전한 백그라운드 실행 가능:

```python
hwp = win32.DispatchEx("HWPFrame.HwpObject")
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
hwp.XHwpWindows.Item(0).Visible = False  # 창 숨기기
```

### AutomationClient에 통합

향후 개선: `AutomationClient.__init__`에서 자동으로 등록하도록 수정 가능

```python
# src/automation/client.py
def __init__(self):
    self._hwp = None
    # TODO: 자동으로 FileChecker 등록

def _create_hwp_instance(self) -> Any:
    hwp = win32.DispatchEx("HWPFrame.HwpObject")
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")  # 자동 등록
    return hwp
```

---

## 실제 사례

### merge_with_template.py

```python
# Lines 167-173
target_hwp = win32.DispatchEx("HwpFrame.HwpObject")
target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
target_hwp.XHwpWindows.Item(0).Visible = False

source_hwp = win32.DispatchEx("HwpFrame.HwpObject")
source_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
source_hwp.XHwpWindows.Item(0).Visible = False
```

### simple_mcp_column_test.py (수정 필요 예시)

```python
# 현재 (등록 없음)
client = AutomationClient()
hwp = client.hwp
hwp.SetPos(0, 1, 0)

# 개선 (등록 추가)
client = AutomationClient()
hwp = client.hwp
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")  # 추가!
hwp.SetPos(0, 1, 0)
```

---

## 체크리스트

새 스크립트 작성 시 확인:

- [ ] `win32.DispatchEx("HWPFrame.HwpObject")` 호출 후
- [ ] `hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")` 호출
- [ ] 파일 열기/저장 전에 등록 완료
- [ ] 창 숨기기 설정 (선택사항)

---

## 문서 출처

- HWP Automation API 공식 문서: `HwpBooks/HwpAutomation_2504.pdf`
- 프로젝트 구현: `Scripts/merge_with_template.py`, `Scripts/find_column_positions.py`
