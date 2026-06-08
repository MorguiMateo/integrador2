from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.modules.upload.schema import UploadResponse


UPLOAD_DIR = Path("uploads")


async def save_upload(file: UploadFile) -> UploadResponse:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "").suffix
    filename = f"{uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / filename

    size = 0
    with destination.open("wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)
            size += len(chunk)

    await file.close()

    return UploadResponse(
        filename=filename,
        url=f"/uploads/{filename}",
        content_type=file.content_type,
        size=size,
    )

