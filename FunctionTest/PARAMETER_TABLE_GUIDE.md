# HWP Parameter Table 가이드

> FunctionTest에서 발견한 Parameter 사용법 정리

## 공통 함수

### mili_to_hwp_unit(mili: float) -> int

밀리미터를 HWP 단위로 변환

```python
def mili_to_hwp_unit(mili: float) -> int:
    """
    밀리미터를 HWP 단위로 변환

    HWP 단위 = 1/7200 inch = 1/283.465 mm
    """
    return int(mili * 283.465)
```

## 1. 페이지 설정 (PageSetup - B4)

**원본 스크립트**: `OnScriptMacro_b4만들기()`

```python
def setup_b4_page(hwp) -> bool:
    """
    B4 페이지 설정

    - 용지: B4 (257mm x 364mm)
    - 여백: 좌우 30mm, 상 20mm, 하 15mm
    - 머리글/꼬리글: 15mm
    """
    hwp.HAction.GetDefault("PageSetup", hwp.HParameterSet.HSecDef.HSet)

    sec_def = hwp.HParameterSet.HSecDef
    sec_def.PageDef.PaperWidth = mili_to_hwp_unit(257.0)     # 257mm
    sec_def.PageDef.PaperHeight = mili_to_hwp_unit(364.0)    # 364mm
    sec_def.PageDef.LeftMargin = mili_to_hwp_unit(30.0)      # 좌측 30mm
    sec_def.PageDef.RightMargin = mili_to_hwp_unit(30.0)     # 우측 30mm
    sec_def.PageDef.TopMargin = mili_to_hwp_unit(20.0)       # 상단 20mm
    sec_def.PageDef.BottomMargin = mili_to_hwp_unit(15.0)    # 하단 15mm
    sec_def.PageDef.HeaderLen = mili_to_hwp_unit(15.0)       # 머리글 15mm
    sec_def.PageDef.FooterLen = mili_to_hwp_unit(15.0)       # 꼬리글 15mm
    sec_def.HSet.SetItem("ApplyClass", 24)                   # 적용 클래스
    sec_def.HSet.SetItem("ApplyTo", 3)                       # 적용 범위

    return hwp.HAction.Execute("PageSetup", sec_def.HSet)
```

**Parameters**:
- `PaperWidth`: 용지 너비 (HWPUNIT)
- `PaperHeight`: 용지 높이 (HWPUNIT)
- `LeftMargin`: 좌측 여백 (HWPUNIT)
- `RightMargin`: 우측 여백 (HWPUNIT)
- `TopMargin`: 상단 여백 (HWPUNIT)
- `BottomMargin`: 하단 여백 (HWPUNIT)
- `HeaderLen`: 머리글 길이 (HWPUNIT)
- `FooterLen`: 꼬리글 길이 (HWPUNIT)
- `ApplyClass`: 24 (페이지 설정)
- `ApplyTo`: 3 (현재 섹션)

## 2. 다단 레이아웃 (MultiColumn - 2단)

**원본 스크립트**: `OnScriptMacro_단2나누기()`

```python
def create_two_column_layout(hwp) -> bool:
    """
    2단 레이아웃 설정

    - Count: 2 (2단)
    - SameGap: 8mm (단 간격)
    """
    hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)

    col_def = hwp.HParameterSet.HColDef
    col_def.Count = 2                           # 2단
    col_def.SameGap = mili_to_hwp_unit(8.0)     # 단 간격 8mm
    col_def.HSet.SetItem("ApplyClass", 832)     # 적용 클래스
    col_def.HSet.SetItem("ApplyTo", 6)          # 적용 범위

    return hwp.HAction.Execute("MultiColumn", col_def.HSet)
```

**Parameters**:
- `Count`: 단 개수 (2 = 2단)
- `SameGap`: 단 간격 (HWPUNIT)
- `ApplyClass`: 832 (다단 설정)
- `ApplyTo`: 6 (현재 위치부터)

**Note**:
- 원본 스크립트는 `MultiColumn` + `MultiColumnPreset1` 두 단계
- Python에서는 `MultiColumnPreset1`의 Type, Layout 등이 작동하지 않음
- `MultiColumn`만으로도 기본 2단 설정 가능

## 3. 조합: B4 + 2단

**통합 템플릿 생성**:

```python
def create_b4_two_column_template(hwp) -> bool:
    """
    B4 + 2단 레이아웃 템플릿 생성
    """
    # 1. B4 페이지 설정
    if not setup_b4_page(hwp):
        return False

    # 2. 2단 레이아웃
    if not create_two_column_layout(hwp):
        return False

    return True
```

## 4. 페이지/칼럼 정보 감지 문제

**문제**: HWP API는 (list, para, pos) 좌표만 제공하며, 직접적인 page/column 정보를 제공하지 않음

**시도한 방법**:
1. `HKeyIndicator.PrintPageNo` - ❌ 항상 0 반환
2. `HKeyIndicator.CurrentColumn` - ❌ 항상 0 반환
3. `PosToLinePos()` - ❌ 메서드 존재하지 않음
4. `GetCursorPos()` - ❌ 메서드 존재하지 않음

**결론**:
- HWP API는 **내용 기반 (Content-based)** 위치 제어만 제공
- Para 번호는 동적으로 변경됨 (BreakColumn 호출 시)
- **직접적인 page, column 번호 조회 불가능**

**우회 방법** (제안):
1. **문서 생성 시 직접 추적**:
   - 삽입할 때마다 page, column 카운터 수동 관리
   - BreakColumn 호출 → column += 1
   - 페이지 넘김 감지 → page += 1

2. **Para → Column 매핑 테이블**:
   - B4 + 2단 레이아웃에서:
     - Para 0 = 헤더 영역
     - Para 1~8 = 1페이지 1칼럼
     - Para 9~16 = 1페이지 2칼럼
     - Para 17~24 = 2페이지 1칼럼
     - ...
   - 하지만 내용량에 따라 동적 변경되므로 정확하지 않음

3. **BreakColumn 카운팅**:
   ```python
   column_tracker = {
       'page': 1,
       'column': 1,
       'para_list': [],
   }

   def insert_problem(hwp, problem_file, tracker):
       """문항 삽입 + 위치 추적"""
       start_para = hwp.GetPos()[1]

       # 복사-붙여넣기
       copy_paste_problem(problem_file, hwp)

       # 칼럼 구분
       hwp.Run("BreakColumn")

       # 추적
       end_para = hwp.GetPos()[1]
       tracker['para_list'].append({
           'para_range': (start_para, end_para),
           'page': tracker['page'],
           'column': tracker['column'],
       })

       # 칼럼 증가 (2단이면 2마다 페이지 증가)
       tracker['column'] += 1
       if tracker['column'] > 2:
           tracker['column'] = 1
           tracker['page'] += 1

       return tracker
   ```

## 참조

- `HwpBooks/ParameterSetTable_2504.pdf` - 전체 파라미터 테이블
- `FunctionTest/test_create_two_columns.py` - 2단 테스트
- `FunctionTest/test_create_b4_two_column_template.py` - B4 + 2단 테스트
- `FunctionTest/test_e2e_b4_two_column_merge.py` - E2E 합병 테스트
- `Schema/HWP_POSITION_CONTROL_SPEC.md` - 위치 제어 명세
