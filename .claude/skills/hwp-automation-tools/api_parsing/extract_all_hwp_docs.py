"""
모든 HWP API 문서를 텍스트로 추출하고 Idris2 형태로 정리

PDF 파일들:
1. ActionTable_2504.pdf - Action 테이블 (이미 처리됨)
2. HwpAutomation_2504.pdf - Automation API 참조
3. ParameterSetTable_2504.pdf - ParameterSet 테이블
4. 한글오토메이션EventHandler추가_2504.pdf - EventHandler

출력:
- HwpIdris/ActionTable_extracted.txt (이미 존재)
- HwpIdris/Automation_extracted.txt
- HwpIdris/ParameterSet_extracted.txt
- HwpIdris/EventHandler_extracted.txt
"""

import sys
from pathlib import Path

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

try:
    import pdfplumber
except ImportError:
    print('❌ pdfplumber가 설치되지 않았습니다.')
    print('   pip install pdfplumber')
    sys.exit(1)


def extract_pdf_to_text(pdf_path: Path, output_path: Path) -> bool:
    """PDF를 텍스트로 추출"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f'  총 {total_pages}페이지')

            text_parts = []
            for i, page in enumerate(pdf.pages, 1):
                if i % 10 == 0:
                    print(f'    {i}/{total_pages} 페이지 처리 중...')

                text = page.extract_text()
                if text:
                    text_parts.append(text)

            full_text = '\n\n'.join(text_parts)

            # 텍스트 저장
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)

            file_size = output_path.stat().st_size
            print(f'  ✅ 추출 완료: {len(full_text):,}글자, {file_size:,} bytes')
            return True

    except Exception as e:
        print(f'  ❌ 추출 실패: {e}')
        return False


def main():
    print('=' * 70)
    print('HWP API 문서 전체 추출')
    print('=' * 70)

    # PDF 파일 목록
    pdf_files = [
        {
            'name': 'ActionTable_2504.pdf',
            'output': 'ActionTable_extracted.txt',
            'description': 'Action Table (400+ actions)',
            'skip_if_exists': True  # 이미 처리됨
        },
        {
            'name': 'HwpAutomation_2504.pdf',
            'output': 'Automation_extracted.txt',
            'description': 'Automation API Reference'
        },
        {
            'name': 'ParameterSetTable_2504.pdf',
            'output': 'ParameterSet_extracted.txt',
            'description': 'ParameterSet Table'
        },
        {
            'name': '한글오토메이션EventHandler추가_2504.pdf',
            'output': 'EventHandler_extracted.txt',
            'description': 'EventHandler Guide'
        },
    ]

    hwp_books_dir = Path('HwpBooks')
    output_dir = Path('HwpIdris')
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for i, pdf_info in enumerate(pdf_files, 1):
        pdf_path = hwp_books_dir / pdf_info['name']
        output_path = output_dir / pdf_info['output']

        print(f'\n[{i}/{len(pdf_files)}] {pdf_info["description"]}')
        print(f'  PDF: {pdf_path.name}')
        print(f'  출력: {output_path.name}')

        if not pdf_path.exists():
            print(f'  ⚠️  PDF 파일이 없습니다')
            results.append((pdf_info['name'], False))
            continue

        # 이미 처리된 파일 스킵
        if pdf_info.get('skip_if_exists', False) and output_path.exists():
            print(f'  ✅ 이미 추출됨 (스킵)')
            results.append((pdf_info['name'], True))
            continue

        # 추출
        success = extract_pdf_to_text(pdf_path, output_path)
        results.append((pdf_info['name'], success))

    # 결과 요약
    print('\n' + '=' * 70)
    print('추출 결과')
    print('=' * 70)

    for pdf_name, success in results:
        status = '✅' if success else '❌'
        print(f'{status} {pdf_name}')

    success_count = sum(1 for _, s in results if s)
    print(f'\n성공: {success_count}/{len(results)}개')

    print('\n생성된 파일:')
    for txt_file in sorted(output_dir.glob('*_extracted.txt')):
        file_size = txt_file.stat().st_size
        print(f'  {txt_file.name}: {file_size:,} bytes')

    print('=' * 70)


if __name__ == "__main__":
    main()
