# 한글 오토메이션 Event Handler 분석

**소스**: `HwpBooks/한글오토메이션EventHandler추가_2504.pdf` (6페이지)
**분석일**: 2025-11-13

---

## 📋 문서 내용

### 문서 성격
- **기술 문서 타입**: C++/ATL 구현 가이드
- **대상**: Visual C++ 개발자
- **목적**: HWP Automation Event Handler 구현 방법 설명
- **언어**: C++ (MFC/ATL)

### 주요 내용

#### 1. IHwpObjectEvents 인터페이스 (이벤트 목록)
```cpp
// 감지 가능한 이벤트들:

STDMETHOD(Quit)()                           // 한글 종료
STDMETHOD(CreateXHwpWindow)()               // 창 생성
STDMETHOD(CloseXHwpWindow)()                // 창 닫기
STDMETHOD(NewDocument)(long newVal)         // 새 문서 생성
STDMETHOD(DocumentBeforeOpen)(long newVal)  // 문서 열기 전
STDMETHOD(DocumentAfterOpen)(long newVal)   // 문서 열기 후
STDMETHOD(DocumentBeforeClose)(long newVal) // 문서 닫기 전
STDMETHOD(DocumentAfterClose)(long newVal)  // 문서 닫기 후
STDMETHOD(DocumentBeforeSave)(long newVal)  // 문서 저장 전
STDMETHOD(DocumentAfterSave)(long newVal)   // 문서 저장 후
STDMETHOD(DocumentChange)(long newVal)      // 문서 변경
```

#### 2. 구현 단계
1. ATL 이벤트 핸들러 클래스 생성
2. `IHwpObjectEvents` 인터페이스 구현
3. Connection Point를 통해 이벤트 핸들러 연결
4. 종료 시 연결 해제

#### 3. Connection Point 패턴
```cpp
// 연결
IConnectionPointContainer* pCPC;
m_app.m_lpDispatch->QueryInterface(IID_IConnectionPointContainer, (void**)&pCPC);
pCPC->FindConnectionPoint(__uuidof(IHwpObjectEvents), &m_pCP);
m_pCP->Advise(p, &m_dwHwpObjectEventHandlerCookie);

// 해제
m_pCP->Unadvise(m_dwHwpObjectEventHandlerCookie);
```

---

## 🔍 Python MCP 적용 분석

### 현재 상황
- **Automation MCP**: OLE Object Model 기반 (속성/메서드만)
- **Event Handler**: ❌ 미구현 (C++ 전용 가이드만 존재)

### 기술적 제약사항

#### 1. Python COM 이벤트 제한
- **pywin32의 한계**:
  - COM 이벤트 핸들러는 `win32com.client.WithEvents()` 사용
  - Connection Point 패턴 지원하지만 제한적
  - MCP 서버는 비동기 이벤트 처리 복잡

#### 2. MCP 아키텍처 제약
- MCP는 **요청-응답 모델** (Request-Response)
- 이벤트는 **푸시 모델** (Server-Push)
- MCP는 서버가 클라이언트에게 능동적으로 메시지 전송 불가

#### 3. 구현 복잡도
- C++ ATL/COM 전용 패턴
- Python에서 재구현하려면 고급 COM 지식 필요
- MCP 서버에서 비동기 이벤트 처리 어려움

---

## 💡 MCP 보강 방안

### 옵션 A: 이벤트 폴링 (Polling) - 실용적 ✅

**개념**: 이벤트를 직접 감지하는 대신, 상태 변경을 주기적으로 확인

**구현**:
```python
# MCP 도구 추가
hwp_auto_poll_document_state()  # 문서 상태 폴링
hwp_auto_check_document_modified()  # 수정 여부 확인
hwp_auto_get_last_event()  # 마지막 작업 확인 (간접)
```

**장점**:
- MCP 요청-응답 모델과 호환
- Python으로 구현 가능
- 안정적

**단점**:
- 실시간 이벤트 감지 불가
- 일부 이벤트 놓칠 수 있음

---

### 옵션 B: 이벤트 로깅 + 조회 - 추천 ⭐

**개념**: HWP 자체의 로그/히스토리를 조회하는 방식

**구현**:
```python
# Automation API의 기존 속성 활용
hwp.IsModified  # 문서 수정 여부
hwp.Path        # 현재 경로 (열림/닫힘 감지)
hwp.EditMode    # 편집 모드 변경 감지
```

**장점**:
- 별도 이벤트 핸들러 불필요
- 상태 기반 감지
- MCP와 완벽 호환

