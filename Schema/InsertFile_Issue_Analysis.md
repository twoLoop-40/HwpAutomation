# InsertFile 액션 문제 분석 및 해결

## 문제 상황

### 증상
- `InsertFile` 액션이 `True`를 반환하지만 실제 내용이 삽입되지 않음
- 문서 페이지 수가 1로 유지됨
- `GetText()`로 확인 시 텍스트 길이 2 (거의 비어있음)
- 40개 파일이 모두 "삽입 완료"로 표시되지만 문서는 비어있음

### 환경
- HWP 2024
- Python pywin32
- Automation API (HAction + ParameterSet)

## 원인 분석

### 핵심 원인
**B4 2단 설정을 먼저 적용하면 InsertFile이 작동하지 않음**

### 재현 코드
```python
# ❌ 작동하지 않는 순서
hwp.HAction.Run("FileNew")

# B4 용지 설정
hwp.HAction.GetDefault("PageSetup", hwp.HParameterSet.HPageDef.HSet)
hwp.HParameterSet.HPageDef.PaperWidth = 25700
hwp.HParameterSet.HPageDef.PaperHeight = 36400
hwp.HAction.Execute("PageSetup", hwp.HParameterSet.HPageDef.HSet)

# 2단 편집 설정
hwp.HAction.GetDefault("ColumnDef", hwp.HParameterSet.HColDef.HSet)
hwp.HParameterSet.HColDef.Count = 2
hwp.HAction.Execute("ColumnDef", hwp.HParameterSet.HColDef.HSet)

# InsertFile - 작동하지 않음!
hwp.HAction.GetDefault("InsertFile", hwp.HParameterSet.HInsertFile.HSet)
pset.filename = str(file_path)
hwp.HAction.Execute("InsertFile", pset.HSet)  # True 반환하지만 내용 없음
```

### 검증 테스트
- `test_simple_insert.py`: B4 2단 설정 없이 파일 삽입 → ✅ 성공 (페이지 수 2)
- `debug_hwp_insert.py`: B4 2단 설정 후 파일 삽입 → ❌ 실패 (페이지 수 1)

## 해결 방법

### ✅ 작동하는 순서

```python
# 1. 새 문서 생성 (설정 없이)
hwp.HAction.Run("FileNew")

# 2. 파일 삽입 (일반 문서 상태에서)
for file_path in files:
    hwp.HAction.GetDefault("InsertFile", hwp.HParameterSet.HInsertFile.HSet)
    pset = hwp.HParameterSet.HInsertFile
    pset.filename = str(file_path.absolute())
    pset.KeepSection = 0
    pset.KeepCharshape = 1
    pset.KeepParashape = 1
    pset.KeepStyle = 0
    pset.MoveNextPos = 0
    hwp.HAction.Execute("InsertFile", pset.HSet)

    hwp.Run("MoveDocEnd")  # 커서 이동

# 3. 모든 삽입 완료 후 B4 2단 설정 적용
hwp.Run("MoveDocBegin")
hwp.Run("Select")
hwp.Run("MoveDocEnd")  # 전체 선택

# B4 용지 설정
hwp.HAction.GetDefault("PageSetup", hwp.HParameterSet.HPageDef.HSet)
hwp.HParameterSet.HPageDef.PaperWidth = 25700
hwp.HParameterSet.HPageDef.PaperHeight = 36400
hwp.HAction.Execute("PageSetup", hwp.HParameterSet.HPageDef.HSet)

# 2단 편집 설정
hwp.HAction.GetDefault("ColumnDef", hwp.HParameterSet.HColDef.HSet)
hwp.HParameterSet.HColDef.Count = 2
hwp.HParameterSet.HColDef.SameGap = 1
hwp.HParameterSet.HColDef.Layout = 0
hwp.HAction.Execute("ColumnDef", hwp.HParameterSet.HColDef.HSet)

hwp.Run("Cancel")  # 선택 해제
```

### 핵심 원칙
1. **InsertFile은 기본 문서 설정에서만 작동**
2. **페이지/단 설정은 내용 삽입 후에 적용**
3. **전체 선택 후 설정 적용으로 전체 문서에 적용 가능**

## 참조 구현

### math-collector 프로젝트
`tools/handle_hwp.py`의 `combine_problems()` 함수:
- ✅ B4 2단 설정을 **하지 않음**
- ✅ 파일만 순서대로 삽입
- ✅ 원본 문서 분리 시에만 특정 설정 사용

```python
# math-collector 방식
hwp.HAction.Run("FileNew")  # 설정 없이 새 문서

for target in targets:
    insert_text(hwp, header)      # 헤더 삽입
    insert_hwp_file(hwp, target)  # 파일 삽입 (설정 없음)
    hwp.Run("MoveDocEnd")          # 커서 이동

save_hwp(hwp, out_path)  # 저장
```

## 적용 결과

### 수정 전
```
[4/7] 문제 삽입 중...
  [1/40] 수매씽 공통수학2_9.유리식과 유리함수_3_6_1.hwp
    ✅ 삽입 완료 (1/40)
  ...
[5/7] 문서 저장 중...
✅ 문서 저장 완료

결과: 파일은 비어있음 (내용 없음)
```

### 수정 후
```
[1/7] 새 문서 생성 중...
[4/7] 문제 삽입 중...
  [1/40] 수매씽 공통수학2_9.유리식과 유리함수_3_6_1.hwp
    ✅ 삽입 완료 (1/40)
  ...
  [40/40] 최근평가원 교육청 기출_ver.2024_공통수학 하_어려운거_10_2_20.hwp
    ✅ 삽입 완료 (40/40)

[2-3/7] 문서 전체에 B4 2단 설정 적용...
✅ B4 2단 설정 완료

[5/7] 문서 저장 중...
✅ 문서 저장 완료

결과: 40개 파일 정상 삽입, B4 2단 적용됨
```

## 교훈

### HWP Automation API 특성
1. **문서 설정이 파일 삽입에 영향을 줌**
   - 특히 PageSetup, ColumnDef 등의 구역 설정
2. **InsertFile은 기본 문서 상태를 선호**
   - 복잡한 설정은 삽입 후 적용
3. **전체 선택 후 설정 적용이 안전**
   - 이미 삽입된 내용에 일괄 적용 가능

### 디버깅 방법
1. **단순화 테스트**: B4 2단 설정 없이 먼저 테스트
2. **단계별 검증**: 페이지 수, 텍스트 길이로 삽입 확인
3. **참조 구현 비교**: math-collector 같은 동작하는 코드와 비교

### Idris2 스펙 개선 필요
현재 스펙은 이런 상태 의존성을 표현하지 못함:
```idris
-- 필요한 스펙
data DocumentConfig = DefaultConfig | CustomConfig

-- InsertFile은 DefaultConfig에서만 작동 보장
insertFile : (doc : HwpDocument DefaultConfig) -> FilePath -> HwpResult

-- 설정 적용 후 타입이 변경
applyPageSetup : HwpDocument DefaultConfig -> HwpDocument CustomConfig
```

## 관련 파일
- `Scripts/merge_problems_automation.py`: 수정된 메인 스크립트
- `Scripts/test_simple_insert.py`: 검증 테스트 (B4 2단 없이)
- `Scripts/debug_hwp_insert.py`: 디버깅 스크립트
- `C:\Users\joonho.lee\Projects\math-collector\tools\handle_hwp.py`: 참조 구현
