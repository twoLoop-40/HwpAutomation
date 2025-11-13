# Future Enhancements - 향후 확장 아이디어

**우선순위**: 📋 BACKLOG  
**예상 시간**: 여러 스프린트  
**목표**: 400+ 액션 완전 구현

---

## 현재 상태

### 구현 완료 (6/400+)
- ✅ FileNew
- ✅ FileOpen
- ✅ FileClose
- ✅ FileSave
- ✅ InsertText
- ✅ TableCreate

### 진척률: **1.5%**

---

## Phase 2: 핵심 문서 조작 (우선순위 HIGH)

### 1. 텍스트 검색/치환
**ActionTable 참조**: FindDlg, ReplaceDlg, AllReplace

```python
# 제안 API
def find_text(self, text: str, case_sensitive: bool = False) -> HwpResult:
    """문서에서 텍스트 검색"""
    
def replace_text(
    self, 
    find: str, 
    replace: str, 
    all: bool = False
) -> HwpResult:
    """텍스트 치환 (all=True면 전체 치환)"""
```

**MCP 도구**:
- `hwp_find_text`
- `hwp_replace_text`

**예상 시간**: 2시간

---

### 2. 문서 저장 확장
**ActionTable 참조**: FileSaveAs, FileSaveAll

```python
def save_document_as(
    self, 
    path: str, 
    format: str = "HWP"
) -> HwpResult:
    """다른 이름으로 저장 (PDF, DOCX 등 지원)"""
```

**MCP 도구**:
- `hwp_save_as`
- `hwp_export_pdf`

**예상 시간**: 3시간

---

### 3. 커서 이동 및 선택
**ActionTable 참조**: MovePos, Goto, SelectAll

```python
def move_cursor(self, para: int, pos: int) -> HwpResult:
    """커서를 특정 위치로 이동"""

def select_all(self) -> HwpResult:
    """전체 선택"""

def select_range(self, start: tuple, end: tuple) -> HwpResult:
    """범위 선택"""
```

**MCP 도구**:
- `hwp_move_cursor`
- `hwp_select_all`
- `hwp_select_range`

**예상 시간**: 4시간

---

## Phase 3: 서식 및 스타일 (우선순위 MEDIUM)

### 4. 글자 서식
**ActionTable 참조**: CharShape

```python
def set_char_shape(
    self,
    font_face: Optional[str] = None,
    font_size: Optional[int] = None,
    text_color: Optional[int] = None,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None,
    underline: Optional[bool] = None
) -> HwpResult:
    """글자 서식 설정"""
```

**MCP 도구**:
- `hwp_set_font`
- `hwp_set_text_color`
- `hwp_toggle_bold`
- `hwp_toggle_italic`

**예상 시간**: 5시간

---

### 5. 문단 서식
**ActionTable 참조**: ParagraphShape

```python
def set_paragraph_shape(
    self,
    align: Optional[str] = None,  # "left", "center", "right", "justify"
    line_spacing: Optional[float] = None,
    indent_first: Optional[int] = None,
    indent_left: Optional[int] = None,
    indent_right: Optional[int] = None
) -> HwpResult:
    """문단 서식 설정"""
```

**MCP 도구**:
- `hwp_set_alignment`
- `hwp_set_line_spacing`
- `hwp_set_indent`

**예상 시간**: 5시간

---

### 6. 스타일 적용
**ActionTable 참조**: Style

```python
def apply_style(self, style_name: str) -> HwpResult:
    """미리 정의된 스타일 적용"""

def list_styles(self) -> HwpResult:
    """사용 가능한 스타일 목록"""
```

**MCP 도구**:
- `hwp_apply_style`
- `hwp_list_styles`

**예상 시간**: 3시간

---

## Phase 4: 고급 표 조작 (우선순위 MEDIUM)

### 7. 표 편집
**ActionTable 참조**: TableInsertRow, TableDeleteRow, TableMergeCell

```python
def insert_table_row(self, position: int, count: int = 1) -> HwpResult:
    """표에 행 삽입"""

def delete_table_row(self, position: int, count: int = 1) -> HwpResult:
    """표의 행 삭제"""

def insert_table_col(self, position: int, count: int = 1) -> HwpResult:
    """표에 열 삽입"""

def delete_table_col(self, position: int, count: int = 1) -> HwpResult:
    """표의 열 삭제"""

def merge_table_cells(
    self, 
    start_row: int, 
    start_col: int,
    end_row: int, 
    end_col: int
) -> HwpResult:
    """표 셀 병합"""

def split_table_cell(self, rows: int, cols: int) -> HwpResult:
    """표 셀 분할"""
```

