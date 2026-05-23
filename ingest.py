import os
from pdfminer.high_level import extract_text

def read_file(file_path):
    """Reads text from a PDF or TXT file."""
    # Find out if it is a pdf or txt file
    ext = os.path.splitext(file_path)[1].lower()
    
    # If it is a PDF file, use pdfminer to read the text safely
    if ext == '.pdf':
        try:
            return extract_text(file_path)
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return ""
            
    # If it is a normal text file, open it directly
    elif ext == '.txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TXT {file_path}: {e}")
            return ""
            
    # For anything else, tell the user it is not supported
    else:
        print(f"Unsupported file format: {ext}")
        return ""
