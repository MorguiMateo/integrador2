from fastapi import APIRouter, File, UploadFile, status

from app.modules.upload.schema import UploadResponse
from app.modules.upload.service import save_upload


router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    return await save_upload(file)
