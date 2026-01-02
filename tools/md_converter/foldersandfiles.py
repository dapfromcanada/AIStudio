"""
Module for file and folder operations
"""

from pathlib import Path


def get_convertible_files(input_path):
    """
    Get list of files that docling can convert to markdown.
    
    Docling supports: PDF, DOCX, PPTX, images (PNG, JPG, etc.), HTML, and more.
    
    Args:
        input_path (str): Path to the input folder
    
    Returns:
        list: List of file paths that can be converted
    """
    # File extensions that docling can convert
    convertible_extensions = {
        ".pdf",
        ".docx",
        ".doc",
        ".pptx",
        ".ppt",
        ".html",
        ".htm",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".tiff",
        ".txt",
        ".rtf",
        ".odt",
        ".xlsx",
        ".xls",
    }
    
    convertible_files = []
    
    # Check if path exists
    path = Path(input_path)
    if not path.exists() or not path.is_dir():
        return convertible_files
    
    # Get all files in the directory
    for file_path in path.iterdir():
        if file_path.is_file():
            # Check if file extension is in the convertible list
            if file_path.suffix.lower() in convertible_extensions:
                convertible_files.append(str(file_path))
    
    # Sort files by name for consistent ordering
    convertible_files.sort()
    
    return convertible_files
