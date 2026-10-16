
from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.app.services.document_service import extract_text

router = APIRouter(prefix="/api", tags=["Учебники"])


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Выберите файл."
        )

    try:
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Файл пустой."
            )

        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Максимальный размер файла — 20 МБ."
            )

        text = extract_text(file.filename, content)

        return {
            "filename": file.filename,
            "characters": len(text),
            "preview": text[:1500],
            "message": "Текст успешно извлечён."
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Не удалось обработать документ."
        )
