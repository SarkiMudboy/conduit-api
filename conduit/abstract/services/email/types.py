from typing import Any, Dict, List, TypedDict, Union

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.fields.files import FieldFile


class EmailData(TypedDict):

    subject: str
    from_email: str
    to_email: List[str]
    template: str
    context: Dict[str, Any]
    file: Union[FieldFile, SimpleUploadedFile]
