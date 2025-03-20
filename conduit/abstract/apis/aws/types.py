from typing import Optional, TypedDict


class FileObject(TypedDict):

    id: str
    path: str
    size: int
    url: str


class FileMetaData(TypedDict):

    author: str
    drive_id: str
    file_path: str  # path without the drive
    filesize: str
    resource_id: Optional[str]
    # sharing...
    share_uid: str
    note: str
    mentioned_members: str
