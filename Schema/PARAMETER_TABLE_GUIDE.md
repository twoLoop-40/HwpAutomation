# ParameterSetTable_2504.pdf 처리 가이드

## 문제 상황
- PDF 파일이 너무 커서 Claude에 직접 업로드 불가
- 400+ 액션의 파라미터 정보가 필요

## 해결 전략

---

## 🎯 전략 1: PDF → 구조화된 데이터 (권장)

### 장점
- ✅ 재사용 가능한 JSON/CSV 생성
- ✅ Idris 스펙 자동 생성 가능
- ✅ Python 코드 생성 자동화

### 실행 방법

#### 1단계: PDF 텍스트 추출
```bash
# 필요한 패키지 설치
pip install PyPDF2

# 파싱 스크립트 실행
python Scripts/parse_parameter_table.py
```

#### 2단계: 생성된 청크 확인
```bash
# 청크 파일들 확인
ls Schema/ParameterTable_Chunks/

# 첫 번째 청크 내용 확인
cat Schema/ParameterTable_Chunks/parameter_table_chunk_1.txt
```

#### 3단계: 형식에 맞게 파서 조정
PDF의 실제 형식을 확인하고 `parse_parameter_line()` 함수 수정

#### 4단계: JSON 생성
```bash
# 다시 실행
python Scripts/parse_parameter_table.py

# 결과 확인
cat Schema/parameter_table.json
```

---

## 🎯 전략 2: 페이지별 수동 추출

### 실행 방법

#### 옵션 A: PDF 분할 도구 사용

**Windows (Adobe Reader):**
```
1. PDF 열기
2. Tools → Organize Pages
3. Split → 50 페이지씩 분할
4. 각 파일을 Claude에 업로드
```

**온라인 도구:**
- https://www.ilovepdf.com/split_pdf (무료)
- 50-100 페이지씩 분할

#### 옵션 B: 페이지 범위 지정 추출

```python
# Scripts/split_pdf.py
import PyPDF2

def split_pdf(input_path, output_dir, pages_per_file=50):
    with open(input_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        total_pages = len(reader.pages)
        
        for start in range(0, total_pages, pages_per_file):
            end = min(start + pages_per_file, total_pages)
            writer = PyPDF2.PdfWriter()
            
            for page_num in range(start, end):
                writer.add_page(reader.pages[page_num])
            
            output_path = f"{output_dir}/parameter_table_p{start+1}-{end}.pdf"
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"✅ {output_path} 생성")

split_pdf("HwpBooks/ParameterSetTable_2504.pdf", "HwpBooks/Chunks")
```

---

## 🎯 전략 3: OCR + 표 인식

### 실행 방법

#### 옵션 A: Tabula (PDF 표 추출 전문)

```bash
# Tabula 설치
pip install tabula-py

# 표 추출
python Scripts/extract_tables.py
```

```python
# Scripts/extract_tables.py
import tabula
import pandas as pd

# PDF에서 모든 표 추출
tables = tabula.read_pdf(
    "HwpBooks/ParameterSetTable_2504.pdf",
    pages='all',
    multiple_tables=True
)

# CSV로 저장
for i, table in enumerate(tables):
    table.to_csv(f"Schema/parameter_table_{i+1}.csv", index=False)
    print(f"✅ Table {i+1} 저장 완료")
```

#### 옵션 B: camelot (고품질 표 추출)

```bash
pip install camelot-py[cv]

python -c "
import camelot
tables = camelot.read_pdf('HwpBooks/ParameterSetTable_2504.pdf')
tables[0].to_csv('Schema/parameter_table.csv')
"
```

---

## 🎯 전략 4: 점진적 구현 (실용적)

### 핵심 아이디어
모든 400개 액션을 한 번에 하지 말고, **우선순위가 높은 것부터**

### 실행 계획

#### Phase 1: 핵심 액션 20개 (손으로 입력)
```markdown
PDF에서 가장 자주 사용되는 액션만 선택:

1. FileNew, FileOpen, FileSave, FileSaveAs
2. InsertText, Delete, Copy, Paste
3. CharShape, ParagraphShape
4. TableCreate, TableInsertRow, TableDeleteRow
5. FindText, ReplaceText
6. MoveDocBegin, MoveDocEnd
7. Undo, Redo
8. Print

→ 이것들의 파라미터를 직접 확인하여 JSON으로 작성
```

**예시 JSON:**
```json
{
  "actions": [
    {
      "action_id": "FileOpen",
      "parameters": [
        {
          "name": "filename",
          "type": "String",
          "required": true,
          "description": "열 파일의 경로"
        },
        {
          "name": "format",
          "type": "String",
          "required": false,
          "default": "HWP",
          "description": "파일 포맷"
        }
      ]
    }
  ]
}
```

#### Phase 2: 자동화 스크립트로 나머지 추가
나중에 PDF 파싱이 완성되면 나머지 380개 추가

---

## 🎯 전략 5: Claude를 활용한 단계적 처리

### 방법

#### 1. 텍스트 청크 생성
```bash
python Scripts/parse_parameter_table.py
# → Schema/ParameterTable_Chunks/ 생성
```

#### 2. Claude에게 순차적으로 처리 요청

