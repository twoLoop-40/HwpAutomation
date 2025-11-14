# HWP 위치(Position)와 위치 제어 명세

> **목적**: FunctionTest 기반 실증 데이터로 HWP 문서 위치 체계와 제어 방법을 명세화
> **다음 단계**: Idris2 타입 명세 작성
>
> **핵심 인사이트**: HWP 위치 제어는 **내용 기반(Content-based)**이다.
> - Para 번호는 고정된 주소가 아님
> - 삽입/삭제 시 Para 번호 동적 변경
> - 절대 위치 대신 **상대 위치 + 동적 확인** 전략 필요

---

## 1. 위치 좌표 체계

### 1.1 좌표 형식

```python
# 위치 설정
hwp.SetPos(list, para, pos) → bool

# 위치 조회
(list, para, pos) = hwp.GetPos() → (int, int, int)
```

### 1.2 각 좌표의 의미

| 좌표 | 타입 | 의미 | 범위 | 비고 |
|------|------|------|------|------|
| `list` | int | 텍스트 영역 (List) | 0 ~ N | 0 = 본문, 1+ = 표/헤더/푸터 등 |
| `para` | int | 문단 번호 (Paragraph) | 0 ~ M | 0-based, Para 0은 특수 영역 |
| `pos` | int | 문자 위치 (Character offset) | 0 ~ K | 0-based, 문단 내 문자 위치 |

**핵심 공식:**
```
Position = (List, Para, Pos)
         = (텍스트영역, 문단번호, 문자위치)
```

---

## 2. List (텍스트 영역)

### 2.1 List의 개념

HWP 문서는 여러 독립적인 텍스트 영역(List)으로 구성됨:

- **List 0**: 본문 (Main document body)
- **List 1+**: 특수 영역 (표 내부 셀, 헤더, 푸터, 텍스트 박스, 각주 등)

### 2.2 실증 데이터 (test_document_structure.py, test_explore_all_lists.py)

**양식 파일 ([양식]mad모의고사.hwp):**
```
List 0 (본문):     Para 0~3, 빈 문단들
List 1:            Para 0,   빈 (pos=16에서 시작)
List 2:            Para 0,   빈
List 3:            Para 0,   빈
List 4:            Para 0~1, 빈
List 5:            Para 0,   빈 (pos=16에서 시작)
List 6-9:          Para 0,   빈
```

**관찰:**
- 양식 파일은 List 0~9까지 총 10개 List 보유
- 모든 List가 빈 문단 (클립보드 복사 시 내용 없음)
- **그러나** SelectAll + Copy 시 70자 검출
- **결론**: 실제 내용은 표(Table), 개체(Object) 등 다른 구조에 저장

### 2.3 List 이동 명령 (HwpAutomation_2504.pdf)

```python
# MovePos(moveID, para, pos)
moveMain = 0      # 본문(List 0)으로 이동
moveCurList = 1   # 현재 List 유지
```

---

## 3. Para (문단 번호)

### 3.1 Para의 특성

- **0-based 인덱싱**
- **List 내에서의 문단 순서**
- **Para 0은 특수 제어 영역** (직접 접근 불가)

### 3.2 Para 0의 특이점 (test_inspect_para_0_and_1.py)

```python
hwp.SetPos(0, 0, 0)   # 요청: (0, 0, 0)
hwp.GetPos()          # 실제: (0, 0, 48)  ⚠️ 자동 이동!
```

**실증 데이터:**

| 파일 | Para 0 길이 | 자동 이동 위치 | Para 0 내용 |
|------|-------------|----------------|-------------|
| [양식]mad모의고사.hwp | 48자 | (0, 0, 48) | 빈 (제어 문자만) |
| RPM 공통수학Ⅱ... 문항 | 16자 | (0, 0, 16) | 빈 (제어 문자만) |

**핵심 발견:**
- Para 0은 **문서 메타데이터/제어 영역**
- 길이는 파일마다 다름 (양식 48자, 문항 16자)
- SetPos(0, 0, X)는 항상 Para 0 끝으로 이동
- 클립보드 복사 시 빈 문단 (텍스트 내용 없음)

### 3.3 Para 1 이후 (test_first_column_position.py, test_e2e_column_insertion.py)

```python
hwp.SetPos(0, 1, 0)   # 요청: (0, 1, 0)
hwp.GetPos()          # 실제: (0, 1, 0)  ✅ 정확히 이동
```

**관찰:**
- Para 1부터 실제 본문 시작
- 양식 파일: Para 1~3 모두 빈 문단 (길이 0)
- 문항 파일: Para 1~4 모두 빈 문단 (길이 0)

