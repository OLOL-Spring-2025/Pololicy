import os
import comtypes.client
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
from pypdf import PdfReader
from fpdf import FPDF
import pandas as pd
from docx import Document
from docx2pdf import convert

# Path to Tesseract OCR (for Windows users)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update if needed

# Set up paths
INPUT_DIR = r"OneDrive Feb 12 2025/Volunteers"  # Use raw string for Windows paths
OUTPUT_DIR = "output_texts"
PDF_DIR = "converted_pdfs"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

failed_getting_text = []

def convert_doc_to_pdf(input_path, output_path):
    wdFormatPDF = 17

    # Ensure the file exists
    if not os.path.exists(input_path):
        print(f"Error: File not found -> {input_path}")
        return

    #print(f"Converting DOC to PDF: {input_path} -> {output_path}")

    # Initialize Word application
    word = comtypes.client.CreateObject('Word.Application')
    word.Visible = False  # Run in the background

    try:
        doc = word.Documents.Open(os.path.abspath(input_path))  # Ensure absolute path
        doc.SaveAs(os.path.abspath(output_path), FileFormat=wdFormatPDF)
        doc.Close()
        #print(f"Successfully converted: {output_path}")

    except Exception as e:
        print(f"Error converting DOC to PDF: {e}")

    finally:
        word.Quit()

def convert_xls_to_pdf(input_path, output_path):
    """ Converts Excel to a PDF by extracting text. """
    print(f"Converting XLS to PDF: {input_path} -> {output_path}")
    try:
        df = pd.read_excel(input_path, sheet_name=None)
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        for sheet, data in df.items():
            pdf.cell(200, 10, txt=f"Sheet: {sheet}", ln=True)
            for row in data.astype(str).values:
                pdf.cell(200, 10, txt=" | ".join(row), ln=True)

        pdf.output(output_path)
    except Exception as e:
        print(f"Error converting XLS: {e}")

def convert_txt_to_pdf(input_path, output_path):
    """ Converts a plain text file to a PDF. """
    print(f"Converting TXT to PDF: {input_path} -> {output_path}")
    try:
        with open(input_path, "r", encoding="utf-8") as file:
            content = file.readlines()
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for line in content:
            pdf.cell(200, 10, txt=line.strip(), ln=True)

        pdf.output(output_path)
    except Exception as e:
        print(f"Error converting TXT: {e}")

def extract_text_from_pdf(pdf_path):
    """ Extracts text from a PDF using PyMuPDF (fitz) and pdfplumber. """
    print(f"Extracting text from PDF: {pdf_path}")
    try:
        reader = PdfReader(pdf_path)
        text = ""

        for page in reader.pages:
            extracted_text = page.extract_text()
            text += extracted_text if extracted_text else ""

        if not text.strip():
            print(f"No text found, using OCR... {pdf_path}")
            text = extract_text_via_ocr(pdf_path)

        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_text_via_ocr(pdf_path):
    """ Extracts text from scanned PDFs using OCR. """
    print(f"Performing OCR on scanned PDF: {pdf_path}")
    text = ""
    try:
        images = convert_from_path(pdf_path)
        for img in images:
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)  # Fix image conversion
            text += pytesseract.image_to_string(img_cv) + "\n"
    except Exception as e:
        print(f"OCR Error: {e}")
        failed_getting_text.append(pdf_path)
    return text

def process_files(input_dir):
    """ Processes all files in the directory, converting and extracting text. """
    for root, _, files in os.walk(input_dir):
        for file in files:
            input_path = os.path.join(root, file)
            filename, ext = os.path.splitext(file)
            ext = ext.lower()

            print(f"Processing file: {file} (Extension: {ext})")

            if ext == ".pdf":
                pdf_path = input_path
            else:
                pdf_path = os.path.join(PDF_DIR, f"{filename}.pdf")

                if ext == ".docx":
                    convert(input_path, pdf_path)  # Correct usage for docx2pdf
                elif ext == ".doc":
                    convert_doc_to_pdf(input_path, pdf_path)
                elif ext in [".xls", ".xlsx"]:
                    convert_xls_to_pdf(input_path, pdf_path)
                elif ext == ".txt":
                    convert_txt_to_pdf(input_path, pdf_path)
                else:
                    print(f"Skipping unsupported file type: {file}")
                    continue

            if os.path.exists(pdf_path):
                extracted_text = extract_text_from_pdf(pdf_path)
                text_file_path = os.path.join(OUTPUT_DIR, f"{filename}.txt")
                
                with open(text_file_path, "w", encoding="utf-8") as text_file:
                    text_file.write(extracted_text)

                print(f"Text extracted and saved: {text_file_path}")
            else:
                print(f"PDF not found: {pdf_path}")

if __name__ == "__main__":
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory '{INPUT_DIR}' does not exist!")
    else:
        process_files(INPUT_DIR)
        
        with open("failed_getting_text.txt", "a") as file:
            file.write("\n".join(failed_getting_text))
