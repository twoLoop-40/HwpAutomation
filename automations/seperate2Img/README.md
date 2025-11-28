# Seperate2Img Plugin

HWP 문제 파일을 분리하고 각 문제를 이미지로 변환하는 플러그인입니다.

## Idris2 형식 명세

- **Types**: [Specs/Seperate2Img/Types.idr](../../Specs/Seperate2Img/Types.idr)
- **Workflow**: [Specs/Seperate2Img/Workflow.idr](../../Specs/Seperate2Img/Workflow.idr)

## 워크플로우

```
입력 HWP 파일
    ↓
0. preprocessInput: 입력 파일 전처리 (Merger.ParallelPreprocessor 재사용)
    ↓
1. separateProblems: HWP → HWP 파일들 (Separator 재사용)
    ↓
2. convertToPdf: HWP 파일들 → PDF 파일들 (Converter 재사용)
    ↓
3. convertToImage: PDF 파일들 → Image 파일들 (pypdfium2)
    ↓
4. CleaningUp: 임시 파일 정리 (옵션)
    ↓
출력 이미지 파일들
```

## 주요 기능

### 0. 입력 파일 전처리 (NEW!)
- **재사용 모듈**: `automations.merger.parallel_preprocessor`
- 빈 문단 제거로 이미지 품질 향상
- 1단 변환 (필요 시)
- 전처리 실패 시 원본 파일 사용 (fallback)
- 제거된 빈 문단 개수 리포트

### 1. 문제 분리
- **재사용 모듈**: `automations.separator`
- HWP/HWPX 파일에서 EndNote 기반 문제 추출
- HWP 포맷으로 각 문제를 개별 파일로 저장
- 전처리된 파일 사용

### 2. PDF 변환
- **재사용 모듈**: `core.hwp_to_pdf`
- 병렬 처리 (max_workers=5)
- HWP COM API의 `FileSaveAsPdf` 액션 사용

### 3. 이미지 변환
- **라이브러리**: `pypdfium2`, `Pillow`
- 지원 포맷: PNG, JPG
- DPI 옵션: 150, 300, 600
- **다중 페이지 지원**: 모든 페이지를 이미지로 변환
  - 단일 페이지: `문제_01.png`
  - 다중 페이지: `문제_01_1.png`, `문제_01_2.png`, `문제_01_3.png` ...
- **여백 자동 제거 (Auto-Crop)**: 이미지 주변 여백 제거 (옵션)
  - 배경과 콘텐츠 차이 계산으로 자동 크롭
  - 10픽셀 패딩 유지

### 4. 임시 파일 정리
- 옵션 설정 가능
- 중간 HWP 및 PDF 파일 삭제
- 전처리된 임시 파일도 포함

## 설치

```bash
pip install pypdfium2
```

## 사용법

### UI 실행

```python
from automations.seperate2Img import Seperate2ImgPlugin

plugin = Seperate2ImgPlugin()
plugin.run_ui()
```

또는 메인 런처에서:

```bash
python run_ui.py
```

### CLI 실행

```python
from automations.seperate2Img import Seperate2ImgPlugin

plugin = Seperate2ImgPlugin()
result = plugin.run(
    input_path="문제파일.hwp",
    output_dir="./output",
    ui=False
)
```

## UI 옵션

### 해상도 (DPI)
- **150 DPI**: 저해상도 (빠른 처리, 작은 파일)
- **300 DPI**: 표준 해상도 (기본값, 균형)
- **600 DPI**: 고해상도 (느린 처리, 큰 파일)

### 이미지 포맷
- **PNG**: 무손실 압축, 투명도 지원
- **JPG**: 손실 압축, 더 작은 파일 크기

### 이미지 여백 자동 제거
- **체크**: 이미지 주변 여백 자동 크롭
- **미체크**: 원본 이미지 크기 유지 (기본값)
- 배경색과 콘텐츠 차이 계산으로 크롭 영역 결정
- 10픽셀 패딩 자동 추가

### 임시 파일 정리
- **체크**: 작업 완료 후 temp 폴더 삭제
- **미체크**: temp 폴더 유지 (디버깅 용이, 기본값)

## 출력 구조

```
입력파일_images/
├── temp/                          # 임시 파일 (옵션으로 삭제 가능)
│   ├── 1.hwp
│   ├── 1.pdf
│   ├── 2.hwp
│   ├── 2.pdf
│   └── ...
├── 1.png                          # 최종 이미지 (단일 페이지)
├── 2_1.png                        # 최종 이미지 (다중 페이지 - 첫 페이지)
├── 2_2.png                        # 최종 이미지 (다중 페이지 - 둘째 페이지)
├── 3.png
└── ...
```

