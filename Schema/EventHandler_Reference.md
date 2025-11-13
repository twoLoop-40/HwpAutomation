# 한글 오토메이션 Event Handler 참조 문서

**원본**: `HwpBooks/한글오토메이션EventHandler추가_2504.pdf` (6페이지)
**작성일**: 2025-11-13
**MCP 구현**: 옵션 B (상태 조회 방식) - [EventHandler_Analysis.md](EventHandler_Analysis.md) 참조

---

## 📋 개요

### 문서 성격
- **타입**: C++/ATL 구현 가이드
- **대상**: Visual C++ 개발자
- **목적**: HWP Automation Event Handler 구현 방법 설명
- **언어**: C++ (MFC/ATL)

### ⚠️ Python/MCP 제약사항
이 문서는 **C++ 전용** 구현 패턴을 다루며, Python pywin32로는 제한적으로만 구현 가능합니다.
**AutoHwp MCP**에서는 **옵션 B (상태 조회 방식)**을 채택하여 EventHandler의 기능을 간접적으로 제공합니다.

---

## 🔍 IHwpObjectEvents 인터페이스

### 이벤트 목록 (11개)

#### 1. 애플리케이션 수명주기
```cpp
STDMETHOD(Quit)()                           // 한글 종료
```
- **발생 시점**: HWP 어플리케이션 종료 시
- **MCP 대체 방법**: 감지 불가 (프로세스 종료로 MCP 서버도 종료)

#### 2. 창 관리
```cpp
STDMETHOD(CreateXHwpWindow)()               // 창 생성
STDMETHOD(CloseXHwpWindow)()                // 창 닫기
```
- **발생 시점**: HWP 창 생성/닫기
- **MCP 대체 방법**: `hwp_auto_get_windows()` - 창 개수 조회

#### 3. 문서 생성
```cpp
STDMETHOD(NewDocument)(long newVal)         // 새 문서 생성
```
- **발생 시점**: 새 문서 생성
- **파라미터**: `newVal` - 문서 인덱스
- **MCP 대체 방법**: `hwp_auto_get_document_count()` - 문서 개수 증가 감지

#### 4. 문서 열기
```cpp
STDMETHOD(DocumentBeforeOpen)(long newVal)  // 문서 열기 전
STDMETHOD(DocumentAfterOpen)(long newVal)   // 문서 열기 후
```
- **발생 시점**: 문서 열기 전/후
- **파라미터**: `newVal` - 문서 인덱스
- **MCP 대체 방법**:
  - `Before`: ❌ 감지 불가 (상태 조회의 한계)
  - `After`: ✅ `hwp_auto_get_document_path()` - 경로 존재 확인

#### 5. 문서 닫기
```cpp
STDMETHOD(DocumentBeforeClose)(long newVal) // 문서 닫기 전
STDMETHOD(DocumentAfterClose)(long newVal)  // 문서 닫기 후
```
- **발생 시점**: 문서 닫기 전/후
- **파라미터**: `newVal` - 문서 인덱스
- **MCP 대체 방법**:
  - `Before`: ❌ 감지 불가
  - `After`: ✅ `hwp_auto_get_document_count()` - 문서 개수 감소 감지

#### 6. 문서 저장
```cpp
STDMETHOD(DocumentBeforeSave)(long newVal)  // 문서 저장 전
STDMETHOD(DocumentAfterSave)(long newVal)   // 문서 저장 후
```
- **발생 시점**: 문서 저장 전/후
- **파라미터**: `newVal` - 문서 인덱스
- **MCP 대체 방법**:
  - `Before`: ❌ 감지 불가
  - `After`: ✅ `hwp_auto_is_document_modified()` - `false`로 변경 감지

#### 7. 문서 변경
```cpp
STDMETHOD(DocumentChange)(long newVal)      // 문서 변경
```
- **발생 시점**: 문서 내용 변경 시 (타이핑, 편집 등)
- **파라미터**: `newVal` - 문서 인덱스
- **MCP 대체 방법**: ✅ `hwp_auto_is_document_modified()` - `true`로 변경 감지

---

## 🛠️ C++ 구현 방법 (참조용)

### 1. ATL 이벤트 핸들러 클래스 생성

```cpp
// EventHandler.h
class CHwpObjectEventHandler :
    public IDispEventSimpleImpl<1, CHwpObjectEventHandler, &DIID__IHwpObjectEvents>
{
public:
    // 이벤트 핸들러 메서드
    STDMETHOD(Quit)();
    STDMETHOD(DocumentChange)(long newVal);
    // ... 나머지 이벤트 메서드
};
```

