from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    url: str
    content_type: str | None = None
    size: int

