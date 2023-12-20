from django.core.files.storage import FileSystemStorage
from django.conf import settings

class MediaRoot1Storage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(location=settings.MEDIA_ROOT1, *args, **kwargs)