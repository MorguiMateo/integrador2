from __future__ import annotations

import cloudinary.uploader
from fastapi import HTTPException, UploadFile

from app.modules.upload.schema import CloudinaryResponse


ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_FORMATS = ["jpg", "jpeg", "png", "webp"]
MAX_SIZE = 5 * 1024 * 1024


async def upload_imagen(file: UploadFile, folder: str) -> CloudinaryResponse:
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado")

    contenido = await file.read()
    await file.close()

    if len(contenido) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="La imagen supera el tamaño máximo de 5 MB")

    resultado = cloudinary.uploader.upload(
        contenido,
        folder=folder,
        overwrite=False,
        unique_filename=True,
        resource_type="image",
        allowed_formats=ALLOWED_FORMATS,
    )

    return CloudinaryResponse(
        secure_url=resultado["secure_url"],
        public_id=resultado["public_id"],
        width=resultado["width"],
        height=resultado["height"],
        format=resultado["format"],
        resource_type=resultado["resource_type"],
    )


def eliminar_imagen(public_id: str) -> None:
    cloudinary.uploader.destroy(public_id, resource_type="image")