### 2. Connection Point를 통한 연결

```cpp
// 연결
IConnectionPointContainer* pCPC;
m_app.m_lpDispatch->QueryInterface(IID_IConnectionPointContainer, (void**)&pCPC);

IConnectionPoint* m_pCP;
pCPC->FindConnectionPoint(__uuidof(IHwpObjectEvents), &m_pCP);

DWORD m_dwHwpObjectEventHandlerCookie;
m_pCP->Advise(p, &m_dwHwpObjectEventHandlerCookie);

pCPC->Release();
```

### 3. 연결 해제

```cpp
// 종료 시
if (m_pCP) {
    m_pCP->Unadvise(m_dwHwpObjectEventHandlerCookie);
    m_pCP->Release();
    m_pCP = NULL;
}
```

---

## 🐍 Python pywin32 구현 (제한적)

### 가능한 방법 (고급 사용자용)

```python
import win32com.client

class HwpEventHandler:
    """HWP 이벤트 핸들러 (제한적)"""

    def OnDocumentChange(self, index):
        """문서 변경 이벤트"""
        print(f"Document {index} changed")

    def OnDocumentAfterSave(self, index):
        """문서 저장 후 이벤트"""
        print(f"Document {index} saved")

# WithEvents 사용
hwp = win32com.client.DispatchWithEvents("HWPFrame.HwpObject", HwpEventHandler)
```

### ⚠️ Python 구현의 한계

1. **Connection Point 복잡성**: pywin32의 WithEvents는 제한적 지원
2. **MCP 구조 불일치**: MCP는 요청-응답 모델, 이벤트는 푸시 모델
3. **비동기 처리**: MCP 서버에서 이벤트 루프 구현 복잡
4. **안정성**: C++ ATL 대비 불안정

---

## ✅ AutoHwp MCP 대체 방안 (옵션 B)

### 상태 조회 기반 변경 감지

EventHandler 이벤트를 직접 구현하는 대신, **상태 조회 도구**를 제공합니다.

#### 📦 제공 도구 (5개)

##### 1. `hwp_auto_is_document_modified()`
**대체 이벤트**: `DocumentChange`, `DocumentAfterSave`

```json
{
  "is_modified": true,
  "status": "Modified"
}
```

**Agent 활용 예시**:
```
Agent: 작업 전 상태 확인
→ hwp_auto_is_document_modified() → false
→ hwp_action_insert_text("Hello")
→ hwp_auto_is_document_modified() → true
Agent: "문서가 수정되었습니다. 저장하시겠습니까?"
```

##### 2. `hwp_auto_get_document_path()`
**대체 이벤트**: `DocumentAfterOpen`, `DocumentAfterSave`

```json
{
  "has_path": true,
  "path": "C:\\Documents\\report.hwp",
  "status": "Path exists"
}
```

**Agent 활용 예시**:
```
Agent: 문서 열림 감지
→ hwp_auto_get_document_count() → 1
→ hwp_auto_get_document_path() → "report.hwp"
Agent: "report.hwp 문서가 열렸습니다."
```

##### 3. `hwp_auto_get_edit_mode()`
**대체 이벤트**: 편집 모드 변경 감지

```json
{
  "edit_mode": "Editable",
  "raw_value": 1
}
```

**Agent 활용 예시**:
```
Agent: 작업 전 편집 가능 여부 확인
→ hwp_auto_get_edit_mode() → "ReadOnly"
Agent: "문서가 읽기 전용입니다. 편집 모드로 전환이 필요합니다."
```

##### 4. `hwp_auto_get_document_count()`
**대체 이벤트**: `DocumentAfterOpen`, `DocumentAfterClose`, `NewDocument`

```json
{
  "count": 2
}
```

**Agent 활용 예시**:
```
Agent: 주기적 문서 개수 확인
→ 이전: count=1
→ 현재: count=2
Agent: "새 문서가 열렸습니다."
```

##### 5. `hwp_auto_get_state_snapshot()`
**대체 이벤트**: 전체 상태 통합 조회

```json
{
  "is_modified": true,
  "has_path": true,
  "path": "C:\\Documents\\report.hwp",
  "edit_mode": "Editable",
  "document_count": 1
}
```

**Agent 활용 예시**:
```
Agent: 효율적인 변경 감지
→ 스냅샷 1: {is_modified: false, path: "", count: 0}
→ 스냅샷 2: {is_modified: false, path: "report.hwp", count: 1}
Agent: "report.hwp가 열렸습니다."
```

---

## 📊 EventHandler vs 상태 조회 비교

