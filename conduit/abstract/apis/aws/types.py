from typing import Optional, TypedDict


class BaseFileObject(TypedDict):

    id: str
    path: str
    url: str


class FileObject(BaseFileObject):
    # this adds filesize for unsaved assets (Best for representing files to be uploaded)
    size: int


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
