from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Path, UploadFile, status

from app.modules.auth.dependencies import require_admin
from app.modules.upload import service
from app.modules.upload.schema import CloudinaryResponse


router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post(
    "/imagen",
    response_model=CloudinaryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def subir_imagen(
    file: UploadFile = File(...),
    folder: Annotated[str, Form()] = "foodstore",
) -> CloudinaryResponse:
    return await service.upload_imagen(file, folder)


@router.delete(
    "/imagen/{public_id:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def eliminar_imagen(public_id: Annotated[str, Path()]) -> None:
    service.eliminar_imagen(public_id)
