"""
Automation API를 Idris2 형태로 파싱

출처: Automation_extracted.txt
목표: HwpIdris/Automation/*.idr 생성
"""

import sys
import re
from pathlib import Path

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


def parse_automation_objects(text: str) -> dict:
    """Automation Object 목록 추출"""

    # IHwpObject, IXHwpDocuments 등 패턴
    pattern = r'(I\w+)\s+(?:Object|Collection)?'
    matches = re.findall(pattern, text)

    # 중복 제거 및 정렬
    objects = sorted(set(matches))

    return {
        'objects': objects
    }


def generate_automation_idris(objects: list) -> str:
    """Automation API Idris2 코드 생성"""

    idris_code = '''-- HWP Automation API Objects
-- 자동 생성됨: Scripts/parse_automation_api.py

module HwpIdris.Automation.Objects

import Data.String

-- Automation Object 타입
public export
data AutomationObject
'''

    for i, obj in enumerate(objects):
        idris_code += f'    {"=" if i == 0 else "|"} {obj}\n'

    idris_code += '\n-- Object 이름 문자열로 변환\n'
    idris_code += 'public export\n'
    idris_code += 'toString : AutomationObject -> String\n'

    for obj in objects:
        idris_code += f'toString {obj} = "{obj}"\n'

    idris_code += '\n-- Object 설명\n'
    idris_code += 'public export\n'
    idris_code += 'description : AutomationObject -> String\n'

    # 주요 Object에 대한 설명
    descriptions = {
        'IHwpObject': '최상위 Automation Object',
        'IXHwpDocuments': '문서 Collection Object',
        'IXHwpDocument': '단일 문서 Object',
        'IXHwpWindows': '창 Collection Object',
        'IXHwpWindow': '단일 창 Object',
    }

    for obj in objects:
        desc = descriptions.get(obj, 'Automation Object')
        idris_code += f'description {obj} = "{desc}"\n'

    idris_code += f'\n-- 총 {len(objects)}개 Automation Object\n'

    return idris_code


def main():
    print('=' * 70)
    print('Automation API → Idris2 변환')
    print('=' * 70)

    # 입력 파일 읽기
    input_file = Path('HwpIdris/Automation_extracted.txt')

    if not input_file.exists():
        print(f'❌ 파일이 없습니다: {input_file}')
        return

    print(f'\n[1/3] 텍스트 읽기: {input_file}')
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f'  텍스트 길이: {len(text):,}글자')

    # 파싱
    print(f'\n[2/3] Object 추출...')
    result = parse_automation_objects(text)

    objects = result['objects']
    print(f'  발견된 Object: {len(objects)}개')

    for obj in objects[:10]:
        print(f'    - {obj}')

    if len(objects) > 10:
        print(f'    ... 외 {len(objects) - 10}개')

    # Idris2 코드 생성
    print(f'\n[3/3] Idris2 코드 생성...')

    output_dir = Path('HwpIdris/Automation')
    output_dir.mkdir(parents=True, exist_ok=True)

    idris_code = generate_automation_idris(objects)

    output_file = output_dir / 'Objects.idr'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(idris_code)

    print(f'  ✅ {output_file}')

    # 요약
    print('\n' + '=' * 70)
    print('완료!')
    print('=' * 70)
    print(f'생성된 파일: {output_file}')
    print(f'Object 수: {len(objects)}개')
    print('=' * 70)


if __name__ == "__main__":
    main()
