# HWP Automation Tools

한글(HWP) 문서 자동화를 위한 도구 모음입니다.

## 핵심 원칙

### 1. Idris2 형식 명세 우선
- 모든 HWP API 작업은 **HwpIdris/** 디렉토리의 Idris2 타입 명세를 먼저 확인
- 타입 안전성 검증 후 Python 구현
- HwpBooks PDF는 보조 자료로만 사용

### 2. HWP COM API 함수형 패턴
**중요 발견**: 함수를 리턴하는 함수형 방식이 HWP COM API와 우연히 잘 작동함

**이유**:
- HWP COM 객체는 상태를 가지지만, 명령(Action)은 무상태
- 함수를 리턴하면 COM 객체의 생명주기와 독립적으로 동작 가능
- 클로저를 통해 COM 객체 참조를 캡슐화하여 안전하게 전달

**예시**:
```python
def open_hwp(file_path: str):
    """HWP 파일을 열고 hwp 객체를 리턴하는 컨텍스트 매니저"""
    pythoncom.CoInitialize()
    try:
        hwp = win32.DispatchEx('HwpFrame.HwpObject')
        hwp.Open(file_path, 'HWP', 'lock:false;forceopen:true')
        yield hwp
    finally:
        hwp.Quit()
        pythoncom.CoUninitialize()

# 함수형 패턴: 클로저로 hwp 참조 캡슐화
def make_text_inserter(hwp):
    """텍스트 삽입 함수를 리턴"""
    def insert_text(text: str) -> bool:
        hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = text
        return hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
    return insert_text

with open_hwp("test.hwp") as hwp:
    insert = make_text_inserter(hwp)  # 함수 리턴
    insert("Hello")  # 나중에 실행
    insert("World")
```

**장점**:
1. **COM 객체 생명주기 관리 명확**: 컨텍스트 매니저와 자연스럽게 조합
2. **재사용성**: 같은 hwp 객체로 여러 작업 함수 생성 가능
3. **테스트 용이**: 함수를 모킹하기 쉬움
4. **Idris2 타입과 매핑**: `(hwp : AnyPtr) -> (params : ParamSet) -> IO Bool` 패턴과 일치

### 3. Copy/Paste vs SaveBlock
**Copy/Paste 방식의 문제**:
- `FileNew` 실행 시 같은 HWP 인스턴스의 클립보드/선택 상태 초기화
- 별도 HWP 인스턴스가 필요 (AppV1 Merger 패턴)

**SaveBlock 방식 (권장)**:
```python
# 블록 선택
hwp.SetPos(*start)
hwp.Run("Select")
hwp.SetPos(*end)

# 선택 영역을 파일로 직접 저장
hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
hwp.HParameterSet.HFileOpenSave.filename = filepath
hwp.HParameterSet.HFileOpenSave.Format = "HWP"
hwp.HParameterSet.HFileOpenSave.Argument = "saveblock"  # ✨ 핵심!
hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)

# 선택 해제
hwp.Run("Cancel")
```

**장점**:
- FileNew/FileClose 불필요
- 클립보드 상태 무관
- 단일 HWP 인스턴스 사용
- 코드 간결 (Copy/Paste 대비 40% 감소)

### 4. 동기화 패턴
HWP COM 작업은 비동기적으로 처리될 수 있음:

```python
from core.sync import wait_for_hwp_ready

# 파일 열기 후 대기
hwp.Open(file_path)
wait_for_hwp_ready(hwp, timeout=5.0)

# 작업 후 대기
hwp.Run("Paste")
time.sleep(0.3)  # 기본 지연
wait_for_hwp_ready(hwp, timeout=2.0)  # 추가 확인
```

## 디렉토리 구조

```
HwpAutomation/
├── HwpIdris/          # Idris2 타입 명세 (최우선 참조)
│   ├── Actions/       # HWP 액션 타입
│   └── ParameterSets/ # 파라미터 타입
├── core/              # 공통 HWP API
│   ├── hwp_extractor.py
│   ├── hwp_extractor_copypaste.py  # SaveBlock 방식
│   └── sync.py        # 동기화 유틸
├── automations/       # 플러그인
│   ├── merger/        # 문제 파일 병합
│   └── separator/     # 문제 파일 분리
└── CLAUDE.md          # 개발 로그
```

## API 사용 순서

1. **HwpIdris/** 확인 → Idris2 타입 검색
2. **Python 구현** → 함수형 패턴 사용
3. **테스트 작성** → Tests/ 또는 .claude/skills/*/tests_*
4. **동기화 확인** → wait_for_hwp_ready 적용

## 참고 문서

- **개발 로그**: `CLAUDE.md` (Step 1~12)
- **타입 명세**: `HwpIdris/TYPE_SPECIFICATION.md`
- **분석 문서**: `Schema/` (HWP 위치 제어, MoveSel 가이드 등)
- **HWP API**: `HwpBooks/ActionTable_2504.pdf`, `HwpBooks/HwpAutomation_2504.pdf`

## 최근 발견 (2025-11-19)

### SaveBlock 방식 전환
- Copy/Paste 방식의 한계 발견 및 SaveBlock 방식으로 전환
- `Argument="saveblock"` 파라미터 발견
- 코드 간결화 및 안정성 향상

### 함수형 패턴의 성공
- 함수를 리턴하는 방식이 HWP COM API와 우연히 잘 맞음
- COM 객체 생명주기와 독립적 동작
- Idris2 타입 시스템과 자연스럽게 매핑
