# Idris2 형식 명세 사용하기

## 개요
HwpAutomation 프로젝트는 Idris2 형식 명세를 사용하여 타입 안전성을 보장합니다.

## 형식 명세 파일

- **Specs/HwpCommon.idr**: 공통 타입 (DocumentState, HwpResult, ParamValue)
- **Specs/ActionTableMCP.idr**: ActionTable API 명세
- **Specs/AutomationMCP.idr**: Automation API 명세 (OLE Object Model)

## 컴파일 체크

### Bash에서 (Claude Code)

Idris2는 `~/.bashrc`에서 자동으로 로드됩니다 (PowerShell 프로필과 동일).

```bash
# 전체 스펙 체크
bash check_specs.sh

# 개별 파일 체크 (idris2.sh는 전역 사용 가능)
idris2.sh --check Specs/HwpCommon.idr
```

### 다른 프로젝트에서도 동일하게 작동

Idris2 환경은 전역으로 설정되어 있으므로, 모든 프로젝트에서 자동으로 사용 가능합니다.

자세한 내용은 `/c/Users/joonho.lee/Projects/InstallIdris2/BASH_SETUP.md` 참조.

## CI/CD 통합

GitHub Actions 등에서 사용하려면:

```yaml
- name: Setup Idris2
  run: |
    # WSL 또는 직접 설치

- name: Check Specs
  run: bash check_specs.sh
```

## Python 구현과의 관계

| Idris2 스펙 | Python 구현 |
|-------------|-------------|
| Specs/HwpCommon.idr | src/common/types.py |
| Specs/ActionTableMCP.idr | src/action_table/*.py |
| Specs/AutomationMCP.idr | src/automation/*.py |

Python 구현은 Idris2 스펙을 기반으로 타입 힌트와 런타임 검증을 제공합니다.
