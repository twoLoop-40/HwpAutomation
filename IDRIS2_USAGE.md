# Idris2 형식 명세 사용하기

## 개요
AutoHwp 프로젝트는 Idris2 형식 명세를 사용하여 타입 안전성을 보장합니다.

## 형식 명세 파일

- **Specs/HwpCommon.idr**: 공통 타입 (DocumentState, HwpResult, ParamValue)
- **Specs/ActionTableMCP.idr**: ActionTable API 명세
- **Specs/AutomationMCP.idr**: Automation API 명세 (OLE Object Model)

## 컴파일 체크

### Bash에서 (Claude Code 권장)

```bash
# 전체 스펙 체크
bash check_specs.sh

# 개별 파일 체크
source .bashrc
idris2.sh --check Specs/HwpCommon.idr
```

### 수동 설정 (다른 프로젝트)

다른 프로젝트에서 Idris2를 사용하려면:

1. 프로젝트 루트에 `.bashrc` 생성:
   ```bash
   source /c/Users/joonho.lee/Projects/InstallIdris2/init.sh
   ```

2. 스크립트에서 사용:
   ```bash
   source .bashrc
   idris2.sh --check YourSpec.idr
   ```

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
