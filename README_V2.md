# HwpAutomation v2.0

확장 가능한 HWP 자동화 플랫폼

## 🎯 프로젝트 개요

HwpAutomation은 한글(HWP) 문서를 자동화하는 플러그인 기반 플랫폼입니다.

### 주요 특징

- ✅ **플러그인 아키텍처**: 자동화 작업을 독립적인 플러그인으로 추가
- ✅ **공통 Core API**: 모든 플러그인이 공유하는 HWP API 래퍼
- ✅ **Tkinter UI**: 플러그인 선택 및 실행을 위한 GUI
- ✅ **타입 안전성**: Idris2 형식 명세 기반
- ✅ **Python 3.13**: 최신 Python 기능 활용

## 📁 프로젝트 구조

```
HwpAutomation/
├── core/                    # 공통 HWP API 래퍼
│   ├── hwp_client.py       # pywin32 COM 클라이언트
│   ├── automation_client.py # Automation API
│   ├── types.py            # 공통 타입
│   └── sync.py             # 동기화 유틸
│
├── automations/             # 플러그인 디렉토리
│   ├── base.py             # AutomationBase 추상 클래스
│   ├── registry.py         # 플러그인 레지스트리
│   │
│   ├── merger/             # 문제 파일 병합 플러그인
│   │   ├── plugin.py
│   │   ├── merger.py
│   │   └── ...
│   │
│   └── mcp/                # MCP 서버 플러그인
│       ├── plugin.py
│       ├── server.py
│       └── tools.py
│
├── ui/                      # Tkinter 런처
│   └── main.py
│
├── HwpIdris/                # Idris2 형식 명세
│   └── V2/
│
└── tests/                   # 테스트
```

## 🚀 시작하기

### 1. 설치

```bash
# uv 사용 (권장)
uv pip install -e .

# 또는 pip
pip install -e .
```

### 2. UI 런처 실행

```bash
python -m ui.main
```

플러그인 카드가 표시되고, 선택하여 실행할 수 있습니다.

### 3. CLI에서 플러그인 직접 실행

**Merger 플러그인 (문제 파일 병합)**:
```python
from automations.merger import MergerPlugin

plugin = MergerPlugin()
result = plugin.run(
    csv_path="problems.csv",
    template_path="template.hwp",
    output_path="output.hwp",
    parallel=True
)
print(result)
```

**MCP 서버 플러그인**:
```bash
python -m automations.mcp.server
```

## 🔌 플러그인 개발

새로운 플러그인을 추가하려면:

### 1. 플러그인 디렉토리 생성

```
automations/
└── my_plugin/
    ├── __init__.py
    ├── plugin.py
    └── ...
```

### 2. AutomationBase 상속

```python
from automations import AutomationBase, PluginMetadata, register_plugin

@register_plugin
class MyPlugin(AutomationBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="my_plugin",
            name="My Plugin",
            description="플러그인 설명",
            version="1.0.0",
            author="Your Name"
        )

    def run(self, **kwargs):
        # 플러그인 로직
        return {
            "success": True,
            "message": "완료"
        }
```

### 3. UI에서 자동으로 표시됨!

플러그인을 import하면 자동으로 레지스트리에 등록되고 UI에 표시됩니다.

## 📦 기본 제공 플러그인

### 1. Merger (문제 파일 병합)
- **ID**: `merger`
- **기능**: HWP 문제 파일들을 2단 편집 양식으로 병합
- **UI**: ✅ 있음
- **CLI**: ✅ 있음

### 2. MCP Server
- **ID**: `mcp`
- **기능**: Claude Desktop 통합을 위한 MCP 서버
- **UI**: ❌ 없음
- **CLI**: ✅ 있음

## 🛠️ 개발

### Idris2 명세 컴파일

```bash
cd HwpIdris/V2
idris2 --check Main.idr
```

### 테스트 실행

```bash
pytest tests/
```

## 📝 라이선스

MIT License

## 🙋 기여

이슈 및 Pull Request 환영합니다!

---

**v2.0.0** - 플러그인 아키텍처로 전면 재설계
이전 버전: AppV1 (병합 기능만), src (MCP만)