**첫 번째 청크:**
```
<chunk 1 내용 붙여넣기>

위 내용에서 액션과 파라미터 정보를 추출해서 
다음 형식의 JSON으로 만들어줘:

{
  "actions": [
    {
      "action_id": "액션명",
      "parameters": [...]
    }
  ]
}
```

**두 번째 청크:**
```
이전에 만든 JSON에 이어서 추가해줘:
<chunk 2 내용>
```

#### 3. 모든 청크 병합
```python
import json

all_actions = []
for i in range(1, 11):  # 10개 청크 가정
    with open(f"Schema/actions_chunk_{i}.json") as f:
        data = json.load(f)
        all_actions.extend(data["actions"])

# 최종 파일 저장
with open("Schema/parameter_table_complete.json", "w") as f:
    json.dump({"actions": all_actions}, f, indent=2, ensure_ascii=False)
```

---

## 📊 최종 목표 데이터 구조

```json
{
  "version": "2504",
  "actions": [
    {
      "action_id": "FileOpen",
      "description": "파일 열기",
      "requirement": "RequiredParam",
      "parameters": [
        {
          "name": "filename",
          "type": "String",
          "required": true,
          "default": null,
          "description": "열 파일의 전체 경로"
        },
        {
          "name": "format",
          "type": "String",
          "required": false,
          "default": "HWP",
          "values": ["HWP", "HWPX", "DOC", "DOCX"],
          "description": "파일 형식"
        }
      ]
    },
    {
      "action_id": "CharShape",
      "description": "글자 모양 설정",
      "requirement": "RequiredParam",
      "parameters": [
        {
          "name": "FontFace",
          "type": "String",
          "required": false,
          "description": "글꼴 이름"
        },
        {
          "name": "FontSize",
          "type": "Int",
          "required": false,
          "default": 10,
          "description": "글자 크기 (포인트)"
        },
        {
          "name": "TextColor",
          "type": "Int",
          "required": false,
          "description": "텍스트 색상 (RGB)"
        }
      ]
    }
  ]
}
```

---

## 🚀 자동화: JSON → Idris 스펙

JSON이 완성되면 자동으로 Idris 코드 생성:

```python
# Scripts/generate_idris_from_json.py
import json

def generate_idris_actions(json_path):
    with open(json_path) as f:
        data = json.load(f)
    
    idris_code = "-- Generated from parameter_table.json\n\n"
    idris_code += "public export\ndata ActionID =\n"
    
    for action in data["actions"]:
        idris_code += f"  {action['action_id']} |\n"
    
    idris_code += "  UnknownAction String\n\n"
    
    # 파라미터 빌더 생성
    for action in data["actions"]:
        if action["parameters"]:
            idris_code += generate_param_builder(action)
    
    return idris_code

# 실행
code = generate_idris_actions("Schema/parameter_table_complete.json")
with open("Specs/Generated_Actions.idr", "w") as f:
    f.write(code)
```

---

## 💡 권장 작업 순서

### 주말 작업 (4시간)

**1단계 (30분): PDF 텍스트 추출**
```bash
python Scripts/parse_parameter_table.py
```

**2단계 (1시간): 청크 확인 및 형식 파악**
```bash
# 첫 몇 개 청크를 읽고 형식 이해
cat Schema/ParameterTable_Chunks/parameter_table_chunk_1.txt
```

**3단계 (2시간): 핵심 20개 액션 수동 입력**
```bash
# Schema/core_actions.json 생성
# 가장 자주 쓰는 액션들만 먼저
```

**4단계 (30분): Python/Idris 코드 생성**
```bash
python Scripts/generate_idris_from_json.py
```

### 평일 작업 (매일 30분씩)

- 월: 액션 21-40 추가
- 화: 액션 41-60 추가
- 수: 액션 61-80 추가
- 목: 액션 81-100 추가
- 금: 테스트 및 검증

**→ 2주면 100개 액션 완성!**

---

## 🎯 즉시 시작 가능한 방법

### 옵션 A: 자동 (추천)

```bash
# 1. 스크립트 실행
python Scripts/parse_parameter_table.py

# 2. 첫 번째 청크 확인
cat Schema/ParameterTable_Chunks/parameter_table_chunk_1.txt | head -100

# 3. Claude에게 물어보기
```

### 옵션 B: 수동 (빠른 시작)

```bash
# 1. PDF 직접 열기
start HwpBooks/ParameterSetTable_2504.pdf

# 2. 핵심 액션 20개 페이지 찾기
#    (목차가 있다면 해당 페이지로)

# 3. 손으로 Schema/core_actions.json 작성
```

---

## 📞 도움이 필요하면

1. **첫 번째 청크만 보여주기**
   - Schema/ParameterTable_Chunks/parameter_table_chunk_1.txt
   - 형식 파악 후 파서 작성 도와드림

2. **특정 액션 하나만 예시로**
   - PDF에서 FileOpen 액션 부분 복사
   - JSON 구조 만들기 도와드림

3. **단계별 진행**
   - 10개씩 나누어서 처리
   - 점진적으로 완성

---

**핵심:** 한 번에 다 하려고 하지 말고, **작은 것부터 자동화!** ✨

