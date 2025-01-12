from typing import Optional, TypedDict


class FileObject(TypedDict):

    id: str
    path: str
    url: str


class FileMetaData(TypedDict):

    owner_email: str
    drive_id: str
    file_path: str  # path without the drive
    resource_id: Optional[str]
