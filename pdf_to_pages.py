import argparse
import io
from pathlib import Path
from PIL import Image as PILImage
import pytesseract
from pdf2image import convert_from_path

def ocr_scribe_pdf(
    pdf_path: Path,
    page_range: tuple[int, int] | None = None,
    output_dir: Path | None = None,
    split_pages: bool = False,
) -> None:
    """
    Rasterizes PDF pages and performs OCR to capture handwritten Scribe content.
    """
    if not pdf_path.is_file():
        print(f"Error: File not found at '{pdf_path}'")
        return

    output_path = Path(output_dir) if output_dir else Path(pdf_path.stem)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Processing: {pdf_path}")

    # Determine page boundaries
    first_page = page_range[0] if page_range else 1
    last_page = page_range[1] if page_range else None

    try:
        # Convert PDF pages to PIL images at 300 DPI for OCR accuracy
        pages = convert_from_path(
            str(pdf_path),
            dpi=300,
            first_page=first_page,
            last_page=last_page
        )

        all_text_content = []

        for i, img in enumerate(pages):
            actual_page_num = first_page + i
            print(f"  OCR on page {actual_page_num}...")
            
            # Standard OCR call on the full-page raster
            text = pytesseract.image_to_string(img)
            
            page_header = f"--- Page {actual_page_num} ---"
            formatted_content = f"{page_header}\n{text.strip()}\n"
            all_text_content.append(formatted_content)

            if split_pages:
                page_file = output_path / f"page_{actual_page_num}.txt"
                page_file.write_text(text.strip(), encoding="utf-8")

        if not split_pages:
            combined_file = output_path / f"{pdf_path.stem}_combined.txt"
            combined_file.write_text("\n\n".join(all_text_content), encoding="utf-8")
            print(f"Saved: {combined_file}")

    except Exception as e:
        print(f"Processing failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="OCR for Kindle Scribe PDFs.")
    parser.add_argument("pdf_file", help="Path to Scribe PDF")
    parser.add_argument("--range", help="Page range (e.g., 1-5)")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--split", action="store_true", help="One file per page")

    args = parser.parse_args()
    
    p_range = None
    if args.range:
        start, end = map(int, args.range.split("-"))
        p_range = (start, end)

    ocr_scribe_pdf(
        pdf_path=Path(args.pdf_file),
        page_range=p_range,
        output_dir=args.output,
        split_pages=args.split
    )

if __name__ == "__main__":
    main()
