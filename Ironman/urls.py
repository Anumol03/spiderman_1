"""
URL configuration for Ironman project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from myapp.views import *
from recapp.views import *


from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('',first,name='first'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('employee_register/',employee_registration,name='employee_register'),
    path('login/', login_view, name='login'),
    path('admin-approval/', admin_approval, name='admin_approval'),
    path('video_feed/<str:employee_name>/<str:employee_id>/', video_feed, name='video_feed'),
    path('company_page/<str:company_id>/', company_page, name='company_page'),
    path('process_videos/<str:company_id>/', process_videos, name='process_videos'),
    path('delete-employee/<int:employee_id>/', delete_employee, name='delete_employee'),
    path('admin-approval/admin_total_Companies/',admin_total_Companies,name='admin_total_Companies'),
    path('company/<int:company_id>/department/<str:department_name>/', department_employees, name='department_employees'),
    path('approve_video/<int:video_id>/', approve_video_view, name='approve_video'),
    path('approval/', admin_approval_view, name='approval'),
    path('upload/', video_upload_view, name='video_upload'),
    path('company_page/<str:company_id>/unapproved-videos/', unapproved_videos_view, name='unapproved_videos'),
    path('password_reset/', password_reset_request, name='password_reset_request'),
    path('password_reset/done/', password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', password_reset_complete, name='password_reset_complete'),
    path('video_approval/', video_approval_page, name='video_approval_page'),

    
    #api
    path('uploads/', FileUploadView.as_view(), name='file-upload'),
    path('files/', UploadedFilesView.as_view(), name='uploaded-files'),
    
    # Password reset links (ref: https://docs.djangoproject.com/en/2.2/topics/auth/default/)

   
    # other patterns...
   ] 


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL1, document_root=settings.MEDIA_ROOT1)
   
