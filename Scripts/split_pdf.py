"""
PDF 파일을 작은 파일로 분할

Usage:
    python Scripts/split_pdf.py
"""

from pathlib import Path

try:
    import PyPDF2
except ImportError:
    print("❌ PyPDF2가 필요합니다")
    print("설치: pip install PyPDF2")
    exit(1)


def split_pdf(input_path: str, output_dir: str, pages_per_file: int = 50):
    """PDF를 여러 개의 작은 PDF로 분할"""
    
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {input_path}")
        return
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    print(f"📄 PDF 읽기: {input_path}")
    
    with open(input_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        total_pages = len(reader.pages)
        
        print(f"📊 총 {total_pages} 페이지")
        print(f"📦 {pages_per_file} 페이지씩 분할...")
        
        chunk_num = 1
        for start in range(0, total_pages, pages_per_file):
            end = min(start + pages_per_file, total_pages)
            
            writer = PyPDF2.PdfWriter()
            
            for page_num in range(start, end):
                writer.add_page(reader.pages[page_num])
            
            output_file = output_path / f"parameter_table_part{chunk_num}_p{start+1}-{end}.pdf"
            
            with open(output_file, 'wb') as output:
                writer.write(output)
            
            print(f"  ✅ Part {chunk_num}: {output_file.name} ({end-start} 페이지)")
            chunk_num += 1
        
        print(f"\n🎉 완료! 총 {chunk_num-1}개 파일 생성")
        print(f"📁 저장 위치: {output_path.absolute()}")


if __name__ == "__main__":
    # 설정
    INPUT_PDF = "HwpBooks/ParameterSetTable_2504.pdf"
    OUTPUT_DIR = "HwpBooks/ParameterTable_Chunks"
    PAGES_PER_FILE = 50
    
    print("=" * 60)
    print("PDF 분할 도구")
    print("=" * 60)
    
    split_pdf(INPUT_PDF, OUTPUT_DIR, PAGES_PER_FILE)

