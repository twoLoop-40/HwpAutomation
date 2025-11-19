"""출력 파일을 TXT로 변환해서 확인"""
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

# 첫 번째 출력 파일
hwpx_file = r"Tests\seperation\output_test_new\문제_001-010.hwpx"

if not Path(hwpx_file).exists():
    print(f"파일이 없습니다: {hwpx_file}")
    exit(1)

with zipfile.ZipFile(hwpx_file, 'r') as zf:
    xml_content = zf.read('Contents/section0.xml')
    root = ET.fromstring(xml_content)
    
    ns = {'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}
    text_elements = root.findall('.//hh:t', ns)
    
    full_text = '\n'.join(t.text for t in text_elements if t.text)
    
    # 파일로 저장
    output_txt = r"Tests\seperation\output_test_new\문제_001-010.txt"
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    print(f"저장 완료: {output_txt}")
    print(f"\n첫 2000자:")
    print("="*60)
    print(full_text[:2000])
