# MoveSel 명령 가이드

## 개요
MoveSel* 명령은 HWP에서 텍스트 선택을 확장하는 명령입니다. Move* 명령과 달리, 선택 영역(Selection)을 유지하면서 커서를 이동시킵니다.

## 실험 결과

### 1. MoveSelLeft
**동작**: 현재 위치에서 왼쪽(이전)으로 선택 확장

**예시**:
```
텍스트: "ABCDEFGH"
커서 위치: H 뒤 (pos=24)

MoveSelLeft x3:
  1회: pos=23 → "H" 선택
  2회: pos=22 → "GH" 선택
  3회: pos=21 → "FGH" 선택
```

**사용 시나리오**:
- Para 끝에서 시작할 때
- 역방향 선택이 필요할 때
- 사용자 스크립트: `OnScriptMacro_DeleteEmptryPara()`에서 사용

### 2. MoveSelRight
**동작**: 현재 위치에서 오른쪽(다음)으로 선택 확장

**예시**:
```
텍스트: "ABCDEFGH"
커서 위치: A 앞 (pos=16)

MoveSelRight x3:
  1회: pos=17 → "A" 선택
  2회: pos=18 → "AB" 선택
  3회: pos=19 → "ABC" 선택
```

**사용 시나리오**:
- Para 시작에서 시작할 때
- 정방향 선택이 필요할 때
- 빈 Para 삭제 시 권장 방법

### 3. MoveSelDown
**동작**: 현재 위치에서 아래(다음 줄)로 선택 확장

**예시**:
```
텍스트:
  Line1
  Line2
  Line3

커서 위치: Line1 시작 (para=0)

MoveSelDown x2:
  1회: para=1 → "Line1\n" 선택
  2회: para=2 → "Line1\nLine2\n" 선택
```

**사용 시나리오**:
- 여러 줄을 한 번에 선택할 때
- Para 단위 선택이 필요할 때
- 빈 Para 삭제 시 사용자가 선호하는 방법

## 빈 Para 삭제에 적용

### 테스트 구조
```
Para 0: "Before"
Para 1: (빈 문단)
Para 2: "After"
```

### 방법 1: MoveSelRight (from Para start)
```python
hwp.SetPos(para_start[0], para_start[1], para_start[2])
hwp.Run("MoveSelRight")
hwp.Run("MoveSelRight")
hwp.Run("Delete")
```
**결과**: 빈 Para + 다음 문자 일부 선택 (`"\nA"`)

### 방법 2: MoveSelDown (from Para start)
```python
hwp.SetPos(para_start[0], para_start[1], para_start[2])
hwp.Run("MoveSelDown")
hwp.Run("Delete")
```
**결과**: 빈 Para 전체 선택 (`"\n"`)

### 방법 3: MoveSelLeft (from Para end) ⭐ **검증됨**
```python
hwp.SetPos(para_start[0], para_start[1], para_start[2])
hwp.Run("MoveSelLeft")
hwp.Run("MoveSelLeft")
hwp.Run("Delete")
```
**결과**: 3개 빈 Para → 0개 (완벽한 삭제, 재생성 없음)
- 이전 테스트(`test_delete_empty_with_movesel.py`)에서 검증 완료

## 권장사항

### 빈 Para 삭제 최적 전략
1. **MoveSelDown 방식** (사용자 선호):
   - Para 시작에서 `MoveSelDown` 1회
   - 정확히 빈 Para만 선택 (개행 문자)
   - 간결하고 직관적

2. **MoveSelLeft 방식** (검증됨):
   - Para 시작에서 `MoveSelLeft` 2회
   - 재생성 없이 완벽하게 삭제됨
   - 기존 스크립트에서 사용됨

3. **MoveSelRight 방식**:
   - Para 시작에서 `MoveSelRight` 2회
   - 다음 문자 일부 포함 가능성 (주의)

### 빈 Para 확인 필수
모든 방식에서 삭제 전 빈 Para 확인 필수:
```python
hwp.Run("MoveParaEnd")
end_pos = hwp.GetPos()
is_empty = (end_pos[2] == 0)

if is_empty:
    # MoveSel + Delete
```

## Select vs MoveSel 비교

| 명령 | 동작 | 선택 유지 | 사용 사례 |
|------|------|-----------|-----------|
| `Select` | 선택 시작 | ❌ 단일 호출 | 범위 선택 시작 |
| `MoveSel*` | 선택 확장 | ✅ 연속 호출 | 점진적 선택 확장 |
| `Move*` | 커서 이동 | ❌ 선택 해제 | 네비게이션 |

## 구현 예제

### MoveSelDown 방식 (권장)
```python
def remove_empty_para_movesel_down(hwp, para_pos):
    """MoveSelDown 방식으로 빈 Para 삭제"""
    # Para 시작으로 이동
    hwp.SetPos(para_pos[0], para_pos[1], para_pos[2])

    # 빈 Para 확인
    hwp.Run("MoveParaEnd")
    end_pos = hwp.GetPos()

    if end_pos[2] == 0:  # 빈 Para
        # Para 시작으로 복귀
        hwp.SetPos(para_pos[0], para_pos[1], para_pos[2])

        # MoveSelDown 1회 (빈 Para 선택)
        hwp.Run("MoveSelDown")

        # 삭제
        hwp.Run("Delete")
        return True

    return False
```

### MoveSelLeft 방식 (검증됨)
```python
def remove_empty_para_movesel_left(hwp, para_pos):
    """MoveSelLeft 방식으로 빈 Para 삭제 (검증됨)"""
    # Para 시작으로 이동
    hwp.SetPos(para_pos[0], para_pos[1], para_pos[2])

    # 빈 Para 확인
    hwp.Run("MoveParaEnd")
    end_pos = hwp.GetPos()

    if end_pos[2] == 0:  # 빈 Para
        # Para 시작으로 복귀
        hwp.SetPos(para_pos[0], para_pos[1], para_pos[2])

        # MoveSelLeft 2회
        hwp.Run("MoveSelLeft")
        hwp.Run("MoveSelLeft")

        # 삭제
        hwp.Run("Delete")
        return True

    return False
```

## 참고 자료
- 실험 코드: `FunctionTest/test_movesel_research.py`
- 검증 코드: `FunctionTest/test_delete_empty_with_movesel.py`
- 사용자 스크립트: `OnScriptMacro_DeleteEmptryPara()` (MoveSelLeft x2 사용)