**MCP 도구**:
- `hwp_table_insert_row`
- `hwp_table_delete_row`
- `hwp_table_merge_cells`
- `hwp_table_split_cell`

**예상 시간**: 8시간

---

## Phase 5: 문서 정보 조회 (우선순위 HIGH)

### 8. 문서 속성 읽기
**ActionTable 참조**: GetPos, GetFieldList

```python
def get_cursor_position(self) -> HwpResult:
    """현재 커서 위치 조회"""

def get_document_info(self) -> HwpResult:
    """문서 정보 (페이지 수, 글자 수 등)"""

def get_text_content(self) -> HwpResult:
    """문서의 전체 텍스트 추출"""

def get_field_list(self) -> HwpResult:
    """필드 목록 조회"""
```

**MCP 도구**:
- `hwp_get_cursor_pos`
- `hwp_get_document_info`
- `hwp_extract_text`
- `hwp_list_fields`

**예상 시간**: 6시간

---

## Phase 6: 고급 기능 (우선순위 LOW)

### 9. 개체 삽입
**ActionTable 참조**: PictureInsert, ShapeObjectCreate

```python
def insert_image(self, path: str, width: int, height: int) -> HwpResult:
    """이미지 삽입"""

def insert_shape(self, shape_type: str, **kwargs) -> HwpResult:
    """도형 삽입 (사각형, 원 등)"""
```

### 10. 머리말/꼬리말
**ActionTable 참조**: HeaderFooter

```python
def set_header(self, text: str) -> HwpResult:
    """머리말 설정"""

def set_footer(self, text: str) -> HwpResult:
    """꼬리말 설정"""
```

### 11. 페이지 설정
**ActionTable 참조**: PageSetup

```python
def set_page_size(self, width: int, height: int) -> HwpResult:
    """페이지 크기 설정"""

def set_page_margins(
    self, 
    top: int, 
    bottom: int, 
    left: int, 
    right: int
) -> HwpResult:
    """여백 설정"""
```

**예상 시간**: 각 3-5시간

---

## 아키텍처 개선

### 1. 액션 팩토리 패턴
**문제**: 400개 메서드를 일일이 구현하면 비효율적

**제안**:
```python
class ActionFactory:
    """Generic action executor based on ActionTable."""
    
    def __init__(self, hwp):
        self.hwp = hwp
        self.action_registry = self._load_action_table()
    
    def execute(
        self, 
        action_id: str, 
        params: dict = None
    ) -> HwpResult:
        """
        Execute any action by ID.
        
        Uses ActionTable_2504.pdf metadata:
        - Parameter requirements
        - State requirements
        - Default values
        """
        action_spec = self.action_registry.get(action_id)
        if not action_spec:
            return HwpResult.fail(f"Unknown action: {action_id}")
        
        # Validate state
        if action_spec.required_state:
            if not self.check_state(action_spec.required_state):
                return HwpResult.fail("Invalid state")
        
        # Validate parameters
        if action_spec.param_requirement == "RequiredParam":
            if not params:
                return HwpResult.fail("Parameters required")
        
        # Execute
        try:
            action = self.hwp.CreateAction(action_id)
            param_set = action.CreateSet()
            action.GetDefault(param_set)
            
            if params:
                for key, value in params.items():
                    param_set.SetItem(key, value)
            
            if action.Execute(param_set):
                return HwpResult.ok()
            else:
                return HwpResult.fail("Execution failed")
        except Exception as e:
            return HwpResult.fail(str(e))
```

**장점**:
- 새 액션 추가가 메타데이터 업데이트만으로 가능
- ActionTable PDF를 JSON으로 파싱하여 자동화 가능
- 400개 액션을 코드 수정 없이 지원

---

