# Scripts - 도구 모음

**Idris2 명세**: [Specs/Tools/ScriptOrganization.idr](../Specs/Tools/ScriptOrganization.idr)

**주의**: 활성 스크립트들은 `.claude/skills/hwp-automation-tools/`로 이동했습니다.

## 디렉토리 구조

```
Scripts/
└── _deprecated/          # 일회성/구버전 스크립트 (59개)

.claude/skills/hwp-automation-tools/
├── api_parsing/          # API 문서 → Idris2 명세 생성 도구 (7개)
├── dev_utils/            # 개발 유틸리티 (2개)
├── tests_core/           # core/ 모듈 테스트 (3개)
└── tests_automation/     # automations/ 플러그인 테스트 (3개)
```

## 카테고리별 설명

### api_parsing/ - API 파싱 도구 (7개)

HWP API PDF 문서를 Idris2 형식 명세로 변환

- extract_hwp_api.py: HWP API PDF → Idris2 추출
- parse_action_table.py: ActionTable → Idris2 명세
- parse_automation_api.py: Automation API → Idris2
- parse_eventhandler_pdf.py: EventHandler PDF 파싱
- parse_parameter_sets.py: ParameterSet → Idris2
- extract_all_hwp_docs.py: 전체 API 문서 통합
- split_pdf.py: PDF 분할 유틸리티

### dev_utils/ - 개발 유틸리티 (2개)

- kill_hwp.py: 모든 HWP 프로세스 종료
- find_file.py: 파일 검색

### tests_core/ - Core 모듈 테스트 (3개)

- test_copypaste_extraction.py: Copy/Paste 방식 검증
- test_hwp_extractor_full.py: hwp_extractor API 전체 검증
- test_merge_3blocks_parallel.py: 병렬 처리 검증

### tests_automation/ - Automation 플러그인 테스트 (3개)

- test_separator_full.py: Separator 완전 테스트
- test_separator_new.py: Separator 신규 기능
- test_separator_parser.py: XML 파서 테스트

### _deprecated/ - 아카이브 (59개)

일회성 분석, 구버전, 중복 스크립트

## 정리 결과

- 보존: 15개 (API 파싱 7 + 유틸리티 2 + 테스트 6)
- 아카이브: 59개 (일회성/구버전/중복)
- 감소율: 80% (74개 → 15개 활성)