| 항목 | EventHandler (C++) | 상태 조회 (MCP) |
|------|-------------------|----------------|
| **실시간성** | ✅ 즉시 감지 | ⚠️ 폴링 필요 |
| **Before 이벤트** | ✅ 지원 | ❌ 불가 |
| **After 이벤트** | ✅ 직접 감지 | ✅ 상태 변경으로 근사 |
| **구현 복잡도** | 높음 (C++/ATL) | 낮음 (Python) |
| **MCP 호환성** | ❌ 부적합 | ✅ 완벽 호환 |
| **Agent 활용** | ⚠️ 콜백 처리 복잡 | ✅ 단순 조회 |
| **안정성** | ✅ 매우 안정적 | ✅ 안정적 |
| **유지보수** | 어려움 | 쉬움 |

---

## 💡 사용 시나리오

### 시나리오 1: 자동 저장 프롬프트

**EventHandler 방식 (C++)**:
```cpp
void OnDocumentChange(long index) {
    if (!autoSaveEnabled) {
        ShowSavePrompt();
    }
}
```

**상태 조회 방식 (MCP + Agent)**:
```
Agent 작업 후:
→ hwp_action_insert_text("Hello")
→ hwp_auto_is_document_modified() → true
Agent: "문서가 수정되었습니다. 저장하시겠습니까?"
User: "네"
→ hwp_action_execute("FileSave")
```

### 시나리오 2: 문서 열림 감지

**EventHandler 방식 (C++)**:
```cpp
void OnDocumentAfterOpen(long index) {
    LoadDocumentMetadata(index);
}
```

**상태 조회 방식 (MCP + Agent)**:
```
Agent 주기적 확인:
→ hwp_auto_get_state_snapshot()
→ 이전: {count: 0}
→ 현재: {count: 1, path: "report.hwp"}
Agent: "report.hwp가 열렸습니다."
→ hwp_auto_get_document_property("DocumentName")
```

### 시나리오 3: 읽기 전용 문서 경고

**EventHandler 방식 (C++)**:
```cpp
void OnDocumentAfterOpen(long index) {
    if (doc->IsReadOnly) {
        ShowReadOnlyWarning();
    }
}
```

**상태 조회 방식 (MCP + Agent)**:
```
Agent 문서 열기 후:
→ hwp_auto_get_edit_mode() → "ReadOnly"
Agent: "이 문서는 읽기 전용입니다."
```

---

## 🎯 권장사항

### DO (권장)
1. ✅ **MCP 도구 사용**: `hwp_auto_*` 상태 조회 도구 활용
2. ✅ **폴링 패턴**: Agent가 필요 시 상태 조회
3. ✅ **스냅샷 비교**: 이전/현재 상태 비교로 변경 감지
4. ✅ **사전 검증**: 작업 전 `get_edit_mode()`, `get_document_count()` 확인

### DON'T (비권장)
1. ❌ **C++ EventHandler 포팅**: Python/MCP 제약으로 복잡도 높음
2. ❌ **Before 이벤트 기대**: 상태 조회로는 불가능
3. ❌ **실시간 감지 기대**: 폴링 기반이므로 시간차 존재
4. ❌ **Connection Point 직접 구현**: pywin32 제한 및 MCP 부적합

---

## 📚 관련 문서

- **분석 문서**: [EventHandler_Analysis.md](EventHandler_Analysis.md) - 옵션 비교 및 설계 결정
- **형식 명세**: [Specs/AutomationState.idr](../Specs/AutomationState.idr) - 상태 조회 타입 정의
- **구현**: [src/automation/client.py](../src/automation/client.py) - 상태 조회 메서드
- **MCP 도구**: [src/automation/tools.py](../src/automation/tools.py) - MCP 도구 정의
- **원본 문서**: `HwpBooks/한글오토메이션EventHandler추가_2504.pdf`

---

## 🔗 참조

### Idris2 형식 명세
```idris
-- Specs/AutomationState.idr
data ModificationStatus = Unmodified | Modified
data EditMode = ReadOnly | Editable | Locked
record DocumentStateSnapshot where
  isModified : ModificationStatus
  documentPath : DocumentPath
  editMode : EditMode
  documentCount : Nat
```

### Python 구현
```python
# src/automation/client.py
def is_document_modified(self) -> HwpResult:
    """문서 수정 여부 확인"""
    doc = self.get_active_document().value["document"]
    is_modified = doc.IsModified
    return HwpResult.ok({"is_modified": bool(is_modified)})
```

---

**작성**: AutoHwp MCP Server
**날짜**: 2025-11-13
**버전**: 1.0 (옵션 B 구현)
