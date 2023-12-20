from myapp.models import CustomUser
from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
import os
# Mapping of API keys to usernames 'ApiKeyForUser3': 'user3',
from .storages import MediaRoot1Storage

storage = MediaRoot1Storage()


users = CustomUser.objects.filter(is_approved=True).exclude(api_key__isnull=True)
API_KEYS = {}

for user in users:
    API_KEYS[user.api_key] = user.company_id


# API_KEYS = {
#     'ApiKeyForUser1': 'user1',
#     'ApiKeyForUser2': 'user2',
#     'ApiKeyForUser3': 'user3',
# }

def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        users = CustomUser.objects.filter(is_approved=True).exclude(api_key__isnull=True)
        API_KEYS = {}

        for user in users:
            API_KEYS[user.api_key] = user.company_id
        

        request = args[1]
        api_key = request.headers.get('X-API-KEY')
        if api_key not in API_KEYS:
            return Response({'message': 'Invalid API Key'}, status=status.HTTP_403_FORBIDDEN)
        request.user = API_KEYS[api_key]  # Add username to the request
        return f(*args, **kwargs)
    return decorated

class FileUploadView(APIView):
    @api_key_required
    def post(self, request, format=None):
        file = request.FILES.get('file')
        if not file:
            return Response({'message': 'No file part'}, status=status.HTTP_400_BAD_REQUEST)
        user_folder = os.path.join(settings.MEDIA_ROOT1, request.user)
        os.makedirs(user_folder, exist_ok=True)
        filename = os.path.join(user_folder, file.name)
        with storage.open(filename, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return Response({'message': 'File uploaded successfully'}, status=status.HTTP_200_OK)
    
class UploadedFilesView(APIView):
    @api_key_required
    def get(self, request, format=None):
        # Get company_id from the request
        company_id = request.user

        # Find all users belonging to the same company
        company_users = CustomUser.objects.filter(company_id=company_id)

        # Aggregate files from all company users
        all_files = []
        for user in company_users:
            user_folder = os.path.join(settings.MEDIA_ROOT, str(user.company_id))
            if os.path.exists(user_folder):
                files = os.listdir(user_folder)
                all_files.extend(files)

        if not all_files:
            return Response({'message': 'No files found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'files': all_files}, status=status.HTTP_200_OK)