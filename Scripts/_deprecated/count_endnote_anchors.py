"""
본문의 미주 앵커 개수 세기

본문에 있는 미주 참조(en 앵커)를 세어서
실제 문제 개수 확인
"""

import sys
import codecs
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


def count_endnote_anchors(hwpx_path: str):
    """미주 앵커 개수 세기"""
    print(f"파일: {Path(hwpx_path).name}\n")

    with zipfile.ZipFile(hwpx_path, 'r') as zf:
        xml_content = zf.read('Contents/section0.xml')
        root = ET.fromstring(xml_content)

        namespaces = {
            'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
        }

        print("=== 미주 앵커 분석 ===\n")

        # 1. 미주 앵커 찾기 (본문에서 미주로의 참조)
        # 가능한 태그: <endnoteRef>, <en>, 등
        anchor_tags = [
            './/hh:endnoteRef',
            './/endnoteRef',
            './/hh:en',
            './/en',
        ]

        all_anchors = []
        for tag in anchor_tags:
            try:
                elements = root.findall(tag, namespaces)
                if elements:
                    print(f"{tag}: {len(elements)}개 발견")
                    all_anchors.extend(elements)
            except:
                pass

        if not all_anchors:
            # 다른 방법: endNote가 아닌 곳에서 endNote 참조 찾기
            print("직접 앵커 태그를 찾을 수 없습니다.\n")
            print("대안: 본문 영역에서 간접 참조 확인...\n")

        # 2. endNote 영역 (미주 실제 내용)
        endnotes = root.findall('.//hh:endNote', namespaces)
        if not endnotes:
            endnotes = root.findall('.//endNote')

        print(f"\nendNote (미주 내용): {len(endnotes)}개")

        # 3. 앵커와 미주 매칭
        if all_anchors:
            print(f"\n본문 미주 앵커: {len(all_anchors)}개")
            print(f"미주 내용: {len(endnotes)}개")
            print(f"매칭 여부: {'✓ 일치' if len(all_anchors) == len(endnotes) else '✗ 불일치'}")

            # 처음 10개 앵커 정보
            print(f"\n처음 10개 앵커:\n")
            for i, anchor in enumerate(all_anchors[:10]):
                # 앵커 속성 확인
                attrs = anchor.attrib
                print(f"   [{i+1:3d}] 속성: {attrs}")

        # 4. 본문 섹션 분석
        print(f"\n=== 본문 섹션 분석 ===\n")

        # 섹션 찾기
        sections = root.findall('.//hh:section', namespaces)
        if not sections:
            sections = [root]  # 루트가 섹션

        print(f"섹션 수: {len(sections)}개\n")

        for i, section in enumerate(sections[:3]):
            # 이 섹션의 미주 앵커
            section_anchors = []
            for tag in anchor_tags:
                try:
                    elems = section.findall(tag, namespaces)
                    section_anchors.extend(elems)
                except:
                    pass

            # 이 섹션의 endNote
            section_endnotes = section.findall('.//hh:endNote', namespaces)
            if not section_endnotes:
                section_endnotes = section.findall('.//endNote')

            # 이 섹션의 문단
            section_paras = section.findall('.//hh:p', namespaces)

            # 미주 내부 문단 제외
            endnote_paras = []
            for en in section_endnotes:
                paras = en.findall('.//hh:p', namespaces)
                endnote_paras.extend(paras)

            body_paras = len(section_paras) - len(endnote_paras)

            print(f"섹션 {i+1}:")
            print(f"  본문 문단: {body_paras}개")
            print(f"  미주 앵커: {len(section_anchors)}개")
            print(f"  미주 내용: {len(section_endnotes)}개")

        # 5. 최종 결론
        print(f"\n=== 최종 결과 ===\n")

        if all_anchors:
            print(f"본문 미주 앵커 (문제 참조): {len(all_anchors)}개")
        else:
            print(f"미주 앵커를 직접 찾을 수 없음")

        print(f"미주 내용 (endNote): {len(endnotes)}개")

        # [정답] 포함 미주 개수
        answer_endnotes = 0
        for endnote in endnotes:
            texts = endnote.findall('.//hh:t', namespaces)
            if not texts:
                texts = endnote.findall('.//t')
            text = ''.join(t.text for t in texts if t.text)
            if '[정답]' in text:
                answer_endnotes += 1

        print(f"[정답] 포함 미주: {answer_endnotes}개")
        print(f"\n추정: 본문에 {len(all_anchors) if all_anchors else len(endnotes)}개 문제가 있고,")
        print(f"      각 문제마다 미주 참조가 있으며,")
        print(f"      미주 영역에 {answer_endnotes}개의 정답 해설이 있음")


if __name__ == "__main__":
    hwpx_file = r"Tests\seperation\6. 명제_2023.hwpx"

    if not Path(hwpx_file).exists():
        print(f"파일이 존재하지 않습니다: {hwpx_file}")
        sys.exit(1)

    count_endnote_anchors(hwpx_file)
