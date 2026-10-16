# готовая функция для извлечения текста из PDF, DOCX и TXT файлов и его содержимое в байтах

from pathlib import Path
from io import BytesIO # работает с файлами и преобразует их в байты

from docx import Document # для чтения DOCX файлов
from pypdf import PdfReader # для чтения PDF файлов


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_text(filename: str, content: bytes) -> str:
    """Извлекает текст из PDF, DOCX или TXT.""" # подсказка

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Поддерживаются только PDF, DOCX и TXT."
        )

    if extension == ".pdf":
        reader = PdfReader(BytesIO(content))

        if reader.is_encrypted:
            raise ValueError(
                "PDF защищён паролем. Загрузите другой файл."
            )

        pages = [
            page.extract_text() or ""
            for page in reader.pages
        ]
        text = "\n".join(pages)

    elif extension == ".docx":
        document = Document(BytesIO(content))
        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

    else:
        text = None

        for encoding in ("utf-8-sig", "utf-8", "cp1251"):
            try:
                text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if text is None:
            raise ValueError(
                "Не удалось прочитать кодировку TXT-файла."
            )

    text = text.strip()

    if not text:
        raise ValueError(
            "В документе не найден текст. "
            "Возможно, PDF состоит из сканов."
        )

    return text
