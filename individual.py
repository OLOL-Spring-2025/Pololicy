import os
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
from pathlib import Path

# Set Tesseract OCR path (Only needed for Windows users)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update path if necessary

# Set Poppler path (Only needed for Windows users)
POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"  # Update this if needed

def extract_text_via_ocr(pdf_path):
    """ Extracts text from scanned PDFs using OCR. """
    print(f"Performing OCR on scanned PDF: {pdf_path}")
    text = ""
    try:
        # Set the path to Poppler binaries (ONLY needed on Windows)
        # Convert PDF to images
        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)

        # Process images for OCR
        for img in images:
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
            text += pytesseract.image_to_string(img_cv) + "\n"
    except Exception as e:
        print(f"OCR Error: {e}")
    return text


if __name__ == "__main__":
    # Set file paths
    input_pdf = "OneDrive Feb 12 2025\Environment of Care\Medical Equipment\TriMedx Policies\TMX-SOP-0089 Alerts and Recalls Management.pdf"
    output_txt = Path(input_pdf).stem + ".txt"  # Generates output filename

    text = extract_text_via_ocr(input_pdf)
    if text!="":
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(text)



