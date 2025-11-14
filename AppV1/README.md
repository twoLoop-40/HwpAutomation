# AppV1: 문항 파일 합병 애플리케이션

여러 개의 HWP 문항 파일을 하나의 2단 레이아웃 문서로 합병하는 애플리케이션

## 특징

- **Idris2 형식 명세 기반**: `HwpIdris/AppV1/MergeProblemFiles.idr`로 타입 안전성 보장
- **모듈화 설계**: 기능별로 명확하게 분리된 모듈 구조
- **최적화된 알고리즘**: `test_merge_40_problems_clean.py`의 가장 깔끔한 결과 기반
- **v3의 모든 학습 내용 통합**:
  - DeleteBack 제거 (시간 소요 문제)
  - 양식 파일 레이아웃 유지 (A3 등)
  - MoveDocBegin + MoveParaBegin으로 헤더 건너뛰기
  - MoveSelDown 방식의 빈 Para 제거

## 구조

```
AppV1/
├── __init__.py          # 패키지 초기화
├── types.py             # 데이터 타입 (Idris 스펙 기반)
├── page_setup.py        # 페이지 설정 (B4, 2단)
├── column.py            # 칼럼 조작
├── para_scanner.py      # Para 스캔 및 제거
├── merger.py            # 메인 합병 로직
├── app.py               # 애플리케이션 엔트리포인트
└── README.md            # 이 파일
```

## 워크플로우

Idris2 명세의 `mergeProblemFiles` 함수 기반:

1. **양식 파일 열기** (또는 새 문서 생성)
   - 기존 레이아웃 유지 (A3 등)
   - 본문 시작 위치로 이동

2. **각 문항 파일 처리**:
   ```
   processSingleProblem:
   - 파일 열기
   - 1단으로 변환
   - Para 스캔
   - 빈 Para 제거 (MoveSelDown 방식)
   - 복사
   ```

3. **대상 문서에 삽입**:
   - 붙여넣기
   - BreakColumn (마지막 제외)

4. **결과 저장**

5. **검증**:
   - 예상 페이지 수 vs 실제 페이지 수
   - ±2 페이지 이내면 성공

## 사용법

```bash
python -m AppV1.app
```

## 주요 개선 사항

### v2 → v3 → AppV1

| 항목 | v2 | v3 | AppV1 |
|------|----|----|-------|
| DeleteBack | ✅ 사용 (무한 루프) | ❌ 제거 | ❌ 제거 |
| 양식 레이아웃 | ❌ B4 강제 변환 | ✅ 유지 (A3 등) | ✅ 유지 |
| Para 제거 방식 | DeleteBack | 없음 | ✅ MoveSelDown |
| 헤더 건너뛰기 | ❌ | ✅ MoveDocBegin + MoveParaBegin | ✅ |
| 모듈화 | ❌ 단일 파일 | ❌ 단일 파일 | ✅ 기능별 분리 |
| Idris2 명세 | ❌ | ✅ OneColOneProblem.idr | ✅ AppV1/MergeProblemFiles.idr |

### 가장 깔끔한 결과

`test_merge_40_problems_clean.py`의 MoveSelDown 방식 채택:
- 빈 Para를 뒤에서부터 제거 (인덱스 유지)
- SetPos로 정확한 위치 이동
- MoveSelDown + Delete로 안전하게 제거

## HwpIdris 참조

AppV1은 HwpIdris의 다음 모듈들을 사용합니다:

- `HwpIdris/Actions/Navigation.idr`: MoveDocBegin, MoveParaEnd, MoveNextParaBegin
- `HwpIdris/Actions/Selection.idr`: MoveSelDown
- `HwpIdris/Actions/Text.idr`: SelectAll, Copy, Paste
- `HwpIdris/ParameterSets/ColDef.idr`: MultiColumn 설정

## 예상 결과

- **입력**: 40개 문항 파일
- **출력**: 약 20페이지 (2단 레이아웃)
- **빈 Para 제거**: MoveSelDown 방식으로 안전하게 제거
- **소요 시간**: 약 2-3분 (파일당 평균 3-5초)

## 검증

Idris2 명세의 `validatePageCount` 기반:
- 예상 페이지: `(문항 수 + 1) / 2` (올림)
- 허용 오차: ±2 페이지

## 다음 단계

- [ ] 새 문서 생성 기능 (B4 2단)
- [ ] CSV 파일 기반 순서 지정
- [ ] 진행률 표시 개선
- [ ] 에러 복구 기능
