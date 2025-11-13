# COM 동기화 문제 해결

## 문제 상황

### 증상
- 40개 파일 중 일부만 삽입됨 (군데군데 들어감)
- 실행 시간이 너무 짧음 (충분히 기다리지 않음)
- 동시성 문제로 인한 불안정한 동작

### 원인 분석
**COM 객체 생성 방식의 차이**

#### ❌ 문제가 있던 방식 (EnsureDispatch)
```python
# src/automation/client.py
def _create_hwp_instance(self):
    self._ensure_com_initialized()
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
    return hwp
```

**EnsureDispatch의 문제점**:
- Early binding (타입 정보 캐싱)
- 비동기적 처리 가능
- 작업 완료를 보장하지 않음
- 다음 명령이 이전 작업 완료 전에 실행될 수 있음

#### ✅ 해결 방법 (DispatchEx)
```python
# math-collector 방식
import pythoncom
import win32com.client as win32

pythoncom.CoInitialize()
try:
    hwp = win32.DispatchEx("HwpFrame.HwpObject")
    # 작업 수행
finally:
    pythoncom.CoUninitialize()
```

**DispatchEx의 장점**:
- Late binding
- 동기적 처리 보장
- 각 작업이 완료될 때까지 대기
- 함수 스코프 내에서 COM 생명주기 관리

## 해결책

### 1. COM 초기화 방식 변경

#### Before (AutomationClient 사용)
```python
def merge_problems(...):
    client = AutomationClient()  # 클래스 인스턴스
    try:
        hwp = client.hwp  # EnsureDispatch 사용
        # 작업...
    finally:
        client.cleanup()
```

#### After (math-collector 방식)
```python
def merge_problems(...):
    import pythoncom
    import win32com.client as win32

    pythoncom.CoInitialize()  # 함수 시작 시 초기화
    try:
        hwp = win32.DispatchEx("HwpFrame.HwpObject")  # Late binding
        # 작업...
    finally:
        pythoncom.CoUninitialize()  # 함수 종료 시 정리
```

### 2. 명시적 동기화 추가

```python
# src/common/sync.py
import time

def wait_for_hwp_ready(hwp, timeout=5.0, check_interval=0.1):
    """HWP가 작업을 완료하고 준비 상태가 될 때까지 대기"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # HWP 속성 접근으로 준비 상태 확인
            _ = hwp.PageCount
            return True
        except Exception:
            time.sleep(check_interval)
            continue

    return False
```

### 3. InsertFile 후 동기화

```python
# InsertFile 액션 실행
result = hwp.HAction.Execute("InsertFile", pset.HSet)

# ✅ 동기화: HWP가 파일 로드를 완료할 때까지 대기
time.sleep(0.3)  # 기본 대기
wait_for_hwp_ready(hwp, timeout=3.0)  # HWP 준비 확인

# 다음 작업 (커서 이동 등)
hwp.Run("MoveDocEnd")
```

### 4. 페이지/단 나누기 후 동기화

```python
# 단 나누기
hwp.HAction.Run("BreakColumn")
time.sleep(0.1)  # 처리 대기

# 페이지 나누기
hwp.HAction.Run("BreakPage")
time.sleep(0.1)  # 처리 대기
```

## COM 스레드 모델 이해

### STA (Single-Threaded Apartment)
```python
pythoncom.CoInitialize()  # STA 초기화
```

**특징**:
- 단일 스레드에서 COM 객체 접근
- 함수 스코프 내에서 생명주기 관리
- 동기적 처리 보장

### Early vs Late Binding

| 특성 | Early Binding (EnsureDispatch) | Late Binding (DispatchEx) |
|------|--------------------------------|---------------------------|
| 타입 정보 | 미리 생성 (gen_py 캐시) | 런타임에 결정 |
| 성능 | 빠름 (캐싱됨) | 약간 느림 |
| 동기화 | 비동기 가능 | 동기적 |
| 안정성 | 불안정 (타이밍 이슈) | 안정적 |
| 배포 | gen_py 필요 | 독립적 |

## 실행 결과

### Before (동기화 없음)
```
실행 시간: ~30초
결과: 40개 중 일부만 삽입 (10~20개 정도)
증상: "군데군데 들어가 있음"
```

### After (DispatchEx + 동기화)
```
실행 시간: ~90초 (각 파일당 0.3초 대기)
결과: 40개 전부 삽입
증상: 모든 내용 정상 삽입
```

