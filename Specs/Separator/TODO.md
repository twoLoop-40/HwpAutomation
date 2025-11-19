# Separator TODO

## 향후 개선 사항

### 1. 정답 형식 검증 및 처리
**현재 상태**: EndNote 태그 기반으로 모든 미주 인식 (408개)
**발견 사항**:
- 408개 중 355개는 `[정답]` 포함
- 53개는 `[정답]` 없음 (해설, 그림, 빈 미주 등)

**향후 작업**:
- 정규식 패턴 `\d\.\s*\[정답\]` 매칭 확인
- 정답 형식에 따라 다른 액션 취하기:
  - `[정답]` 있음: 정답 추출 및 별도 저장
  - `[정답]` 없음: 해설로 분류 또는 스킵

**Idris2 명세 추가 필요**:
```idris
-- Specs/Separator/Separator/AnswerParser.idr
data AnswerFormat : Type where
  WithAnswer : AnswerFormat  -- "\d\.\s*\[정답\]" 패턴
  OnlyExplanation : AnswerFormat  -- 해설만
  Empty : AnswerFormat  -- 빈 미주

detectAnswerFormat : String -> AnswerFormat
extractAnswer : String -> Maybe String
```

**Python 구현 예시**:
```python
import re

ANSWER_PATTERN = re.compile(r'(\d+)\.\s*\[정답\](.+)', re.DOTALL)

def detect_answer_format(text: str) -> AnswerFormat:
    if ANSWER_PATTERN.search(text):
        return AnswerFormat.WITH_ANSWER
    elif text.strip():
        return AnswerFormat.ONLY_EXPLANATION
    else:
        return AnswerFormat.EMPTY

def extract_answer(text: str) -> Optional[str]:
    match = ANSWER_PATTERN.search(text)
    if match:
        return match.group(2).strip()
    return None
```

---

## 구현 우선순위

1. ✅ EndNote 태그 기반 미주 인식 (완료)
2. ⏳ 문제 경계 식별 및 추출 (진행 중)
3. ⏳ 그룹화 및 파일 저장 (진행 중)
4. ⏸️ 정답 형식 검증 및 추출 (보류)
5. ⏸️ 정답/해설 분리 저장 (보류)

---

## 참고 데이터

### EndNote 분포 (408개)
- `[정답]` 포함: 355개 (87%)
- `[정답]` 없음: 53개 (13%)
  - 해설/풀이: ~30개
  - 그림 설명: ~10개
  - 빈 미주: ~13개

### 정답 패턴 예시
```
1. [정답] ➄ㄱ. 거짓인 명제...
2. [정답] ➂조건 의 진리집합을 라 하자...
3. [정답] ➁역을 구해보면...
```

### 정답 없는 미주 예시
```
□. (빈 미주)
그림입니다.
원본 그림의 이름: SNAGIT.jpg
해설만 있는 경우...
```
