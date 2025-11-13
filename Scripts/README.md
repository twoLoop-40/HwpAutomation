# Scripts - 유틸리티 스크립트

PDF 처리 및 자동화 도구

## 📋 스크립트 목록

### 1. `parse_parameter_table.py`
**ParameterSetTable_2504.pdf 파싱**

```bash
# 실행
python Scripts/parse_parameter_table.py

# 결과
Schema/ParameterTable_Chunks/  # 텍스트 청크
Schema/parameter_table.json     # 구조화된 데이터
```

**기능:**
- PDF에서 텍스트 추출
- 50KB씩 청크로 분할
- 파라미터 정보 JSON으로 변환

---

### 2. `split_pdf.py`
**PDF 파일 분할**

```bash
# 실행
python Scripts/split_pdf.py

# 결과
HwpBooks/ParameterTable_Chunks/
├── parameter_table_part1_p1-50.pdf
├── parameter_table_part2_p51-100.pdf
└── ...
```

**기능:**
- PDF를 50 페이지씩 분할
- 각 파일을 Claude에 업로드 가능

---

### 3. `generate_idris_from_json.py` (예정)
**JSON → Idris 코드 자동 생성**

```bash
# 입력: Schema/parameter_table.json
# 출력: Specs/Generated_Actions.idr

python Scripts/generate_idris_from_json.py
```

---

## 🚀 빠른 시작

### 필요한 패키지

```bash
# 기본
pip install PyPDF2

# 표 추출 (선택)
pip install tabula-py
pip install camelot-py[cv]
```

### 사용 순서

#### 1단계: PDF 분할 또는 텍스트 추출
```bash
# 옵션 A: PDF 분할 (Claude에 업로드용)
python Scripts/split_pdf.py

# 옵션 B: 텍스트 추출 (자동 파싱용)
python Scripts/parse_parameter_table.py
```

#### 2단계: 결과 확인
```bash
# 분할된 PDF 확인
ls HwpBooks/ParameterTable_Chunks/

# 또는 텍스트 청크 확인
ls Schema/ParameterTable_Chunks/
cat Schema/ParameterTable_Chunks/parameter_table_chunk_1.txt | head -50
```

#### 3단계: Claude에게 처리 요청
```
분할된 PDF나 텍스트 청크를 Claude에게 보여주고:

"이 내용에서 액션과 파라미터 정보를 추출해서 JSON으로 만들어줘"
```

---

## 💡 팁

### PDF가 너무 클 때
1. `split_pdf.py`로 50페이지씩 분할
2. 각 파일을 Claude에 개별 업로드
3. 결과를 하나의 JSON으로 병합

### 자동화하고 싶을 때
1. `parse_parameter_table.py`로 텍스트 추출
2. 추출된 텍스트 형식 확인
3. `parse_parameter_line()` 함수 수정
4. 다시 실행하여 JSON 생성

### 점진적으로 작업할 때
1. 핵심 20개 액션만 먼저 수동으로
2. `Schema/core_actions.json` 생성
3. Idris/Python 코드 생성 및 테스트
4. 나머지는 나중에 추가

---

## 📁 출력 파일 위치

```
AutoHwp/
├── HwpBooks/
│   └── ParameterTable_Chunks/     # 분할된 PDF
├── Schema/
│   ├── ParameterTable_Chunks/     # 텍스트 청크
│   ├── parameter_table.json       # 구조화된 데이터
│   └── core_actions.json          # 핵심 액션 (수동)
└── Scripts/
    ├── parse_parameter_table.py
    ├── split_pdf.py
    └── README.md
```

---

## 🆘 문제 해결

### PyPDF2 설치 실패
```bash
# Windows
pip install --upgrade pip
pip install PyPDF2

# 가상환경 사용 시
uv pip install PyPDF2
```

### PDF 읽기 실패
- PDF가 암호화되어 있는지 확인
- Adobe Reader에서 열리는지 확인
- 다른 PDF 리더에서 복사가 되는지 확인

### 텍스트 추출 품질 낮음
- Tabula나 Camelot 사용 (표 인식 전문)
- OCR 도구 사용 고려

---

## 🎯 다음 단계

1. **지금**: `split_pdf.py` 실행
2. **다음**: 첫 번째 PDF를 Claude에 업로드
3. **그 다음**: JSON 구조 설계
4. **마지막**: 자동화 스크립트 완성

자세한 내용은 `Schema/PARAMETER_TABLE_GUIDE.md` 참조!

