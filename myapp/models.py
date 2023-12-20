from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, email, company_name, password=None, company_id=None):
        if not email:
            raise ValueError("Users must have an email address")

        if company_id is None:
            numeric_ids = CustomUser.objects.filter(company_id__regex=r'^\d{4}$')
            if numeric_ids:
                max_id = max([int(user.company_id) for user in numeric_ids])
                next_id = str(max_id + 1).zfill(4)
            else:
                next_id = '0001'
            company_id = next_id

        user = self.model(
            email=self.normalize_email(email),
            company_name=company_name,
            company_id=company_id,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, company_name, password=None, company_id=None):
        user = self.create_user(
            email,
            company_name,
            password=password,
            company_id=company_id,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    company_id = models.CharField(max_length=100, unique=True)
    company_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True, validators=[EmailValidator()])
    api_key = models.CharField(max_length=255, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'company_id'
    REQUIRED_FIELDS = ['company_name' ,'email']


    def __str__(self):
        return self.company_id

class Employee(models.Model):
    
    employee_id = models.CharField(max_length=100, unique=True)
    video_file = models.FileField(upload_to='get_upload_path')
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='employees')
    employee_name = models.CharField(max_length=100)
    employee_department = models.CharField(max_length=100)

    def __str__(self):
        return self.employee_name

def get_upload_path(instance, filename):
    # Define the upload path to be company-specific
    return f'videos/{instance.company.company_id}/{filename}'


class VideoRecord(models.Model):
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    video_path = models.CharField(max_length=200)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee.employee_name} - {self.company.company_id}"

class Video(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
from django.db import models

class VideoFile(models.Model):
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link to company
    file_path = models.CharField(max_length=255)  # Path to the video file
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp


class APIConfig(models.Model):
    url = models.CharField(max_length=255)
    token = models.CharField(max_length=100)
    api_key = models.CharField(max_length=100)

    def __str__(self):
        return f"APIConfig for {self.url}"
    

class SpiderApi(models.Model):
    api_key = models.CharField(max_length=200)
    file_status = models.CharField(max_length=200)
    url = models.CharField(max_length=200)

def get_upload_path(instance, filename):
    # Define the upload path to be company-specific
    return f'videos/{instance.company.company_id}/{filename}'

class S3model(models.Model):
    access_id=models.CharField(max_length=100)
    access_key=models.CharField(max_length=100)
    bucket_name=models.CharField(max_length=100)
    region=models.CharField(max_length=100)

    def __str__(self) :
        return self.bucket_name
    

class TelegramApirec(models.Model):
    api_key1 = models.CharField(max_length=300)
    chat_id = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.api_key1

