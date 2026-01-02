"""
Module for converting files to markdown using docling
"""

from pathlib import Path
from docling.document_converter import DocumentConverter


def convert_file(input_file, output_folder):
    """
    Main conversion function that routes to appropriate converter based on file type.
    
    Args:
        input_file (str): Full path to input file
        output_folder (str): Path to output folder
    
    Returns:
        tuple: (success: bool, message: str, output_file: str)
    """
    input_path = Path(input_file)
    extension = input_path.suffix.lower()
    
    # Document files
    if extension in {".pdf", ".docx", ".doc", ".pptx", ".ppt"}:
        return convert_document_file(input_file, output_folder)
    
    # Image files
    elif extension in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}:
        return convert_image_file(input_file, output_folder)
    
    # HTML files
    elif extension in {".html", ".htm"}:
        return convert_html_file(input_file, output_folder)
    
    # Spreadsheet files
    elif extension in {".xlsx", ".xls"}:
        return convert_spreadsheet_file(input_file, output_folder)
    
    # Text files
    elif extension in {".txt", ".rtf", ".odt"}:
        return convert_text_file(input_file, output_folder)
    
    else:
        return (False, f"Unsupported file type: {extension}", "")


def convert_document_file(input_file, output_folder):
    """
    Convert document files (PDF, DOCX, DOC, PPTX, PPT) to markdown.
    
    Args:
        input_file (str): Full path to input file
        output_folder (str): Path to output folder
    
    Returns:
        tuple: (success: bool, message: str, output_file: str)
    """
    try:
        input_path = Path(input_file)
        output_path = Path(output_folder)
        
        # Create output filename with .md extension
        output_file = output_path / f"{input_path.stem}.md"
        
        # Initialize converter
        converter = DocumentConverter()
        
        # Convert document
        result = converter.convert(input_file)
        
        # Export to markdown
        markdown_content = result.document.export_to_markdown()
        
        # Write to output file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return (True, f"Successfully converted {input_path.name}", str(output_file))
    
    except Exception as e:
        return (False, f"Error converting {input_path.name}: {str(e)}", "")


def convert_image_file(input_file, output_folder):
    """
    Convert image files (PNG, JPG, JPEG, GIF, BMP, TIFF) to markdown using OCR.
    
    Args:
        input_file (str): Full path to input file
        output_folder (str): Path to output folder
    
    Returns:
        tuple: (success: bool, message: str, output_file: str)
    """
    try:
        input_path = Path(input_file)
        output_path = Path(output_folder)
        
        # Create output filename with .md extension
        output_file = output_path / f"{input_path.stem}.md"
        
        # Initialize converter with OCR enabled
        converter = DocumentConverter()
        
        # Convert image
        result = converter.convert(input_file)
        
        # Export to markdown
        markdown_content = result.document.export_to_markdown()
        
        # Write to output file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return (True, f"Successfully converted {input_path.name}", str(output_file))
    
    except Exception as e:
        return (False, f"Error converting {input_path.name}: {str(e)}", "")


def convert_html_file(input_file, output_folder):
    """
    Convert HTML/HTM files to markdown.
    
    Args:
        input_file (str): Full path to input file
        output_folder (str): Path to output folder
    
    Returns:
        tuple: (success: bool, message: str, output_file: str)
    """
    try:
        input_path = Path(input_file)
        output_path = Path(output_folder)
        
        # Create output filename with .md extension
        output_file = output_path / f"{input_path.stem}.md"
        
        # Initialize converter
        converter = DocumentConverter()
        
        # Convert HTML
        result = converter.convert(input_file)
        
        # Export to markdown
        markdown_content = result.document.export_to_markdown()
        
        # Write to output file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return (True, f"Successfully converted {input_path.name}", str(output_file))
    
    except Exception as e:
        return (False, f"Error converting {input_path.name}: {str(e)}", "")


def convert_spreadsheet_file(input_file, output_folder):
    """
    Convert spreadsheet files (XLSX, XLS) to markdown.
    
    Args:
        input_file (str): Full path to input file
        output_folder (str): Path to output folder
    
    Returns:
        tuple: (success: bool, message: str, output_file: str)
    """
    try:
        input_path = Path(input_file)
        output_path = Path(output_folder)
        
        # Create output filename with .md extension
        output_file = output_path / f"{input_path.stem}.md"
        
        # Initialize converter
        converter = DocumentConverter()
        
        # Convert spreadsheet
        result = converter.convert(input_file)
        
        # Export to markdown
        markdown_content = result.document.export_to_markdown()
        
        # Write to output file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return (True, f"Successfully converted {input_path.name}", str(output_file))
    
    except Exception as e:
        return (False, f"Error converting {input_path.name}: {str(e)}", "")


def convert_text_file(input_file, output_folder):
    """
    Convert text files (TXT, RTF, ODT) to markdown.
    
    Args:
        input_file (str): Full path to input file
        output_folder (str): Path to output folder
    
    Returns:
        tuple: (success: bool, message: str, output_file: str)
    """
    try:
        input_path = Path(input_file)
        output_path = Path(output_folder)
        extension = input_path.suffix.lower()
        
        # Create output filename with .md extension
        output_file = output_path / f"{input_path.stem}.md"
        
        # For plain text files (.txt), just read and write directly
        # since plain text is already markdown-compatible
        if extension in {".txt"}:
            with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Write to output file with simple markdown formatting
            with open(output_file, "w", encoding="utf-8") as f:
                # Add a title based on filename
                f.write(f"# {input_path.stem}\n\n")
                f.write(content)
            
            return (True, f"Successfully converted {input_path.name}", str(output_file))
        
        # For other text formats (.rtf, .odt), use docling
        else:
            # Initialize converter
            converter = DocumentConverter()
            
            # Convert text file
            result = converter.convert(input_file)
            
            # Export to markdown
            markdown_content = result.document.export_to_markdown()
            
            # Write to output file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            return (True, f"Successfully converted {input_path.name}", str(output_file))
    
    except Exception as e:
        return (False, f"Error converting {input_path.name}: {str(e)}", "")
