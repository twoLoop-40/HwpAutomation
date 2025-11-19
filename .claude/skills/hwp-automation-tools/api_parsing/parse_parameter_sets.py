"""
ParameterSet Table을 Idris2 형태로 파싱

출처: ParameterSet_extracted.txt
목표: HwpIdris/ParameterSets/*.idr 생성

구조:
1) ActionCrossRef : 상호참조 삽입
Item ID Type SubType Description
Command PIT_BSTR ※command string 참조

→ Idris2:
data ActionCrossRefParam
    = Command String  -- command string 참조
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


def parse_parameter_sets(text: str) -> list:
    """ParameterSet 파싱"""

    # ParameterSet 헤더 패턴: "숫자) Name : Description"
    header_pattern = r'(\d+)\)\s+(\w+)\s*:\s*(.+?)(?=\n|$)'
    headers = re.findall(header_pattern, text)

    param_sets = []

    for num, name, description in headers:
        param_sets.append({
            'num': int(num),
            'name': name,
            'description': description.strip()
        })

    return param_sets


def generate_parameterset_idris(param_set: dict) -> str:
    """단일 ParameterSet의 Idris2 코드 생성"""

    name = param_set['name']
    description = param_set['description']

    idris_code = f'''-- ParameterSet: {name}
-- {description}
-- 자동 생성됨: Scripts/parse_parameter_sets.py

module HwpIdris.ParameterSets.{name}

import Data.String

-- {name} ParameterSet
public export
record {name}Params where
    constructor Mk{name}Params
    -- TODO: 항목 추가 필요
    -- 원본 문서 참조: ../ParameterSet_extracted.txt

-- 설명
public export
description : String
description = "{description}"
'''

    return idris_code


def generate_all_parametersets_index(param_sets: list) -> str:
    """전체 ParameterSet 인덱스 Idris2 코드 생성"""

    idris_code = '''-- ParameterSet 전체 목록
-- 자동 생성됨: Scripts/parse_parameter_sets.py

module HwpIdris.ParameterSets.All

import Data.String

-- ParameterSet 타입
public export
data ParameterSetType
'''

    for i, ps in enumerate(param_sets[:50]):  # 너무 많으면 50개만
        name = ps['name']
        idris_code += f'    {"=" if i == 0 else "|"} PS_{name}\n'

    if len(param_sets) > 50:
        idris_code += f'    | PS_Other  -- 외 {len(param_sets) - 50}개\n'

    idris_code += '\n-- ParameterSet 이름\n'
    idris_code += 'public export\n'
    idris_code += 'toString : ParameterSetType -> String\n'

    for ps in param_sets[:50]:
        name = ps['name']
        idris_code += f'toString PS_{name} = "{name}"\n'

    if len(param_sets) > 50:
        idris_code += 'toString PS_Other = "Other"\n'

    idris_code += '\n-- ParameterSet 설명\n'
    idris_code += 'public export\n'
    idris_code += 'description : ParameterSetType -> String\n'

    for ps in param_sets[:50]:
        name = ps['name']
        desc = ps['description'].replace('"', '\\"')
        idris_code += f'description PS_{name} = "{desc}"\n'

    if len(param_sets) > 50:
        idris_code += 'description PS_Other = "기타 ParameterSet"\n'

    idris_code += f'\n-- 총 {len(param_sets)}개 ParameterSet\n'

    return idris_code


def main():
    print('=' * 70)
    print('ParameterSet → Idris2 변환')
    print('=' * 70)

    # 입력 파일 읽기
    input_file = Path('HwpIdris/ParameterSet_extracted.txt')

    if not input_file.exists():
        print(f'❌ 파일이 없습니다: {input_file}')
        return

    print(f'\n[1/4] 텍스트 읽기: {input_file}')
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f'  텍스트 길이: {len(text):,}글자')

    # 파싱
    print(f'\n[2/4] ParameterSet 추출...')
    param_sets = parse_parameter_sets(text)

    print(f'  발견된 ParameterSet: {len(param_sets)}개')

    for ps in param_sets[:10]:
        print(f'    {ps["num"]:3d}. {ps["name"]:20s} - {ps["description"][:40]}...')

    if len(param_sets) > 10:
        print(f'    ... 외 {len(param_sets) - 10}개')

    # 주요 ParameterSet만 개별 파일 생성
    important_sets = [
        'PageSetup', 'MultiColumn', 'CharShape', 'ParaShape',
        'TableCreate', 'BorderFill', 'InsertPicture',
        'ColDef', 'SecDef', 'FieldCtrl'
    ]

    print(f'\n[3/4] 주요 ParameterSet Idris2 코드 생성...')

    output_dir = Path('HwpIdris/ParameterSets')
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_count = 0

    for ps in param_sets:
        if ps['name'] in important_sets:
            idris_code = generate_parameterset_idris(ps)
            output_file = output_dir / f"{ps['name']}.idr"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(idris_code)

            print(f'  ✅ {output_file.name}')
            generated_count += 1

    # 전체 인덱스 생성
    print(f'\n[4/4] 전체 인덱스 생성...')

    index_code = generate_all_parametersets_index(param_sets)
    index_file = output_dir / 'All.idr'

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_code)

    print(f'  ✅ {index_file.name}')

    # 요약
    print('\n' + '=' * 70)
    print('완료!')
    print('=' * 70)
    print(f'총 ParameterSet: {len(param_sets)}개')
    print(f'생성된 개별 파일: {generated_count}개')
    print(f'인덱스 파일: All.idr ({min(50, len(param_sets))}개 포함)')
    print(f'출력 디렉토리: {output_dir}')
    print('=' * 70)


if __name__ == "__main__":
    main()