### 2. 플러그인 시스템
```python
class ActionPlugin:
    """Base class for action plugins."""
    
    action_id: str
    description: str
    
    def validate(self, params: dict) -> bool:
        """Validate parameters."""
        pass
    
    def execute(self, client: HwpClient, params: dict) -> HwpResult:
        """Execute action."""
        pass

# 사용
class FindTextPlugin(ActionPlugin):
    action_id = "FindText"
    
    def execute(self, client, params):
        return client.find_text(**params)

# 등록
registry.register(FindTextPlugin())
```

---

### 3. 배치 작업 지원
```python
class HwpBatch:
    """Batch operations for efficiency."""
    
    def __init__(self, client: HwpClient):
        self.client = client
        self.operations = []
    
    def add(self, operation: callable, *args, **kwargs):
        """Add operation to batch."""
        self.operations.append((operation, args, kwargs))
        return self
    
    def execute(self) -> list[HwpResult]:
        """Execute all operations."""
        results = []
        for op, args, kwargs in self.operations:
            result = op(*args, **kwargs)
            results.append(result)
            if not result.success:
                break  # Stop on first error
        return results

# 사용
batch = HwpBatch(client)
batch.add(client.create_new_document)
batch.add(client.insert_text, "Title")
batch.add(client.set_char_shape, font_size=20, bold=True)
batch.add(client.insert_text, "\n\n")
batch.add(client.create_table, 3, 3)
results = batch.execute()
```

---

## 성능 최적화

### 1. COM 호출 캐싱
```python
class CachedHwpClient(HwpClient):
    """HWP client with caching."""
    
    def __init__(self):
        super().__init__()
        self._action_cache = {}
    
    def get_action(self, action_id: str):
        """Get action with caching."""
        if action_id not in self._action_cache:
            self._action_cache[action_id] = self.hwp.CreateAction(action_id)
        return self._action_cache[action_id]
```

### 2. 비동기 작업
```python
import asyncio

class AsyncHwpClient:
    """Async wrapper for HWP client."""
    
    async def insert_text_async(self, text: str) -> HwpResult:
        """Async text insertion."""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            self.client.insert_text, 
            text
        )
        return result
```

---

## 테스트 확장

### 1. 통합 테스트
```python
def test_document_with_formatting():
    """Test document creation with formatting."""
    client = HwpClient()
    
    # Create document
    client.create_new_document()
    
    # Insert title with formatting
    client.insert_text("보고서 제목")
    client.set_char_shape(font_size=20, bold=True)
    client.set_paragraph_shape(align="center")
    
    # Insert content
    client.insert_text("\n\n본문 내용")
    
    # Insert table
    client.create_table(3, 3)
    
    # Save
    client.save_document_as("report.hwp")
    
    client.cleanup()
```

### 2. 성능 테스트
```python
def test_large_document_performance():
    """Test performance with large documents."""
    client = HwpClient()
    client.create_new_document()
    
    start = time.time()
    for i in range(1000):
        client.insert_text(f"Line {i}\n")
    duration = time.time() - start
    
    assert duration < 10.0  # Should complete within 10 seconds
```

---

## 로드맵 요약

| Phase | 기능 | 액션 수 | 예상 시간 | 우선순위 |
|-------|------|---------|-----------|----------|
| Phase 2 | 핵심 문서 조작 | +9 | 2주 | HIGH |
| Phase 3 | 서식/스타일 | +15 | 2주 | MEDIUM |
| Phase 4 | 고급 표 조작 | +8 | 1주 | MEDIUM |
| Phase 5 | 문서 정보 조회 | +10 | 1주 | HIGH |
| Phase 6 | 고급 기능 | +20 | 3주 | LOW |
| **합계** | | **+62** | **9주** | |

**목표**: 6개 → 68개 액션 (17% 달성)

---

## 커뮤니티 기여

### 액션 크라우드소싱
1. ActionTable_2504.pdf를 JSON으로 변환
2. GitHub에 공개
3. 커뮤니티가 개별 액션 구현
4. PR을 통해 통합

### 템플릿 제공
```python
# contrib/action_template.py
class YourActionPlugin(ActionPlugin):
    action_id = "YourAction"
    description = "액션 설명"
    
    def validate(self, params):
        # 검증 로직
        return True
    
    def execute(self, client, params):
        # 실행 로직
        return HwpResult.ok()
```

---

**최종 목표**: **400개 액션 완전 구현으로 HWP 자동화의 표준이 되기** 🎯

