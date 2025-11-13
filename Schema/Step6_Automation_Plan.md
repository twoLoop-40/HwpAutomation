# Step 6: Automation API 구현 계획

## 목표
HwpAutomation_2504.pdf 기반 Automation API 구현

## 형식 명세 (완료)
- ✅ `Specs/HwpCommon.idr`: 공통 타입 (DocumentState, HwpResult, ParamValue)
- ✅ `Specs/ActionTableMCP.idr`: ActionTable 전용 스펙
- ✅ `Specs/AutomationMCP.idr`: Automation 전용 스펙 (OLE Object Model)

## API 차이점

### ActionTable API
- **패러다임**: Action 기반
- **호출 방식**: `CreateAction("FileNew")`, `Execute(paramSet)`
- **도구**: `hwp_action_*`
- **상태 관리**: DocumentState (Closed → Opened → Modified → Saved)

### Automation API
- **패러다임**: Object-Oriented (OLE)
- **호출 방식**: `hwp.XHwpDocuments.Open("file.hwp")`
- **도구**: `hwp_auto_*`
- **객체 계층**:
  ```
  IHwpObject (root)
  ├── XHwpDocuments (collection)
  │   └── Item(index) → IXHwpDocument
  └── XHwpWindows (collection)
      └── Item(index) → IXHwpWindow
  ```

## 구현 단계

### 1. AutomationClient (src/automation/client.py)
- [ ] AutomationClient 클래스
- [ ] get_documents() → IXHwpDocuments
- [ ] open_document(path) → IXHwpDocument
- [ ] get_document_property(doc, prop_name)
- [ ] set_document_property(doc, prop_name, value)
- [ ] invoke_document_method(doc, method_name, args)
- [ ] get_windows() → IXHwpWindows
- [ ] COM object lifetime 관리

### 2. Automation Tools (src/automation/tools.py)
- [ ] AUTOMATION_TOOLS 정의
  - hwp_auto_get_documents
  - hwp_auto_open_document
  - hwp_auto_get_path
  - hwp_auto_is_modified
  - hwp_auto_save
  - hwp_auto_close
  - hwp_auto_get_windows
- [ ] AutomationToolHandler 구현

### 3. 통합 (src/tools.py)
- [ ] UnifiedToolHandler에 Automation 라우팅 추가
- [ ] 네임스페이스 분리 확인 (hwp_action_* vs hwp_auto_*)

### 4. 테스트 (TestAutomation_2504/)
- [ ] test_automation_basic.py
  - 문서 열기/닫기
  - 속성 읽기 (Path, IsModified)
- [ ] test_automation_properties.py
  - 읽기 전용 속성 검증
  - 읽기/쓰기 속성 검증
- [ ] test_automation_methods.py
  - Save/Close 메서드
- [ ] test_automation_spec.py
  - Idris 스펙 기반 검증

## 참조 문서
- HwpBooks/HwpAutomation_2504.pdf (Object Model)
- Specs/AutomationMCP.idr (형식 명세)
- Specs/HwpCommon.idr (공통 타입)