### 3.4 Para 증가 패턴

**이론적 칼럼 패턴 (다단 레이아웃):**
```
첫 번째 칼럼: para = 1
두 번째 칼럼: para = 3 = 1 + 2*1
세 번째 칼럼: para = 5 = 1 + 2*2
N번째 칼럼:   para = 1 + 2*(N-1)
```

**실제 동작 (test_e2e_column_insertion.py):**
```
문항 1: (0,  1, 0) → (0, 10, 0)  +9 para
문항 2: (0, 10, 0) → (0, 19, 0)  +9 para
문항 3: (0, 19, 0) → (0, 22, 0)  +3 para
문항 4: (0, 22, 0) → (0, 28, 0)  +6 para
문항 5: (0, 28, 0) → (0, 33, 0)  +5 para
```

**결론:**
- Para 증가량 = 삽입된 내용의 문단 구조
- 불규칙적 증가 (내용 복잡도에 따라 다름)
- **GetPos()로 실시간 확인 필수**

---

## 4. Pos (문자 위치)

### 4.1 Pos의 의미

- **해당 Para 내에서의 문자 오프셋** (0-based)
- 텍스트 삽입 시 문자 수만큼 증가

### 4.2 실증 데이터 (test_first_column_position.py)

```python
hwp.SetPos(0, 1, 0)          # (0, 1, 0)
hwp.InsertText("Hello")       # 5글자 삽입
hwp.GetPos()                  # (0, 1, 5)  ✅

hwp.SetPos(0, 1, 0)          # 다시 처음으로
hwp.InsertText("..." * 25)    # 74자 삽입
hwp.GetPos()                  # (0, 1, 74)  ✅
```

---

## 5. 위치 제어 명령

### 5.1 SetPos / GetPos

```python
# 위치 설정
result: bool = hwp.SetPos(list, para, pos)

# 위치 조회
(list, para, pos) = hwp.GetPos()
```

**주의 사항:**
- SetPos가 True 반환해도 실제 위치는 다를 수 있음
- **항상 GetPos()로 실제 위치 확인 필수**

**예시:**
```python
hwp.SetPos(0, 0, 0)     # True 반환
hwp.GetPos()            # (0, 0, 48) ⚠️ 다른 위치!
```

### 5.2 BreakColumn (칼럼 구분)

```python
hwp.Run("BreakColumn")
```

**효과:**
- 현재 위치에서 새 칼럼 생성
- Para 번호 증가 (다음 Para로 자동 이동)
- 다단 레이아웃에서 칼럼 분리에 필수

**실증 데이터 (test_insert_three_problems_with_break.py):**
```python
# 문제 1 삽입
hwp.SetPos(0, 0, 0)              # → (0, 0, 48)
hwp.InsertText("[문제 1]...")
after_insert = hwp.GetPos()      # (0, 0, 104)
hwp.Run("BreakColumn")
after_break = hwp.GetPos()       # (0, 1, 0) ✅ Para 증가!

# 문제 2 삽입
hwp.SetPos(0, 1, 0)              # (0, 1, 0)
hwp.InsertText("[문제 2]...")
after_insert = hwp.GetPos()      # (0, 1, 74)
hwp.Run("BreakColumn")
after_break = hwp.GetPos()       # (0, 2, 0) ✅ Para 증가!
```

### 5.3 문서 이동 명령

```python
hwp.Run("MoveDocBegin")      # 문서 시작으로 이동
hwp.Run("MoveDocEnd")        # 문서 끝으로 이동
hwp.Run("MoveParagraphEnd")  # 현재 Para 끝으로 이동
hwp.Run("MoveRight")         # 한 문자 오른쪽으로
hwp.Run("MoveDown")          # 한 줄 아래로
```

**실증 데이터:**
```python
hwp.Run("MoveDocBegin")
pos = hwp.GetPos()               # (0, 0, 48) [양식 파일]
                                 # (0, 0, 16) [문항 파일]
                                 # → Para 0 끝 위치
```

---

## 6. 복사-붙여넣기 워크플로우

### 6.1 Copy-Paste 전략 (test_e2e_column_insertion.py)

```python
# 1. 원본 파일 열기
source_hwp.Run("MoveDocBegin")
source_hwp.Run("Select")
source_hwp.Run("MoveDocEnd")
source_hwp.Run("Copy")

# 2. 대상 파일에 붙여넣기
target_hwp.SetPos(0, 1, 0)      # 첫 번째 칼럼 시작
target_hwp.Run("Paste")

# 3. 다음 칼럼 생성
target_hwp.Run("BreakColumn")

# 4. 위치 확인
current_pos = target_hwp.GetPos()  # 자동으로 다음 para로 이동
```

