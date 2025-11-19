"""HWPX에서 EndNote 앵커 찾기"""
import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('Tests/seperation/6. 명제_2023.hwpx', 'r') as z:
    xml_content = z.read('Contents/section0.xml').decode('utf-8')

root = ET.fromstring(xml_content)
all_elems = list(root.iter())

print(f'전체 요소 수: {len(all_elems)}\n')

# EndNote들의 instId 수집
endnote_map = {}
for i, elem in enumerate(all_elems):
    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
    if tag == 'endNote':
        number = elem.get('number')
        inst_id = elem.get('instId')
        endnote_map[inst_id] = (number, i)

print(f'EndNote 개수: {len(endnote_map)}\n')

# instId로 앵커 찾기 (본문에서)
print('앵커 위치 찾기 (instId 매칭):')
anchor_found = {}
for i, elem in enumerate(all_elems[:50000]):  # 본문 영역만
    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

    # ctrl 태그에서 instId 찾기
    if tag == 'ctrl':
        ctrl_inst_id = elem.get('id')
        if ctrl_inst_id and ctrl_inst_id in endnote_map:
            number, endnote_idx = endnote_map[ctrl_inst_id]
            anchor_found[number] = i
            if len(anchor_found) <= 10:
                print(f'EndNote {number}: 앵커 index={i}, EndNote index={endnote_idx}')

print(f'\n총 {len(anchor_found)}개 앵커 발견')