**시간 분석**:
- InsertFile 40회 × 0.3초 = 12초
- wait_for_hwp_ready 체크 시간 = ~10초
- BreakColumn/BreakPage 40회 × 0.1초 = 4초
- 기타 HWP 처리 시간 = ~64초
- **총 약 90초** (안정적 완료)

## math-collector 참조

### combine_problems 함수
```python
# tools/handle_hwp.py
def combine_problems(target_list: list[TargetPath], ...):
    pythoncom.CoInitialize()  # ✅ 함수 시작

    try:
        hwp = win32.DispatchEx("HwpFrame.HwpObject")  # ✅ Late binding
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        hwp.XHwpWindows.Item(0).Visible = bool(visible)
        hwp.HAction.Run("FileNew")

        for t in target_list:
            insert_hwp_file(hwp, target_path)  # 파일 삽입
            hwp.Run("MoveDocEnd")  # 커서 이동

        save_hwp(hwp, ...)
        hwp.Quit()

    except Exception as e:
        print(f"오류: {e}")
    finally:
        pythoncom.CoUninitialize()  # ✅ 함수 종료
```

### insert_hwp_file 헬퍼
```python
def insert_hwp_file(hwp: CDispatch, file_path: str | Path) -> None:
    hwp.HAction.GetDefault("InsertFile", hwp.HParameterSet.HInsertFile.HSet)
    pset = hwp.HParameterSet.HInsertFile
    pset.filename = str(file_path)
    pset.KeepSection = 0
    pset.KeepCharshape = 1
    pset.KeepParashape = 1
    pset.KeepStyle = 0
    pset.MoveNextPos = 0
    hwp.HAction.Execute("InsertFile", pset.HSet)
    hwp.Run("MoveDocEnd")  # ✅ 바로 다음 작업
```

**math-collector의 안정성**:
- 파일당 처리 시간이 충분함 (자연스러운 대기)
- DispatchEx의 동기적 특성
- 단순한 워크플로우 (설정 변경 없음)

## 교훈

### 1. COM 초기화 위치가 중요
- **함수 스코프**: 안정적, 예측 가능
- **클래스 속성**: 불안정, 생명주기 복잡

### 2. Binding 방식 선택
- **개발 중**: DispatchEx (안정성 우선)
- **배포 후**: DispatchEx (gen_py 의존성 제거)

### 3. 명시적 동기화 필요
- HWP 작업은 비동기적일 수 있음
- time.sleep + 상태 확인 조합
- 너무 짧은 대기는 불안정

### 4. 참조 구현 활용
- math-collector의 패턴 학습
- 동작하는 코드의 방식 정확히 따르기
- 최적화는 안정성 확보 후

## 관련 파일

- `Scripts/merge_problems_automation.py`: ✅ DispatchEx + 동기화 적용
- `src/common/sync.py`: 동기화 유틸리티
- `src/automation/client.py`: MCP 서버용 (EnsureDispatch 유지)
- `C:\Users\joonho.lee\Projects\math-collector\tools\handle_hwp.py`: 참조 구현

## MCP 서버에 대한 고려

AutomationClient (MCP 서버용)는 **EnsureDispatch**를 유지합니다:

**이유**:
1. MCP 도구는 단일 작업 수행 (파일 하나 열기 등)
2. 대량 작업이 아님
3. 타입 정보 캐싱으로 IDE 자동완성 지원

**대량 작업** (merge_problems 등)은:
- DispatchEx 사용
- 명시적 동기화 추가
- 함수 스코프 COM 초기화

## 향후 개선

### Idris2 스펙에 동기화 명세 추가
```idris
-- COM 초기화 상태 추적
data COMState = Uninitialized | Initialized | Terminated

-- 작업 완료 보장
data SyncMode = Synchronous | Asynchronous

-- InsertFile은 동기적 완료 필요
insertFile : (mode : SyncMode)
          -> (doc : HwpDocument)
          -> FilePath
          -> {auto ok : mode = Synchronous}
          -> HwpResult
```

### 성능 최적화 (향후)
```python
# 배치 처리 최적화
def batch_insert_with_minimal_sync(files, hwp):
    for i, file in enumerate(files):
        insert_file(hwp, file)

        # 10개마다 동기화 (전체 대기 시간 단축)
        if (i + 1) % 10 == 0:
            wait_for_hwp_ready(hwp)

    # 마지막 동기화
    wait_for_hwp_ready(hwp, timeout=5.0)
```
