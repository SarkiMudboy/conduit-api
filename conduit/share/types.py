from typing import TypedDict


class ShareData(TypedDict):

    uid: str
    author: str  # uid
    drive: str  # uid
    note: str
    # mentioned_members: List[str]
