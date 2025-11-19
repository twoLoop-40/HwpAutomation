"""
HWPX에서 미주 개수 세기

endNote 태그 기반으로 실제 미주 개수 확인
"""

import sys
import codecs
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


def count_endnotes(hwpx_path: str):
    """미주 개수 세기"""
    print(f"파일: {Path(hwpx_path).name}\n")

    with zipfile.ZipFile(hwpx_path, 'r') as zf:
        xml_content = zf.read('Contents/section0.xml')
        root = ET.fromstring(xml_content)

        # 네임스페이스
        namespaces = {
            'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
            'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
        }

        print("=== 미주 태그 검색 ===\n")

        # endNote 태그 찾기
        endnotes = root.findall('.//hh:endNote', namespaces)
        if not endnotes:
            endnotes = root.findall('.//endNote')

        print(f"endNote 태그: {len(endnotes)}개\n")

        if endnotes:
            print(f"처음 10개 미주 내용:\n")
            for i, endnote in enumerate(endnotes[:10]):
                # 미주 내 텍스트 추출
                texts = endnote.findall('.//hh:t', namespaces)
                if not texts:
                    texts = endnote.findall('.//t')

                endnote_text = ''.join(t.text for t in texts if t.text)
                print(f"[미주 {i+1:3d}] {endnote_text[:100]}")

            if len(endnotes) > 10:
                print(f"\n... 외 {len(endnotes) - 10}개")

        print(f"\n✓ 총 미주 개수: {len(endnotes)}개")
        return len(endnotes)


if __name__ == "__main__":
    hwpx_file = r"Tests\seperation\6. 명제_2023.hwpx"

    if not Path(hwpx_file).exists():
        print(f"파일이 존재하지 않습니다: {hwpx_file}")
        sys.exit(1)

    count = count_endnotes(hwpx_file)
