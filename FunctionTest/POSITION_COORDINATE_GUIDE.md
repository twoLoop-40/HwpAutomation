# HWP Position 좌표 (a, b, c) 의미

## 좌표 형식

```python
hwp.SetPos(list, para, pos)
(list, para, pos) = hwp.GetPos()
```

## 각 값의 의미

### 1. `list` (리스트 번호)
- **의미**: 문서 내 독립적인 텍스트 영역 (List)
- **일반적인 값**: `0` (본문)
- **다른 값들**:
  - 머리말/꼬리말
  - 각주/미주
  - 텍스트 박스
  - 표 내부 셀

**실제 관찰**:
- 양식 파일의 본문 영역은 모두 `list=0`
- 칼럼 이동 시에도 `list=0` 유지

### 2. `para` (문단 번호)
- **의미**: List 내에서의 문단(Paragraph) 번호
- **0부터 시작**
- **증가 패턴**:
  - 텍스트 삽입 시 문단 수만큼 증가
  - `BreakColumn` 실행 시 증가
  - 다단 레이아웃에서 칼럼 구분에 사용

**실제 관찰** (test_inspect_para_0_and_1.py):
```
[양식]mad모의고사.hwp:
  Para 0: 48자 (특수 영역, SetPos(0,0,0) → 자동으로 (0,0,48) 이동)
  Para 1: 0자 (빈 문단, 첫 번째 칼럼 시작)
  Para 2: 0자 (빈 문단)
  Para 3: 0자 (빈 문단)
  Para 4+: 접근 시 (0,0,48)로 자동 이동
  문서 시작: (0, 0, 48)
  문서 끝: (0, 3, 0)

개별 문항 파일 (예: RPM 공통수학Ⅱ 07. 명제 134제_13_14문항_6_18.hwp):
  Para 0: 16자 (특수 영역)
  Para 1-4: 0자 (빈 문단들)
  문서 시작: (0, 0, 16)
  문서 끝: (0, 4, 0)
  마지막 para: 4
```

**핵심 발견**:
- Para 0은 항상 특수 영역 (파일마다 길이 다름: 양식 48자, 문항 16자)
- Para 1부터 실제 본문 시작 (대부분 빈 문단으로 시작)
- 문서 시작 = Para 0의 끝 위치
- 문항 파일은 Para 0~4까지 존재 (모두 빈 문단)

**칼럼 패턴 (이론)**:
- 첫 번째 칼럼: `para = 1`
- 두 번째 칼럼: `para = 3` (1 + 2*1)
- 세 번째 칼럼: `para = 5` (1 + 2*2)
- N번째 칼럼: `para = 1 + 2*(N-1)`

**실제 동작** (FunctionTest 결과):
- 문항 삽입 시 문항 길이에 따라 para가 불규칙하게 증가
- BreakColumn은 항상 다음 para로 이동 (고정 패턴 아님)

### 3. `pos` (문자 위치)
- **의미**: 해당 문단(para) 내에서의 문자 위치 (0-based offset)
- **0부터 시작**
- **증가 패턴**: 문자 삽입 시 문자 수만큼 증가

**실제 관찰**:
```python
SetPos(0, 1, 0)    # 첫 번째 칼럼 시작
# 텍스트 "Hello" 삽입
GetPos()           # (0, 1, 5) - 5글자 이동

SetPos(0, 1, 0)    # 다시 처음으로
# 텍스트 74자 삽입
GetPos()           # (0, 1, 74)
```

## 테스트 결과 기반 발견사항

### 1. SetPos(0, 0, 0)의 특이점
```python
hwp.SetPos(0, 0, 0)   # 요청: (0, 0, 0)
hwp.GetPos()          # 실제: (0, 0, 48)
```
- **Para 0**은 직접 접근 불가
- 자동으로 `pos=48` 위치로 이동 (헤더/특수 영역)

### 2. BreakColumn의 효과
```python
# 문항 1 삽입 후
GetPos()                    # (0, 0, 104)
hwp.Run("BreakColumn")
GetPos()                    # (0, 1, 0) - para 증가!

# 문항 2 삽입 후
GetPos()                    # (0, 1, 74)
hwp.Run("BreakColumn")
GetPos()                    # (0, 2, 0) - 또 para 증가!
```

### 3. 실제 문항 삽입 시 Para 증가
```
문항 1: (0,  1, 0) → (0, 10, 0)  +9 para
문항 2: (0, 10, 0) → (0, 19, 0)  +9 para
문항 3: (0, 19, 0) → (0, 22, 0)  +3 para
문항 4: (0, 22, 0) → (0, 28, 0)  +6 para
문항 5: (0, 28, 0) → (0, 33, 0)  +5 para
```
- Para 증가량 = 삽입된 문항의 문단 수

## 실용적 가이드

### 칼럼 시작 위치로 이동
```python
# 첫 번째 칼럼
hwp.SetPos(0, 1, 0)

# N번째 칼럼 (이론적)
# para = 1 + 2*(N-1)
hwp.SetPos(0, 1 + 2*(N-1), 0)
```

### 문항 삽입 워크플로우
```python
# 1. 첫 칼럼 시작
hwp.SetPos(0, 1, 0)

# 2. 문항 삽입 (복사-붙여넣기)
# ... 삽입 로직 ...

# 3. 다음 칼럼 생성
hwp.Run("BreakColumn")

# 4. 자동으로 다음 para로 이동됨
# GetPos() 확인 가능
```

### 주의사항

1. **Para 0 접근 불가**
   - SetPos(0, 0, 0) 시 (0, 0, 48)로 이동
   - 헤더 또는 특수 영역

2. **BreakColumn 후 Para 패턴**
   - 이론: Para += 2
   - 실제: 문서 구조에 따라 다름
   - **항상 GetPos()로 확인 필요**

3. **복사-붙여넣기 시**
   - Para가 삽입 내용의 문단 수만큼 증가
   - SetPos로 고정 위치 지정 어려움
   - BreakColumn으로 칼럼 구분 필수

## 참조

- `Specs/TemplateMerge.idr` - 칼럼 위치 명세
- `FunctionTest/test_first_column_position.py` - 첫 칼럼 테스트
- `FunctionTest/test_move_from_second_to_zero.py` - Para 0 테스트
- `FunctionTest/test_inspect_para_0_and_1.py` - Para 0/1 구조 검사 ⭐
- `FunctionTest/test_check_file_last_para.py` - 문항 파일 Para 구조 확인
- `FunctionTest/test_e2e_column_insertion.py` - 실제 문항 삽입 테스트

## 요약

| 좌표 | 의미 | 범위 | 비고 |
|------|------|------|------|
| `list` | 텍스트 영역 | 0 (본문), 1+ (특수) | 본문은 항상 0 |
| `para` | 문단 번호 | 0 ~ N | Para 0은 특수 영역 |
| `pos` | 문자 위치 | 0 ~ 문단 길이 | 0-based offset |

**핵심**: `(list, para, pos)` = (영역, 문단, 문자위치)
