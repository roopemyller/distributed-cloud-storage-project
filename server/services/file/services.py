from typing import Optional
from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    message: str
    filename: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None

class FileDownload(BaseModel):
    file_name: str
