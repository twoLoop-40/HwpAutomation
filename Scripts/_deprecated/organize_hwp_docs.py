"""
HWP API 문서를 Idris2/Markdown 형태로 정리

목표:
1. Automation_extracted.txt -> HwpIdris/Automation/ (Object별 정리)
2. ParameterSet_extracted.txt -> HwpIdris/ParameterSets/ (ParameterSet별 정리)
3. 검색 가능한 인덱스 생성

구조:
HwpIdris/
├── Automation/
│   ├── Objects.md - Object 계층 구조
│   ├── Properties.md - Property 목록
│   └── Methods.md - Method 목록
├── ParameterSets/
│   ├── Index.md - ParameterSet 인덱스
│   ├── PageSetup.md
│   ├── MultiColumn.md
│   └── ...
└── API_Index.md - 전체 API 인덱스
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


def organize_automation_api():
    """Automation API 문서 정리"""
    print('\n[1/3] Automation API 정리...')

    automation_file = Path('HwpIdris/Automation_extracted.txt')
    if not automation_file.exists():
        print('  ⚠️  Automation_extracted.txt가 없습니다')
        return

    with open(automation_file, 'r', encoding='utf-8') as f:
        text = f.read()

    output_dir = Path('HwpIdris/Automation')
    output_dir.mkdir(parents=True, exist_ok=True)

    # 간단한 요약 파일 생성
    summary_file = output_dir / 'README.md'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write('# HWP Automation API\n\n')
        f.write('출처: HwpAutomation_2504.pdf\n\n')
        f.write('## 주요 Object\n\n')
        f.write('- **IHwpObject**: 최상위 오브젝트\n')
        f.write('- **IXHwpDocuments**: 문서 Collection\n')
        f.write('- **IXHwpDocument**: 단일 문서\n\n')
        f.write('## 원본 텍스트\n\n')
        f.write('전체 내용은 `../Automation_extracted.txt` 참조\n')

    print(f'  ✅ {summary_file}')


def organize_parameter_sets():
    """ParameterSet 문서 정리"""
    print('\n[2/3] ParameterSet 정리...')

    param_file = Path('HwpIdris/ParameterSet_extracted.txt')
    if not param_file.exists():
        print('  ⚠️  ParameterSet_extracted.txt가 없습니다')
        return

    with open(param_file, 'r', encoding='utf-8') as f:
        text = f.read()

    output_dir = Path('HwpIdris/ParameterSets')
    output_dir.mkdir(parents=True, exist_ok=True)

    # ParameterSet 이름 추출 (숫자) Name : 형식)
    # 예: "1) ActionCrossRef : 상호참조 삽입"
    pattern = r'(\d+)\)\s+(\w+)\s*:\s*(.+)'
    matches = re.findall(pattern, text)

    param_sets = []
    for num, name, description in matches:
        param_sets.append({
            'num': num,
            'name': name,
            'description': description.strip()
        })

    # 인덱스 파일 생성
    index_file = output_dir / 'Index.md'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write('# ParameterSet Index\n\n')
        f.write('출처: ParameterSetTable_2504.pdf\n\n')
        f.write(f'총 {len(param_sets)}개 ParameterSet\n\n')

        f.write('## 목록\n\n')
        for ps in param_sets[:50]:  # 처음 50개만
            f.write(f'{ps["num"]}. **{ps["name"]}**: {ps["description"]}\n')

        if len(param_sets) > 50:
            f.write(f'\n... 외 {len(param_sets) - 50}개\n')

        f.write('\n## 주요 ParameterSet\n\n')

        # 자주 사용하는 ParameterSet 강조
        important_sets = [
            'PageSetup', 'MultiColumn', 'CharShape', 'ParaShape',
            'TableCreate', 'BorderFill', 'InsertPicture'
        ]

        for name in important_sets:
            found = [ps for ps in param_sets if ps['name'] == name]
            if found:
                ps = found[0]
                f.write(f'- **{ps["name"]}** (#{ps["num"]}): {ps["description"]}\n')

        f.write('\n전체 내용은 `../ParameterSet_extracted.txt` 참조\n')

    print(f'  ✅ {index_file}')
    print(f'  발견된 ParameterSet: {len(param_sets)}개')


def create_master_index():
    """전체 API 인덱스 생성"""
    print('\n[3/3] 전체 인덱스 생성...')

    index_file = Path('HwpIdris/API_Index.md')

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write('# HWP API 전체 인덱스\n\n')
        f.write('출처: HwpBooks/*.pdf\n\n')

        f.write('## 1. Action Table\n\n')
        f.write('- **파일**: `ActionTable_extracted.txt`\n')
        f.write('- **Idris2**: `Actions/*.idr` (12 modules, 1,279 actions)\n')
        f.write('- **용도**: HAction.Run() 명령어 참조\n\n')

        f.write('## 2. Automation API\n\n')
        f.write('- **파일**: `Automation_extracted.txt`\n')
        f.write('- **문서**: `Automation/README.md`\n')
        f.write('- **용도**: OLE Object Model, Properties, Methods\n\n')

        f.write('## 3. ParameterSet Table\n\n')
        f.write('- **파일**: `ParameterSet_extracted.txt`\n')
        f.write('- **문서**: `ParameterSets/Index.md`\n')
        f.write('- **용도**: HParameterSet 항목 참조\n\n')

        f.write('## 4. EventHandler\n\n')
        f.write('- **파일**: `EventHandler_extracted.txt`\n')
        f.write('- **용도**: Event 처리 방법\n\n')

        f.write('## 빠른 검색\n\n')
        f.write('### Action 검색\n')
        f.write('```bash\n')
        f.write('grep -i "MoveSelDown" HwpIdris/ActionTable_extracted.txt\n')
        f.write('grep -i "PageSetup" HwpIdris/Actions/*.idr\n')
        f.write('```\n\n')

        f.write('### ParameterSet 검색\n')
        f.write('```bash\n')
        f.write('grep -i "PageDef" HwpIdris/ParameterSet_extracted.txt\n')
        f.write('```\n\n')

        f.write('### Automation Object 검색\n')
        f.write('```bash\n')
        f.write('grep -i "PageCount" HwpIdris/Automation_extracted.txt\n')
        f.write('```\n')

    print(f'  ✅ {index_file}')


def main():
    print('=' * 70)
    print('HWP API 문서 정리')
    print('=' * 70)

    organize_automation_api()
    organize_parameter_sets()
    create_master_index()

    print('\n' + '=' * 70)
    print('완료!')
    print('=' * 70)
    print('\n생성된 파일:')
    print('  HwpIdris/Automation/README.md')
    print('  HwpIdris/ParameterSets/Index.md')
    print('  HwpIdris/API_Index.md')
    print('=' * 70)


if __name__ == "__main__":
    main()
