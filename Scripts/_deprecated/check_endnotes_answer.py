"""미주에 [정답]이 있는지 확인"""
import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('Tests/seperation/6. 명제_2023.hwpx', 'r') as zf:
    xml_content = zf.read('Contents/section0.xml')
    root = ET.fromstring(xml_content)
    
    endnotes = [elem for elem in root.iter() if elem.tag.split('}')[-1] == 'endNote']
    
    print(f'총 미주 개수: {len(endnotes)}')
    print()
    
    # [정답]이 없는 미주 찾기
    no_answer = []
    for i, endnote in enumerate(endnotes, 1):
        text = ''.join(endnote.itertext())
        if '[정답]' not in text:
            no_answer.append((i, text[:100]))
    
    if no_answer:
        print(f'[정답]이 없는 미주: {len(no_answer)}개\n')
        for num, text in no_answer[:20]:
            print(f'  미주 {num}: {text}')
    else:
        print('[정답]이 없는 미주: 없음')
        print('→ 모든 408개 미주에 [정답]이 포함되어 있습니다.')
