"""
ActionTable_extracted.txt 파싱 및 주제별 Idris2 명세 생성

주제별 분류:
1. Navigation (Move*, MoveSel*)
2. Selection (Select*, Cancel)
3. Text (Insert*, Delete*, Break*)
4. Format (CharShape*, ParaShape*, Style*)
5. File (File*, Save*, Open*)
6. Table (Table*, Cell*)
7. Find/Replace (Find*, Replace*)
8. Document (Doc*, Page*, Section*)
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


# 주제별 패턴
CATEGORIES = {
    'Navigation': ['Move', 'MoveSel', 'Jump', 'Goto'],
    'Selection': ['Select', 'Cancel'],
    'Text': ['Insert', 'Delete', 'Break', 'Type'],
    'Format': ['CharShape', 'ParaShape', 'Style', 'Font', 'Color'],
    'File': ['File', 'Save', 'Open', 'Close', 'Load'],
    'Table': ['Table', 'Cell', 'Row', 'Column'],
    'FindReplace': ['Find', 'Replace', 'Search'],
    'Document': ['Doc', 'Page', 'Section', 'Paper'],
    'Shape': ['Shape', 'Object', 'Picture', 'Image'],
    'Field': ['Field', 'MailMerge'],
}


def parse_action_line(line: str) -> dict:
    """액션 라인 파싱"""
    # Format: ActionID ParameterSetID Description 비고
    parts = line.split()

    if len(parts) < 2:
        return None

    action_id = parts[0]

    # ParameterSetID 파싱 (-, +, *, 또는 실제 ID)
    param_id_idx = 1
    param_id = parts[param_id_idx]

    # Description은 나머지 부분
    description_parts = parts[param_id_idx + 1:]
    description = ' '.join(description_parts) if description_parts else ""

    return {
        'action_id': action_id,
        'param_id': param_id,
        'description': description,
    }


def categorize_action(action_id: str) -> str:
    """액션을 주제별로 분류"""
    for category, patterns in CATEGORIES.items():
        for pattern in patterns:
            if action_id.startswith(pattern):
                return category

    return 'Misc'


def parse_action_table(text: str) -> dict:
    """ActionTable 텍스트 파싱"""
    lines = text.split('\n')

    actions_by_category = defaultdict(list)

    for line in lines:
        line = line.strip()

        # 빈 줄이나 헤더 스킵
        if not line or line.startswith('Action ID') or line.startswith('※') or line.startswith('Symbol'):
            continue

        # 숫자로만 이루어진 줄 스킵 (페이지 번호)
        if line.isdigit():
            continue

        # 액션 라인 파싱 시도
        action = parse_action_line(line)

        if action and action['action_id']:
            category = categorize_action(action['action_id'])
            actions_by_category[category].append(action)

    return dict(actions_by_category)


def generate_idris_for_category(category: str, actions: list) -> str:
    """주제별 Idris2 명세 생성"""

    # 액션 이름을 Idris2 생성자로 변환 (첫 글자 대문자 유지)
    action_constructors = []
    seen_constructors = set()

    # Idris2 예약어
    RESERVED_WORDS = ['if', 'then', 'else', 'case', 'of', 'let', 'in', 'do', 'where',
                      'data', 'type', 'record', 'interface', 'implementation', 'module',
                      'import', 'export', 'public', 'private', 'namespace', 'mutual',
                      'covering', 'total', 'partial']

    for action in actions:
        action_id = action['action_id']
        # 특수문자 제거
        clean_id = re.sub(r'[^a-zA-Z0-9_]', '', action_id)

        # 빈 문자열 또는 첫 글자가 숫자이거나 예약어인 경우 스킵
        if not clean_id or not clean_id[0].isalpha() or len(clean_id) < 2:
            continue

        # 예약어인 경우 접미사 추가
        if clean_id.lower() in RESERVED_WORDS:
            clean_id = f'{clean_id}Action'

        if clean_id and clean_id[0].isalpha():
            # 중복 체크
            if clean_id not in seen_constructors:
                action_constructors.append((clean_id, action))
                seen_constructors.add(clean_id)
            else:
                # 중복된 경우 숫자 추가
                counter = 2
                while f"{clean_id}{counter}" in seen_constructors:
                    counter += 1
                unique_id = f"{clean_id}{counter}"
                action_constructors.append((unique_id, action))
                seen_constructors.add(unique_id)

    # Idris2 코드 생성
    idris_code = f'''-- HWP Action Table - {category}
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.{category}

import Data.String

-- {category} 액션 타입
public export
data {category}Action
'''

    # 생성자들
    for i, (constructor, action) in enumerate(action_constructors):
        idris_code += f'    {"=" if i == 0 else "|"} {constructor}'
        if action['description']:
            idris_code += f'  -- {action["description"]}'
        idris_code += '\n'

    idris_code += '\n-- 액션 ID 문자열로 변환\n'
    idris_code += 'public export\n'
    idris_code += f'toString : {category}Action -> String\n'

    for constructor, action in action_constructors:
        idris_code += f'toString {constructor} = "{action["action_id"]}"\n'

    idris_code += '\n-- ParameterSet ID\n'
    idris_code += 'public export\n'
    idris_code += f'paramSetID : {category}Action -> Maybe String\n'

    for constructor, action in action_constructors:
        param_id = action['param_id']
        if param_id == '-':
            idris_code += f'paramSetID {constructor} = Nothing\n'
        elif param_id in ['+', '*']:
            idris_code += f'paramSetID {constructor} = Just "{param_id}"  -- Internal\n'
        else:
            idris_code += f'paramSetID {constructor} = Just "{param_id}"\n'

    idris_code += '\n-- 설명\n'
    idris_code += 'public export\n'
    idris_code += f'description : {category}Action -> String\n'

    for constructor, action in action_constructors:
        desc = action['description'].replace('"', '\\"') if action['description'] else 'No description'
        idris_code += f'description {constructor} = "{desc}"\n'

    idris_code += f'\n-- 총 {len(action_constructors)}개 {category} 액션\n'

    return idris_code


def main():
    print('=' * 70)
    print('ActionTable 파싱 및 Idris2 명세 생성')
    print('=' * 70)

    # ActionTable 텍스트 읽기
    input_file = Path("HwpIdris/ActionTable_extracted.txt")

    if not input_file.exists():
        print(f'❌ 파일이 없습니다: {input_file}')
        return

    print(f'\n[1/3] ActionTable 텍스트 읽기: {input_file}')
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f'텍스트 길이: {len(text):,} 글자')

    # 파싱
    print(f'\n[2/3] ActionTable 파싱...')
    actions_by_category = parse_action_table(text)

    print(f'분류된 카테고리: {len(actions_by_category)}개')
    for category, actions in sorted(actions_by_category.items()):
        print(f'  {category:15s}: {len(actions):3d}개')

    # Idris2 명세 생성
    print(f'\n[3/3] Idris2 명세 생성...')

    output_dir = Path("HwpIdris/Actions")
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []

    for category, actions in sorted(actions_by_category.items()):
        if not actions:
            continue

        idris_code = generate_idris_for_category(category, actions)

        output_file = output_dir / f"{category}.idr"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(idris_code)

        generated_files.append(output_file)
        print(f'  ✅ {output_file.name}: {len(actions)}개 액션')

    # 통합 모듈 생성
    print(f'\n[4/4] 통합 모듈 생성...')

    all_module_code = f'''-- HWP Action Table - 전체 액션
-- 자동 생성됨: Scripts/parse_action_table.py

module HwpIdris.Actions.All

'''

    for category in sorted(actions_by_category.keys()):
        if actions_by_category[category]:
            all_module_code += f'import public HwpIdris.Actions.{category}\n'

    all_module_code += f'''
-- 총 {sum(len(actions) for actions in actions_by_category.values())}개 액션
-- 분류: {len(actions_by_category)}개 카테고리
'''

    all_module_file = output_dir / "All.idr"
    with open(all_module_file, 'w', encoding='utf-8') as f:
        f.write(all_module_code)

    print(f'  ✅ {all_module_file.name}')

    # 요약
    print('\n' + '=' * 70)
    print('완료!')
    print('=' * 70)
    print(f'생성된 파일: {len(generated_files) + 1}개')
    print(f'총 액션 수: {sum(len(actions) for actions in actions_by_category.values())}개')
    print(f'출력 디렉토리: {output_dir}')
    print('=' * 70)

    return generated_files


if __name__ == "__main__":
    main()
