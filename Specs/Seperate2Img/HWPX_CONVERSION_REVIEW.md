# HwpxConversion.idr 명세 검토 및 수정 완료

**검토 날짜**: 2025-11-25
**검토자**: Claude Code

---

## 수정 사항

### 1. Seperate2ImgOps 인터페이스 누락 (추가)
**문제**: `runWorkflowWithConversion` 함수에서 `Seperate2ImgOps` 인터페이스를 사용하지만, import가 없었음.

**해결**:
```idris
-- Forward declaration for Seperate2ImgOps (실제 구현은 Workflow.idr)
public export
interface Seperate2ImgOps where
  preprocessInput : String -> Seperate2ImgConfig -> IO String
  separateProblems : Seperate2ImgConfig -> IO (List String)
  convertToPdf : List String -> IO (List String)
  convertToImage : List String -> Seperate2ImgConfig -> IO (List String)
```

**이유**: 순환 import를 피하기 위해 forward declaration 사용.

---

### 2. getFileName 함수 구문 오류 수정 (Line 89)
**문제**: Pattern guard 구문 오류
```idris
-- Before (오류)
case break (== '/' || == '\\') cs of
```

**해결**:
```idris
-- After (수정)
case break (\c => c == '/' || c == '\\') cs of
```

**이유**: Idris2에서 boolean 조합은 lambda로 감싸야 함.

---

### 3. stripExtension 함수 개선 (Line 103-109)
**문제**:
- 확장자가 없는 경우 처리 불명확
- 패턴 매칭이 불완전

**해결**:
```idris
-- Before
stripExtension filename =
    case break (== '.') (unpack filename) of
        (name, _) => pack name

-- After
stripExtension filename =
    let chars = unpack filename in
    case break (== '.') chars of
        (name, []) => pack name      -- 점이 없음: 원본 반환
        (name, _ :: _) => pack name  -- 점 발견: 점 앞부분 반환
        _ => filename                -- 기타: 원본 반환
```

**이유**: 엣지 케이스 명시적 처리 및 안전성 향상.

---

### 4. 파일명 생성 로직 개선 (Line 131-134)
**문제**: `file.hwpx.converted.hwp` 형태로 중복 확장자 발생 가능

**해결**:
```idris
-- Before
let outputName = fileName ++ ".converted.hwp"

-- After
let baseName = stripExtension fileName
let outputName = baseName ++ ".converted.hwp"
```

**결과**:
- `file.hwpx` → `file.converted.hwp` ✅
- (Before: `file.hwpx` → `file.hwpx.converted.hwp` ❌)

---

## 검증 완료 사항

### ✅ 타입 안전성
- `Either String String` 반환 타입 정확함
- `ConversionResult` 레코드 구조 정확함
- `FileFormat` 타입 정의 적절함

### ✅ 워크플로우 통합
- `ensureHwpFormat` 로직 올바름:
  1. HWP: 원본 경로 반환 (변환 불필요)
  2. HWPX: 변환 후 경로 반환
  3. 기타: 에러 반환
- `runWorkflowWithConversion` 단계 순서 정확함

### ✅ Python 구현 가이드
- `RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")` 명시 ✅
- `Path.with_suffix()` 사용 권장 ✅
- 에러 처리 명확함 ✅
- 타입 시그니처 정확함 ✅

---

## 남은 작업

### 1. Python 구현 (core/hwpx_converter.py)
명세에 따라 다음 함수 구현:
- `convert_hwpx_to_hwp(hwpx_path, output_path)`
- `ensure_hwp_format(input_path, temp_dir)`

### 2. 워크플로우 통합 (automations/seperate2Img/workflow.py)
`Seperate2ImgWorkflow.run()` 메서드 수정:
```python
# 0a. HWPX → HWP 변환 (새로 추가)
from core.hwpx_converter import ensure_hwp_format

target_input_path = ensure_hwp_format(input_path, str(temp_dir))
if target_input_path is None:
    return {"success": False, "message": "HWPX conversion failed"}

# 0b. 전처리 (기존)
preprocessed_path = self._preprocess_input(target_input_path, str(temp_dir))
```

### 3. 테스트 작성
- `Tests/Seperate2Img/test_hwpx_conversion.py`
- HWPX → HWP 변환 검증
- 워크플로우 E2E 테스트

---

## 결론

✅ **명세 검토 완료**: HwpxConversion.idr는 이제 오류 없이 컴파일 가능
✅ **아키텍처 조화**: 기존 Seperate2Img 워크플로우와 자연스럽게 통합됨
✅ **구현 가이드 명확**: Python 개발자가 바로 구현 가능

**다음 단계**: Python 구현 시작 (`core/hwpx_converter.py`)
