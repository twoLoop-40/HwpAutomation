# HWP API 전체 인덱스

출처: HwpBooks/*.pdf

## 1. Action Table

- **파일**: `ActionTable_extracted.txt`
- **Idris2**: `Actions/*.idr` (12 modules, 1,279 actions)
- **용도**: HAction.Run() 명령어 참조

## 2. Automation API

- **파일**: `Automation_extracted.txt`
- **문서**: `Automation/README.md`
- **용도**: OLE Object Model, Properties, Methods

## 3. ParameterSet Table

- **파일**: `ParameterSet_extracted.txt`
- **문서**: `ParameterSets/Index.md`
- **용도**: HParameterSet 항목 참조

## 4. EventHandler

- **파일**: `EventHandler_extracted.txt`
- **용도**: Event 처리 방법

## 빠른 검색

### Action 검색
```bash
grep -i "MoveSelDown" HwpIdris/ActionTable_extracted.txt
grep -i "PageSetup" HwpIdris/Actions/*.idr
```

### ParameterSet 검색
```bash
grep -i "PageDef" HwpIdris/ParameterSet_extracted.txt
```

### Automation Object 검색
```bash
grep -i "PageCount" HwpIdris/Automation_extracted.txt
```