### 6.2 Copy-Paste의 특징

**장점:**
- 복잡한 구조(표, 그림, 수식 등)를 통째로 복사
- 서식 정보 유지
- Para 단위 텍스트 삽입보다 안정적

**단점:**
- Para 증가량 예측 불가 (내용 복잡도에 따라 다름)
- SetPos로 고정 위치 지정 어려움
- BreakColumn으로 칼럼 구분 필수

---

## 7. Para와 실제 내용의 분리

### 7.1 핵심 발견 (test_read_para_content.py)

**모순적 관찰:**
```python
# 양식 파일
Para 0-3: 모두 빈 문단 (클립보드 복사 시 빈 문자열)

# 전체 선택 + 복사
hwp.Run("SelectAll")
hwp.Run("Copy")
text_length = len(clipboard_text)  # 70자! 🤔
```

**결론:**
- **Para는 문서 구조 메타데이터일 뿐**
- **실제 텍스트는 Para가 아닌 다른 곳에 저장**
- 가능한 저장 위치:
  - 표(Table) 내부 셀
  - 텍스트 박스/그림 개체
  - 다른 List (List 1~9)
  - 특수 컨트롤 객체

### 7.2 표(Table) 구조 (미완성 조사)

```python
# 표 검색 시도 (test_document_structure.py)
hwp.HAction.GetDefault("TableCellBlock",
                       hwp.HParameterSet.HCellBlockExtend.HSet)
# ❌ 실패: 속성 없음
```

**미해결 과제:**
- 표 개수 및 위치 확인 방법
- 표 내부 셀 접근 방법
- 표 안 List 번호 확인

---

## 8. 실용적 가이드

### 8.0 핵심 원칙: 내용 기반 위치 제어

**HWP의 Para 번호는 메모리 주소가 아닌 논리적 순서:**
- 내용 삽입 시 Para 번호 변경 가능
- 절대 Para 번호에 의존하면 안됨
- **항상 현재 위치 기준 + 상대 이동 + GetPos() 확인**

**권장 패턴:**
```python
# ❌ 나쁜 예: 고정 Para 번호 가정
hwp.SetPos(0, 5, 0)  # 다섯 번째 Para가 항상 같은 내용?

# ✅ 좋은 예: 상대 위치 + 동적 확인
hwp.SetPos(0, 1, 0)              # 시작점
current = hwp.GetPos()
print(f"현재: {current}")

# 내용 삽입
insert_content()
after = hwp.GetPos()             # 삽입 후 위치 확인
print(f"삽입 후: {after}")

hwp.Run("BreakColumn")
next_pos = hwp.GetPos()          # 다음 위치 확인
print(f"다음 칼럼: {next_pos}")
```

### 8.1 칼럼 시작 위치로 이동

```python
# 첫 번째 칼럼 (안전한 위치)
hwp.SetPos(0, 1, 0)
actual = hwp.GetPos()
assert actual == (0, 1, 0)  # ✅ 확인

# N번째 칼럼 (절대 위치 사용 금지!)
# ❌ para_n = 1 + 2 * (N - 1)  # 이론적 계산 불가!
# ✅ 대신 BreakColumn으로 순차 이동
for i in range(N - 1):
    hwp.Run("BreakColumn")
    current = hwp.GetPos()  # 매번 확인
    print(f"칼럼 {i+2} 위치: {current}")
```

### 8.2 안전한 문항 삽입 패턴

```python
# 1. 첫 칼럼 시작
hwp.SetPos(0, 1, 0)
print(f"시작 위치: {hwp.GetPos()}")

for i, problem_file in enumerate(problem_files):
    # 2. 문항 복사-붙여넣기
    copy_paste_problem(problem_file, target_hwp, source_hwp)

    # 3. 삽입 후 위치 확인
    after_insert = hwp.GetPos()
    print(f"문항 {i+1} 삽입 후: {after_insert}")

    # 4. 마지막 문항이 아니면 BreakColumn
    if i < len(problem_files) - 1:
        hwp.Run("BreakColumn")
        after_break = hwp.GetPos()
        print(f"BreakColumn 후: {after_break}")
```

### 8.3 주의사항

1. **Para 0 접근 불가**
   - SetPos(0, 0, 0) → 자동으로 (0, 0, X)로 이동
   - 항상 Para 1부터 사용

2. **BreakColumn 후 Para 패턴 불규칙**
   - 이론: Para += 2
   - 실제: 내용에 따라 다름
   - **항상 GetPos()로 확인**

