"""
HWPX에서 EndNote 참조 찾기

EndNote 컨트롤이 아니라 EndNote 참조 마크를 찾습니다.
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

    # 모든 태그 검색
    all_elements = list(root.iter())

    print(f"총 XML 요소: {len(all_elements):,}개\n")

    # EndNote 관련 태그 찾기
    endnote_tags = {}
    for elem in all_elements:
        tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

        if 'note' in tag_name.lower() or 'ref' in tag_name.lower():
            if tag_name not in endnote_tags:
                endnote_tags[tag_name] = 0
            endnote_tags[tag_name] += 1

    print("EndNote 관련 태그:")
    for tag, count in sorted(endnote_tags.items()):
        print(f"  {tag}: {count}개")

    print("\n\n=== EndNote 컨트롤 샘플 ===\n")

    # endNote 태그 샘플 출력
    endnote_elems = [e for e in all_elements if e.tag.endswith('endNote')]
    print(f"총 {len(endnote_elems)}개\n")

    for i, elem in enumerate(endnote_elems[:3], 1):
        print(f"EndNote {i}:")
        print(f"  Attributes: {elem.attrib}")

        # 하위 요소
        for child in elem:
            child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            print(f"    - {child_tag}: {child.attrib}")

        print()

    print("\n=== EndNote 참조 마크 (noteMarker) 샘플 ===\n")

    # noteMarker 찾기
    note_markers = [e for e in all_elements if 'noteMarker' in e.tag or 'NoteMarker' in e.tag]
    print(f"총 {len(note_markers)}개\n")

    if note_markers:
        for i, elem in enumerate(note_markers[:10], 1):
            print(f"NoteMarker {i}:")
            print(f"  Tag: {elem.tag}")
            print(f"  Attributes: {elem.attrib}")
            print(f"  Text: {elem.text}")
            print()
