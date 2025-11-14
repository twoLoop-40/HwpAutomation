# InsertFile + BreakColumn 동기화 분석

## 배경

5개 파일 테스트에서 발견한 문제:
- 칼럼 2, 4가 비어있음
- 마지막 칼럼에 3개 문항이 모두 들어감
- 첫 칼럼의 문항은 위가 잘림

**근본 원인**: InsertFile과 BreakColumn이 독립적으로 실행되어 타이밍이 맞지 않음

---

## 시도한 해결책

### 1단계: `time.sleep()` 기반 (실패)

```python
# 기존 코드
hwp.HAction.Execute("InsertFile", ...)
target_hwp.Run("MoveDocEnd")
time.sleep(0.02)  # 임의 대기

hwp.Run("BreakColumn")
time.sleep(0.15)  # 임의 대기
```

**문제점**:
- 임의 대기 시간으로는 실제 작업 완료를 보장할 수 없음
- HWP COM이 비동기적으로 작업 시 동기화 불가능
- 전처리 시간: 72.7초 (매우 느림)

---

### 2단계: `wait_for_hwp_ready()` 기반 (부분 성공)

**구현**:

```python
from src.common.sync import wait_for_hwp_ready

def insert_file_and_break_column(hwp, file_path, is_last):
    # 1. InsertFile 실행
    hwp.HAction.Execute("InsertFile", ...)

    # 2. InsertFile 완료 대기
    if not wait_for_hwp_ready(hwp, timeout=5.0):
        return False

    # 3. 문서 끝으로 이동
    hwp.Run("MoveDocEnd")
    if not wait_for_hwp_ready(hwp, timeout=2.0):
        return False

    # 4. BreakColumn (마지막 제외)
    if not is_last:
        hwp.Run("BreakColumn")
        if not wait_for_hwp_ready(hwp, timeout=3.0):
            return False

    return True
```

**`wait_for_hwp_ready()` 로직** (`src/common/sync.py`):
```python
def wait_for_hwp_ready(hwp, timeout=5.0, check_interval=0.1):
    while time.time() - start_time < timeout:
        try:
            # EditMode 또는 PageCount 접근 가능하면 준비 완료
            if hasattr(hwp, 'EditMode'):
                _ = hwp.EditMode
                return True

            if hasattr(hwp, 'PageCount'):
                _ = hwp.PageCount
                return True

            return True
        except Exception:
            # COM 객체가 바쁘면 예외 발생
            time.sleep(check_interval)
            continue

    return False
```

**결과**:
- 전처리: 69.5초 (3.2초 개선)
- 삽입: 0.8초 (0.8초 개선, 50% 단축)
- **하지만 여전히 칼럼 구분 문제 존재**: 5페이지, 칼럼 구분 0개

---

## 검증 결과

`verify_column_layout.py` 실행 결과:

```
전체 페이지: 5  (기대: 4)

페이지별 내용:
  페이지 1: List=0, Para=0, Pos=48
  페이지 2: List=1, Para=0, Pos=16
  페이지 3: List=2, Para=0, Pos=0
  페이지 4: List=3, Para=0, Pos=0
  페이지 5: List=4, Para=0, Pos=0

칼럼 구조:
  총 Para: 28
  빈 Para: 0
  칼럼 구분: 0개  ⚠️ 문제!
```

**분석**:
- InsertFile은 각 파일을 새로운 List에 삽입 (List 0~4)
- BreakColumn이 전혀 작동하지 않음 (칼럼 구분 0개)
- 각 파일이 별도 페이지로 분리됨 (5페이지)

---

## 근본 문제: BreakColumn 동작 방식

### 가설 1: BreakColumn이 현재 위치가 아닌 삽입 위치에서 작동

```python
# InsertFile 후 커서 위치
pos_before = hwp.GetPos()  # List=0, Para=0, Pos=48
hwp.HAction.Execute("InsertFile", ...)
pos_after = hwp.GetPos()   # List=0, Para=0, Pos=48 (변화 없음!)

# 즉, InsertFile은 문서 끝에 내용을 추가하지만 커서는 원래 위치
```

**문제**:
- `MoveDocEnd`로 문서 끝으로 이동 후 `BreakColumn`을 실행하지만...
- BreakColumn이 실제로 칼럼을 구분하지 못함

### 가설 2: InsertFile의 `KeepSection=0` 파라미터 문제

```python
insert_params.HSet.SetItem("KeepSection", 0)  # 구역 정보 무시
```

**가능성**:
- `KeepSection=0`이 원본 파일의 2단 구성을 무시하고 단순 삽입
- BreakColumn은 이미 2단 구성된 문서에서만 작동?

### 가설 3: InsertFile이 각 파일을 별도 List로 삽입

검증 결과에서 각 파일이 List 0~4에 있음:
- List=0: 첫 번째 파일
- List=1: 두 번째 파일
- List=2: 세 번째 파일
- ...

**의미**:
- InsertFile은 파일을 단순히 덧붙이는 것이 아니라 별도 List로 분리
- BreakColumn은 같은 List 내에서만 작동?

---

## 다음 단계 조사 항목

### 1. BreakColumn 동작 조건 확인
- BreakColumn은 어떤 조건에서 작동하는가?
- 같은 List 내에서만 작동하는가?
- 2단 구성이 먼저 설정되어야 하는가?

### 2. InsertFile 파라미터 재검토
- `KeepSection` 파라미터의 정확한 의미
- 다른 파라미터 옵션 (InsertFileInto, MergeList 등)

### 3. 대안적 접근법
- InsertFile 대신 Copy/Paste + 위치 제어?
- 파일 내용을 직접 읽어서 텍스트/객체 삽입?
- 미리 2단 구성된 섹션에 내용 삽입?

### 4. HwpAutomation_2504.pdf 재확인
- InsertFile 액션의 정확한 동작 명세
- BreakColumn 사용 조건 및 제약사항
- 칼럼 관련 다른 액션 (ColumnControl, SectionControl 등)

---

## 현재 코드 상태

### 개선된 점
✅ `time.sleep()` → `wait_for_hwp_ready()` 전환
✅ InsertFile + BreakColumn 결합 시퀀스 함수
✅ 전처리 시간 3.2초 단축
✅ 삽입 시간 50% 단축

### 미해결 문제
❌ BreakColumn이 작동하지 않음 (칼럼 구분 0개)
❌ 파일들이 별도 List로 분리됨 (5 Lists)
❌ 예상 4페이지 → 실제 5페이지
❌ 전처리 시간 여전히 느림 (69.5초)

---

## 참고 파일

- `AppV1/file_inserter.py`: 현재 구현
- `Tests/AppV1/test_insertfile_5files.py`: 5개 파일 테스트
- `Tests/AppV1/test_insertfile_debug.py`: 커서 위치 디버깅
- `Tests/AppV1/verify_column_layout.py`: 칼럼 레이아웃 검증
- `src/common/sync.py`: HWP 동기화 유틸리티
- `HwpIdris/AppV1/ParallelMerge.idr`: 병렬 처리 명세

---

## 커밋 이력

**현재 커밋**: `Replace time.sleep() with wait_for_hwp_ready() for proper synchronization`

- wait_for_hwp_ready() 활용
- insert_file_and_break_column() 원자적 시퀀스
- 칼럼 레이아웃 검증 스크립트 추가
