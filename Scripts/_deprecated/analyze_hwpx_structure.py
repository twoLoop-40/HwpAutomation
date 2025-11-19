"""
HWPX XML 구조 상세 분석

목표:
1. endNote의 정확한 위치 파악
2. 본문과 미주 영역의 관계 이해
3. 미주 앵커와 미주 내용의 매칭 방법 찾기
"""

import sys
import codecs
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


def analyze_xml_structure(hwpx_path: str):
    """XML 구조 상세 분석"""
    print(f"파일: {Path(hwpx_path).name}\n")

    with zipfile.ZipFile(hwpx_path, 'r') as zf:
        xml_content = zf.read('Contents/section0.xml')
        root = ET.fromstring(xml_content)

        namespaces = {
            'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
            'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
            'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
        }

        print("=== 1. 루트 구조 ===\n")
        print(f"루트 태그: {root.tag}")
        print(f"루트 직계 자식 개수: {len(list(root))}\n")

        # 루트의 직계 자식들
        print("루트의 직계 자식 태그들:")
        for i, child in enumerate(root):
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            print(f"  [{i+1}] {tag} (자손 {len(list(child.iter()))}개)")
            if i >= 10:
                print(f"  ... 외 {len(list(root)) - 11}개")
                break

        print("\n=== 2. 문단(<p>) 분포 ===\n")

        # 모든 문단
        all_paras = root.findall('.//hp:p', namespaces)
        if not all_paras:
            all_paras = root.findall('.//p')

        print(f"전체 문단: {len(all_paras)}개\n")

        # 처음 10개 문단의 부모 확인
        print("처음 10개 문단의 부모:")
        for i, para in enumerate(all_paras[:10]):
            parent = para.getparent() if hasattr(para, 'getparent') else None

            # ElementTree는 getparent() 없음, 수동으로 찾기
            parent_tag = "unknown"
            for elem in root.iter():
                if para in list(elem):
                    parent_tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                    break

            # 문단 내 텍스트
            texts = para.findall('.//hp:t', namespaces)
            if not texts:
                texts = para.findall('.//t')
            para_text = ''.join(t.text for t in texts if t.text)

            print(f"  [{i+1:2d}] 부모: {parent_tag:15s} | {para_text[:60]}")

        print("\n=== 3. endNote 구조 ===\n")

        # 모든 endNote
        endnotes = root.findall('.//hp:endNote', namespaces)
        if not endnotes:
            endnotes = root.findall('.//endNote')

        print(f"총 endNote: {len(endnotes)}개\n")

        # endNote의 위치와 구조
        print("endNote의 부모 및 위치:\n")

        # 첫 5개 endNote
        for i, endnote in enumerate(endnotes[:5]):
            # 부모 찾기
            parent_tag = "unknown"
            for elem in root.iter():
                if endnote in list(elem):
                    parent_tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                    break

            # endNote 내부 문단
            en_paras = endnote.findall('.//hp:p', namespaces)
            if not en_paras:
                en_paras = endnote.findall('.//p')

            # endNote 속성
            attrs = endnote.attrib

            # endNote 텍스트
            texts = endnote.findall('.//hp:t', namespaces)
            if not texts:
                texts = endnote.findall('.//t')
            en_text = ''.join(t.text for t in texts if t.text)

            print(f"[endNote {i+1}]")
            print(f"  부모: {parent_tag}")
            print(f"  속성: {attrs}")
            print(f"  내부 문단: {len(en_paras)}개")
            print(f"  텍스트: {en_text[:80]}")
            print()

        print("=== 4. 본문 영역 vs 미주 영역 ===\n")

        # endNote가 문서의 어디에 배치되어 있는지 확인
        # 방법: 전체 요소를 순회하면서 endNote의 위치 파악

        all_elements = list(root.iter())
        total_elements = len(all_elements)

        # 첫 번째와 마지막 endNote의 위치
        first_endnote_pos = None
        last_endnote_pos = None

        for idx, elem in enumerate(all_elements):
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag == 'endNote':
                if first_endnote_pos is None:
                    first_endnote_pos = idx
                last_endnote_pos = idx

        if first_endnote_pos is not None:
            print(f"전체 요소 수: {total_elements}")
            print(f"첫 endNote 위치: {first_endnote_pos} ({first_endnote_pos/total_elements*100:.1f}%)")
            print(f"마지막 endNote 위치: {last_endnote_pos} ({last_endnote_pos/total_elements*100:.1f}%)")
            print()

            # endNote들이 집중된 영역인지, 분산된 영역인지 확인
            endnote_positions = []
            for idx, elem in enumerate(all_elements):
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                if tag == 'endNote':
                    endnote_positions.append(idx)

            # 앞쪽 10%, 중간, 뒤쪽 10%로 분포 확인
            front_10 = int(total_elements * 0.1)
            back_90 = int(total_elements * 0.9)

            en_in_front = sum(1 for pos in endnote_positions if pos < front_10)
            en_in_middle = sum(1 for pos in endnote_positions if front_10 <= pos < back_90)
            en_in_back = sum(1 for pos in endnote_positions if pos >= back_90)

            print(f"endNote 분포:")
            print(f"  앞쪽 10%: {en_in_front}개")
            print(f"  중간 80%: {en_in_middle}개")
            print(f"  뒤쪽 10%: {en_in_back}개")
            print()

            if en_in_back > en_in_front + en_in_middle:
                print("→ endNote들이 **문서 뒤쪽에 집중**되어 있음")
                print("→ 일반적인 미주 구조: 본문 → 미주 영역\n")
            elif en_in_front > en_in_middle + en_in_back:
                print("→ endNote들이 **문서 앞쪽에 집중**되어 있음\n")
            else:
                print("→ endNote들이 **문서 전체에 분산**되어 있음")
                print("→ 각 문제 내에 미주가 포함된 구조일 가능성\n")

        print("=== 5. 구조 패턴 분석 ===\n")

        # endNote 사이의 요소 개수 확인
        if len(endnote_positions) >= 10:
            print("처음 10개 endNote 사이의 요소 개수:\n")
            for i in range(9):
                gap = endnote_positions[i+1] - endnote_positions[i]
                print(f"  endNote {i+1} → {i+2}: {gap}개 요소")

            avg_gap = sum(endnote_positions[i+1] - endnote_positions[i]
                         for i in range(len(endnote_positions)-1)) / (len(endnote_positions)-1)
            print(f"\n  평균 간격: {avg_gap:.1f}개 요소")

        print("\n=== 6. 결론 및 분리 전략 ===\n")

        if en_in_back > en_in_front + en_in_middle:
            print("📋 구조: 본문 영역 + 미주 영역 분리형")
            print()
            print("분리 전략:")
            print("  1. 첫 endNote 이전까지 = 전체 본문")
            print("  2. 첫 endNote부터 끝까지 = 미주 영역")
            print("  3. 본문에서 미주 앵커(참조) 찾기 필요")
            print("  4. 앵커와 미주 매칭하여 문제 분리")
        else:
            print("📋 구조: 본문-미주 혼합형")
            print()
            print("분리 전략:")
            print("  1. endNote N ~ endNote N+1 사이 = 문제 N")
            print("  2. 각 구간에서 본문 문단만 추출")
            print("  3. endNote 자체는 정답 해설")


if __name__ == "__main__":
    hwpx_file = r"Tests\seperation\6. 명제_2023.hwpx"

    if not Path(hwpx_file).exists():
        print(f"파일이 존재하지 않습니다: {hwpx_file}")
        sys.exit(1)

    analyze_xml_structure(hwpx_file)