**단점**:
- Before 이벤트 감지 불가
- 세밀한 이벤트 추적 어려움

---

### 옵션 C: 문서화만 (구현 안 함) - 보수적

**이유**:
1. Event Handler는 **C++ 전용 패턴**
2. Python pywin32로 구현 가능하지만 복잡도 높음
3. MCP는 이벤트 모델과 구조적으로 맞지 않음
4. 실용적 가치 낮음 (대부분 폴링으로 대체 가능)

**대신**:
- `Schema/EventHandler_Reference.md` 문서화
- Automation API 상태 조회 도구 강화
- 필요 시 사용자가 C++로 직접 구현

---

## 🎯 추천 방안

### **옵션 B (이벤트 로깅 + 조회) 채택** ⭐

#### 이유
1. **MCP와 호환**: 요청-응답 모델 유지
2. **Python 네이티브**: 복잡한 COM 이벤트 불필요
3. **실용적**: 대부분의 사용 사례 커버
4. **유지보수 용이**: Automation API 기존 기능 활용

#### 구현 계획

##### Phase 1: Automation MCP 상태 조회 도구 추가
```python
# 새 MCP 도구들
hwp_auto_is_document_modified()   # IsModified 속성
hwp_auto_get_document_path()      # Path 속성
hwp_auto_get_edit_mode()          # EditMode 속성
hwp_auto_get_document_count()     # Documents.Count
```

##### Phase 2: 상태 변경 감지 헬퍼
```python
# 클라이언트에 상태 추적 기능 추가
class AutomationClient:
    def track_document_changes(self):
        """문서 변경 감지 (폴링)"""
        # 이전 상태와 비교
        # IsModified, Path 등 확인
```

##### Phase 3: 문서화
- `Schema/EventHandler_Reference.md` 작성
- C++ 구현 가이드 번역
- Python에서 대체 방법 안내

---

## 📊 비교: ActionTable vs EventHandler

| 항목 | ActionTable | EventHandler |
|------|-------------|--------------|
| **문서 타입** | API 명세 (400+ 액션) | 구현 가이드 (C++) |
| **적용 대상** | ✅ MCP 직접 적용 | ❌ MCP 간접 적용 |
| **파싱 필요성** | ✅ 필수 (파라미터 정의) | ❌ 불필요 (문서화만) |
| **Python 구현** | ✅ 완벽 지원 | ⚠️ 제한적 |
| **MCP 강화** | ✅ 132개 액션 추가 | ⚠️ 상태 조회 추가 |

---

## 📁 제안 구조

### 신규 파일 (최소)
```
Schema/
└── EventHandler_Reference.md     # 참조 문서 (번역 + 설명)

Specs/
└── AutomationEvents.idr          # 이벤트 타입 정의 (선택사항)

src/automation/
└── state_tracker.py              # 상태 추적 유틸 (선택사항)
```

### 기존 파일 확장
```
src/automation/tools.py
  + hwp_auto_is_document_modified
  + hwp_auto_get_edit_mode
  + hwp_auto_track_changes (폴링)
```

---

## ✅ 최종 권장사항

### DO (권장)
1. ✅ **EventHandler_Reference.md 작성** - 참조용 문서화
2. ✅ **Automation 상태 조회 도구 추가** - IsModified, EditMode 등
3. ✅ **폴링 기반 변경 감지** - 실용적 대안 제공

### DON'T (비권장)
1. ❌ **C++ Event Handler Python 포팅** - 복잡도 높고 MCP 부적합
2. ❌ **ParameterSetTable 방식 파싱** - 구조화된 데이터 없음
3. ❌ **Connection Point 구현** - Python/MCP 제약

---

## 🚀 다음 단계 (권장)

### 우선순위 1 (즉시)
1. `Schema/EventHandler_Reference.md` 작성 (문서화)
2. Automation 도구에 상태 조회 추가

### 우선순위 2 (선택)
3. 상태 추적 헬퍼 구현 (폴링)
4. Idris2 스펙에 이벤트 타입 추가

### 우선순위 3 (나중에)
5. C++ 샘플 코드 제공 (고급 사용자용)

---

## 💡 핵심 인사이트

**ActionTable vs EventHandler 차이**:
- **ActionTable**: API 명세 → Python 직접 구현 가능 → MCP 강화에 최적
- **EventHandler**: C++ 구현 가이드 → Python 제약 → MCP 간접 지원만

**결론**: EventHandler는 "파싱 + 구현"이 아닌 **"문서화 + 대안 제공"**이 적절합니다.