## 테스트

### PDF to Image 변환 테스트

```bash
python -X utf8 Tests/Seperate2Img/test_pdf_to_image.py
```

**테스트 커버리지**:
- ✅ 단일 PDF → PNG 변환
- ✅ 배치 PDF → PNG 변환 (병렬 처리)
- ✅ PDF → JPG 변환
- ✅ 다양한 DPI 설정 (150, 300, 600)

**결과**: 4/4 테스트 통과 (100%)

## 성능

### DPI별 파일 크기 (A4 기준)
- **150 DPI**: ~10 KB (PNG)
- **300 DPI**: ~32 KB (PNG), ~134 KB (JPG)
- **600 DPI**: ~115 KB (PNG)

### 처리 속도
- **문제 분리**: Separator 성능 참조
- **PDF 변환**: 병렬 처리 (5 workers)
- **이미지 변환**: pypdfium2 렌더링 (빠름)

## Idris2 명세 구현

### ProcessingState 구현

```python
# Initial → Preprocessing
preprocessed_path = self._preprocess_input(input_path, temp_dir)
target_input_path = preprocessed_path if preprocessed_path else input_path

# Preprocessing → Separating
hwp_files = self._separate_problems(target_input_path, temp_dir)

# Separating → ConvertingToPdf
pdf_files = self._convert_to_pdf(hwp_files)

# ConvertingToPdf → ConvertingToImg
img_results = self._convert_to_image(pdf_files, output_dir, dpi, format)

# ConvertingToImg → CleaningUp (optional)
if cleanup_temp:
    self._cleanup_temp(temp_dir)  # 재시도 로직 포함

# CleaningUp → Completed
return ProcessingResult(...)
```

### 인터페이스 매핑

| Idris2 인터페이스 | Python 구현 |
|-------------------|-------------|
| `preprocessInput` | `automations.merger.parallel_preprocessor.ParallelPreprocessor` |
| `separateProblems` | `automations.separator.separate_problems` |
| `convertToPdf` | `core.hwp_to_pdf.convert_hwp_to_pdf_parallel` |
| `convertToImage` | `automations.seperate2Img.pdf_to_image.convert_pdfs_to_images` |

## 의존성

- **내부 모듈**:
  - `automations.merger`: 입력 파일 전처리 (빈 문단 제거)
  - `automations.separator`: 문제 분리
  - `core.hwp_to_pdf`: PDF 변환
- **외부 라이브러리**:
  - `pypdfium2`: PDF → 이미지 렌더링
  - `Pillow`: 이미지 저장 (pypdfium2 의존성)
  - `pywin32`: HWP COM 제어 (hwp_to_pdf 의존성)

## 제한사항

- **Windows 전용**: HWP COM API 사용
- **HWP 실행 필요**: PDF 변환 시 HWP 프로그램 필요

## 에러 처리 및 리소스 관리

### 파일 핸들 관리
- PDF 파일은 try-finally 블록으로 명시적 `pdf.close()` 호출
- 0 바이트 이미지 파일 자동 감지 및 실패 처리
- 각 변환 단계마다 상세한 에러 메시지 제공

### 임시 파일 정리
- 가비지 컬렉션 (`gc.collect()`) 후 2초 대기
- 최대 3번 재시도 (재시도 간 1초 대기)
- 실패 시 수동 삭제 안내 메시지 표시

### 에러 유형별 메시지
- PDF 파일 열기 실패
- 빈 PDF 파일
- 페이지 접근 실패
- 페이지 렌더링 실패
- 이미지 변환 실패
- 이미지 저장 실패
- 0 바이트 파일 감지

## 향후 개선 사항

- [x] 다중 페이지 지원 (_1.png, _2.png, ...)
- [x] 0 바이트 이미지 감지 및 에러 보고
- [x] PDF 파일 핸들 명시적 해제
- [x] 임시 폴더 정리 재시도 로직
- [ ] 비동기 UI (Threading 패턴)
- [ ] 진행률 표시 (프로그레스 바)
- [ ] 이미지 품질 미리보기
- [ ] 배치 크기 조정 옵션

## 참조

- **Idris2 명세**: [Specs/Seperate2Img/](../../Specs/Seperate2Img/)
- **Separator 플러그인**: [automations/separator/](../separator/)
- **HWP to PDF**: [core/hwp_to_pdf.py](../../core/hwp_to_pdf.py)
- **테스트**: [Tests/Seperate2Img/](../../Tests/Seperate2Img/)

---

**작성**: 2025-11-24
**버전**: 1.0.0
**상태**: ✅ 구현 및 테스트 완료
