import os
from pathlib import Path
from src import config

def clear_uploads_directory() -> None:
    """
    Elimina todos los archivos del directorio de uploads,
    preservando el archivo placeholder '.gitkeep'.
    """
    if config.UPLOADS_DIR.exists():
        for item in config.UPLOADS_DIR.iterdir():
            if item.is_file() and item.name != ".gitkeep":
                try:
                    item.unlink()
                except Exception as e:
                    print(f"Error al eliminar el archivo temporal {item.name}: {str(e)}")

def is_allowed_file(filename: str) -> bool:
    """
    Verifica si la extensión del archivo está soportada por la aplicación.
    Formatos admitidos: PDF, DOCX, TXT, CSV, XLSX, XLS.
    """
    allowed_extensions = {'.pdf', '.docx', '.txt', '.csv', '.xlsx', '.xls'}
    return Path(filename).suffix.lower() in allowed_extensions

def get_file_size_formatted(file_path: Path) -> str:
    """Retorna el tamaño de un archivo formateado en KB o MB para el usuario."""
    try:
        size_bytes = file_path.stat().st_size
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    except Exception:
        return "Tamaño desconocido"