3. **복사-붙여넣기 시 Para 증가**
   - Para 증가량 = 삽입 내용의 문단 구조
   - 예측 불가 → 동적 확인 필수

---

## 9. 미해결 과제

### 9.1 표(Table) 접근

- [ ] 표 개수 확인 방법
- [ ] 표 위치 및 List 번호
- [ ] 표 내부 셀 접근 API

### 9.2 List 구조 이해

- [ ] List 1~9의 정확한 역할
- [ ] 표 내부 셀이 어느 List에 속하는지
- [ ] List 간 이동 방법

### 9.3 실제 내용 저장 위치

- [ ] Para가 빈 문단인데 내용이 있는 이유
- [ ] 표/개체 내부 텍스트 접근 방법
- [ ] HwpObject 모델의 계층 구조

---

## 10. 참조 테스트 스크립트

| 테스트 | 목적 | 주요 발견 |
|--------|------|-----------|
| `test_first_column_position.py` | 첫 칼럼 위치 검증 | SetPos(0, 1, 0) 정확 |
| `test_move_from_second_to_zero.py` | Para 0 동작 확인 | Para 0 자동 이동 |
| `test_inspect_para_0_and_1.py` | Para 0/1 구조 분석 | Para 0 길이 48/16자 |
| `test_check_file_last_para.py` | 문항 파일 Para 구조 | Para 0~4, 모두 빈 |
| `test_read_para_content.py` | Para 텍스트 읽기 | Para 모두 빈 문단 |
| `test_insert_three_problems.py` | 위치별 삽입 테스트 | 글자 겹침 발생 |
| `test_insert_three_problems_with_break.py` | BreakColumn 효과 | 칼럼 분리 성공 |
| `test_e2e_column_insertion.py` | 실제 문항 E2E 삽입 | Para 불규칙 증가 |
| `test_document_structure.py` | 문서 구조 분석 | List 0~9 존재 |
| `test_explore_all_lists.py` | 모든 List 탐색 | 모든 List 빈 |

---

## 11. 타입 명세를 위한 핵심 개념

### 11.1 Position 타입

```
Position : Type
Position = (List : Nat, Para : Nat, Pos : Nat)
```

**제약 조건:**
- `List >= 0`
- `Para >= 0`
- `Pos >= 0`
- `Para = 0 => Pos >= ParaZeroMinPos` (Para 0은 자동 이동)

### 11.2 SetPos / GetPos 타입

```
SetPos : (list : Nat) -> (para : Nat) -> (pos : Nat) -> IO Bool
GetPos : IO Position

-- 불변식 (Invariant):
-- SetPos(0, 0, 0) >>= GetPos
--   ~> (0, 0, ParaZeroEndPos)  where ParaZeroEndPos ∈ {16, 48, ...}
```

### 11.3 BreakColumn 효과

```
BreakColumn : {current: Position}
           -> IO Position
           where result.para > current.para
```

### 11.4 Para vs 실제 내용 분리

```
Para : Type         -- 구조 메타데이터
Content : Type      -- 실제 텍스트 내용

-- Para와 Content는 독립적
-- Para가 빈 문단이어도 Content는 존재 가능
-- Content는 Table, Object, List 1+ 등에 저장
```

---

## 12. 다음 단계

1. **Idris2 타입 명세 작성**
   - Position, SetPos, GetPos 타입 정의
   - BreakColumn 효과 명세
   - Para 0 불변식 명세

2. **표(Table) API 조사**
   - ActionTable_2504.pdf 재검토
   - 표 접근 방법 확인
   - 표 내부 List 구조 파악

3. **List 구조 완전 이해**
   - List 1~9 역할 명확화
   - List 간 이동 API 확인
   - 표/개체와 List 관계 파악

4. **Python 타입 구현**
   - Idris2 명세 기반 타입 안전 구현
   - Position, SetPos, GetPos 래퍼
   - 런타임 불변식 검증

---

## 부록: 용어 정리

| 용어 | 영문 | 의미 |
|------|------|------|
| 위치 | Position | (list, para, pos) 튜플 |
| 리스트 | List | 독립적 텍스트 영역 |
| 문단 | Paragraph (Para) | List 내 문단 번호 |
| 위치 | Position (Pos) | Para 내 문자 오프셋 |
| 칼럼 | Column | 다단 레이아웃의 단 |
| 표 | Table | 셀로 구성된 표 객체 |
| 개체 | Object | 그림, 텍스트 박스 등 |

---

**작성일**: 2025-11-14
**기반 데이터**: FunctionTest/ 디렉토리 실증 테스트
**다음 작업**: Specs/HwpPosition.idr 작성
