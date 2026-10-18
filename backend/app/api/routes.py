
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.document_service import extract_text
from backend.app.services.rag_service import (
    index_textbook,
    search_textbook,
)

router = APIRouter(prefix="/api", tags=["Учебники"])


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    document_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=10)


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Выберите файл.",
        )

    try:
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Файл пустой.",
            )

        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Максимальный размер файла — 20 МБ.",
            )

        text = extract_text(file.filename, content)

        # Сохраняем фрагменты текста в векторную базу
        indexed = index_textbook(
            text=text,
            filename=file.filename,
        )

        return {
            **indexed,
            "characters": len(text),
            "preview": text[:1500],
            "message": "Учебник обработан и добавлен в базу знаний.",
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except HTTPException:
        raise

    except Exception as error:
        print(f"Ошибка обработки документа: {error}")
        raise HTTPException(
            status_code=500,
            detail="Не удалось обработать документ. Проверьте серверный терминал.",
        )


@router.post("/documents/search")
def search_document(request: SearchRequest):
    try:
        results = search_textbook(
            query=request.query,
            document_id=request.document_id,
            top_k=request.top_k,
        )

        return {
            "query": request.query,
            "results_count": len(results),
            "results": results,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        print(f"Ошибка поиска: {error}")
        raise HTTPException(
            status_code=500,
            detail="Не удалось выполнить поиск. Проверьте серверный терминал.",
        )
