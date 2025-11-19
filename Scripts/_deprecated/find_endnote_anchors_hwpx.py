"""
HWPX에서 EndNote 앵커(참조 마크) 찾기

본문에 있는 EndNote 참조 마크를 찾아서 문제 경계로 사용
"""
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

test_file = r"Tests\seperation\6. 명제_2023.hwpx"

print(f"파일: {Path(test_file).name}\n")

with zipfile.ZipFile(test_file, 'r') as zf:
    section_files = [f for f in zf.namelist() if 'section' in f.lower() and f.startswith('Contents/')]
    xml_content = zf.read(sorted(section_files)[0])
    root = ET.fromstring(xml_content)

    # 모든 요소 확인
    all_elements = list(root.iter())

    # 'NOTEREF' 또는 앵커 관련 검색
    anchor_types = {}
    for elem in all_elements:
        tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

        # ctrl 태그 확인 (컨트롤)
        if tag_name == 'ctrl':
            ctrl_id = elem.attrib.get('id', '')
            if ctrl_id not in anchor_types:
                anchor_types[ctrl_id] = 0
            anchor_types[ctrl_id] += 1

    print("=== 컨트롤 타입별 개수 ===\n")
    for ctrl_id, count in sorted(anchor_types.items(), key=lambda x: -x[1]):
        print(f"  {ctrl_id}: {count}개")

    print("\n\n=== 'noteref' 컨트롤 샘플 ===\n")

    # noteref 컨트롤 찾기
    noteref_ctrls = [e for e in all_elements
                     if e.tag.endswith('ctrl') and 'noteref' in e.attrib.get('id', '').lower()]

    print(f"총 {len(noteref_ctrls)}개\n")

    if noteref_ctrls:
        for i, elem in enumerate(noteref_ctrls[:10], 1):
            print(f"NoteRef {i}:")
            print(f"  Attributes: {elem.attrib}")

            # 부모 문단 찾기
            parent = elem
            for _ in range(5):
                parent = [p for p in all_elements if elem in list(p.iter())][0]
                parent_tag = parent.tag.split('}')[-1] if '}' in parent.tag else parent.tag
                if parent_tag == 'p':
                    # 문단 텍스트 추출
                    texts = [t.text for t in parent.iter() if t.text and len(t.text.strip()) > 0]
                    context = ' '.join(texts[:5])
                    print(f"  Context: {context[:100]}...")
                    break

            print()
