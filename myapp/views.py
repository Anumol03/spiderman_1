
from datetime import datetime
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render,redirect
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from myapp.pose_estimation import process_images_in_subfolders, resize_images_and_save
from myapp.video_processing import process_image, split_video_to_frames
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from .models import *
from django.shortcuts import render, redirect
import myapp.embed as insf
import json
from django.urls import reverse
import os
import cv2
import shutil
import requests
import time 
import secrets
import string
from django.views.decorators.cache import never_cache
import os
import json
import time
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
import os
import json
import time
from myapp.uploadfiles import upload_file_to_s3
from myapp.req import upload_file# send_message
from django.contrib.auth.decorators import login_required
 

CustomUser = get_user_model()

spider_api = SpiderApi.objects.first() if SpiderApi.objects.exists() else None

if spider_api:
    API_KEY = spider_api.api_key
    FILE_STATUS = spider_api.file_status
    UPLOAD_URL = spider_api.url



# def # send_message(message):
#     timeTG = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     tapi = TelegramApirec.objects.first()
#     if tapi:
#         api_key = tapi.api_key1
#         # print('api','6809708822:AAGfeKzCTQccpuBvbbYf65tPeRc5clmmZWk',api_key)
#         chat_id = tapi.chat_id
#         # print('Chat','-1001704174792',chat_id)
#         url = f'https://api.telegram.org/bot{api_key}/sendMessage'
#         params = {'chat_id': chat_id, 'text': f'{timeTG}--{message}'}
#         try:
#             response = requests.post(url, params=params)
#             return response
#         except requests.exceptions.RequestException as e:
#             return f'An error occurred: {e}'
#     else:
#         return 'API configuration not found'

def apipush(jsfile):
    # Fetch the configuration from the database
    config = APIConfig.objects.first()  # Assuming you have one config, adjust as needed

    if config:
        headers = {config.token: config.api_key}
        with open(jsfile, 'rb') as file:
            files = {'file': (file.name, file, 'application/json')}
            response = requests.post(config.url, headers=headers, files=files)
            # print(response.text)
            # print(response)
    else:
        pass
        # print("API configuration not found.")

def first(request):
    return render(request,'firstpage.html')

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email).first()

        if user:
            # Generate token and uid
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))

            # Email subject
            subject = "Your Password Reset Request for MyApp"

            # Email content rendered using an HTML template
            context = {
                'company_name': user.company_name,
                'reset_link': reset_link,
            }
            html_content = render_to_string('password_reset_email.html', context)

            # Creating email message
            email_message = EmailMultiAlternatives(subject, None, 'no-reply@myapp.com', [email])
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

            messages.success(request, 'An email has been sent with instructions to reset your password.')
        else:
            # send_message('No account found with the provided email address...line 114 in views.py/myapp/ironman')
            messages.error(request, 'No account found with the provided email address.')

    return render(request, 'password_reset_request.html')



# Password Reset Done View
def password_reset_done(request):
    return render(request, 'password_reset_done.html')

# Password Reset Confirm View
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        # print("Decoded UID:", uid) 
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        # print("Error decoding UID or user not found:",)  # # print error if any

        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            if new_password1 == new_password2:
                user.set_password(new_password1)
                user.save()
                return redirect('password_reset_complete')
    return render(request, 'password_reset_form.html', {'uidb64': uidb64, 'token': token})

# Password Reset Complete View
def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')


def register(request):
    if request.method == 'POST':
        try:
            company_name = request.POST.get('company_name')
            email = request.POST.get('email')  # Get email from the form
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')

            # Basic validation
            if password != password_confirm:
                messages.error(request, "Passwords do not match.")
                return render(request, 'register.html')

            # Check if email already exists
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return render(request, 'register.html')

            # Create new user with a generated company_id
            user = CustomUser.objects.create_user(
                email=email,
                company_name=company_name,
                password=password  # Password will be encrypted in create_user method
            )

            # Sending Welcome Email with company_id
            subject = "Welcome to Jezt Family"
            context = {
                'company_name': company_name,
                'company_id': user.company_id,  # Include company_id in the email
            }
            html_content = render_to_string('welcome_email_template.html', context)
            email_message = EmailMultiAlternatives(subject, None, 'no-reply@myapp.com', [email])
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

            # Log the user in and redirect to login page with success message
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Registration successful.')
            messages.info(request, f'Your Company ID is {user.company_id}')
            return redirect('login')  # Replace 'login' with the name of your login view

        except Exception as e:
            # send_message(f"An error occurred during registration: {e}...line 194 in views.py/myapp/ironman")
            messages.error(request, f"An error occurred during registration: {e}")
            return render(request, 'register.html')

    return render(request, 'register.html')


def employee_registration(request):
    try:
        if request.method == 'POST':
            employee_id = request.POST.get('employee_id')
            company_id = request.POST.get('company_id')
            employee_name = request.POST.get('employee_name')
            employee_department = request.POST.get('employee_department')

            try:
                company = CustomUser.objects.get(company_id=company_id, is_approved=True)
            except CustomUser.DoesNotExist:
                messages.error(request, "Invalid company ID or company not approved.")
                return render(request, 'employee_register.html')

            try:
                employee = Employee(
                    employee_id=employee_id,
                    company=company,
                    employee_name=employee_name,
                    employee_department=employee_department
                )
                employee.save()
            except IntegrityError:
                messages.error(request, f"Employee ID {employee_id} is already in use.")
                return render(request, 'employee_register.html')

            redirect_url = reverse('video_feed', kwargs={'employee_name': employee_name, 'employee_id': employee.employee_id})
            return redirect(redirect_url)

        return render(request, 'employee_register.html')
    except Exception as e:
        # send_message(f"Error in employee_registration: {e}")
        # print(f"Error in employee_registration: {e}")
        return HttpResponse("Error encountered in employee registration process.")
    
def is_admin_user(user):
    return user.is_superuser

def generate_api_key(length=24):
    characters = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(characters) for _ in range(length))
    return api_key

@never_cache
@login_required
@user_passes_test(is_admin_user)
def admin_approval(request):
    try:
        if request.method == 'POST':
            user_id = request.POST.get('user_id')
            user = CustomUser.objects.get(id=user_id)

            # Check if the user is being approved and does not already have an API key
            if not user.is_approved and not user.api_key:
                user.is_approved = True
                user.api_key = generate_api_key(24)  # Generate a secure random API key
                user.save()

            if user.is_approved and user.api_key:
                data_to_send = {
                    user.api_key: user.company_id,
                }
                # print(data_to_send)

            return redirect('admin_approval')

        users_to_approve = CustomUser.objects.filter(is_approved=False)
        total_company_count = CustomUser.objects.filter(is_approved=True).values('company_id').distinct().count() - CustomUser.objects.filter(is_superuser=True, is_active=True).count()
        unapproved_count = CustomUser.objects.filter(is_approved=False).values('company_id').distinct().count()
        total_employee_count = Employee.objects.count()
        superuser_count = CustomUser.objects.filter(is_superuser=True, is_active=True).count()

        # Prepare data for the doughnut chart
        companies = CustomUser.objects.exclude(is_superuser=True)
        company_data = []
        for company in companies:
            num_employees = company.employees.count()
            percentage = (num_employees / total_employee_count * 100) if total_employee_count > 0 else 0
            company_data.append({
                'name': company.company_name,
                'percentage': percentage
            })
        company_data.sort(key=lambda x: x['percentage'], reverse=True)

        context = {
            'users': users_to_approve,
            'total_company_count': total_company_count,
            'unapproved_count': unapproved_count,
            'total_employee_count': total_employee_count,
            'superuser_count': superuser_count,
            'company_data': company_data
        }
        return render(request, 'admin.html', context)

    except Exception as e:
        # send_message(f"An error occurred: {e}..line 296 in views.py/myapp/ironman")
        messages.error(request, f"An error occurred: {e}")
        return render(request, 'error.html')  # Replace with your error template



@never_cache
@login_required
@user_passes_test(is_admin_user)
def admin_total_Companies(request):
    return render(request,"admin_total_companies.html" )




def login_view(request):
    try:
        if request.method == 'POST':
            company_id = request.POST['company_id']
            password = request.POST['password']
            user = authenticate(request, username=company_id, password=password)

            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    return redirect('admin_approval')
                elif user.is_approved:
                    login(request, user)
                    return redirect('company_page', company_id=company_id)  # Redirect to the company page
                else:
                    messages.error(request, 'Your account has not been approved by the admin yet.')
            else:
                messages.error(request, 'Invalid company ID or password.')

        return render(request, 'login.html')

    except Exception as e:
        # send_message(f"An error occurred during login: {e}..line 333 in veiws.py/myapp/ironman")
        messages.error(request, f"An error occurred during login: {e}")
        return render(request, 'login.html')  # Re-render the login page with the error message

@never_cache
@login_required
def company_page(request, company_id):
    try:
        company = get_object_or_404(CustomUser, company_id=company_id)
        employees = Employee.objects.filter(company=company)
        unapproved_videos = VideoRecord.objects.filter(company=company, is_approved=False)


        department_employees = {}
        for employee in employees:
            dept = employee.employee_department
            if dept not in department_employees:
                department_employees[dept] = []
            department_employees[dept].append(employee)

        context = {
            'company': company,
            'employees': employees,
            'department_employees': department_employees,
            'videos': unapproved_videos,
        }
        return render(request, 'company_page.html', context)

    except Exception as e:
        # send_message(f"An error occurred: {e}....line 362 in views.py/myapp/ironman")
        messages.error(request, f"An error occurred: {e}")
        return render(request, 'error.html')
        
@login_required
def video_approval_page(request):
    try:
        user_company = request.user
        unapproved_videos = VideoRecord.objects.filter(company=user_company, is_approved=False)
        context = {
            'videos': unapproved_videos,
        }
        return render(request, 'video_approval.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return render(request, 'error.html')

def unapproved_videos_view(request):
    company = request.user
    unapproved_videos = VideoRecord.objects.filter(is_approved=False, company=company)

    context = {
        'unapproved_videos': unapproved_videos,
    }

    return render(request, 'unapproved_videos.html', context)

def department_employees(request, company_id, department_name):
    try:
        company = get_object_or_404(CustomUser, company_id=company_id)
        employees = Employee.objects.filter(company=company, employee_department=department_name)

        context = {
            'company': company,
            'department_name': department_name,
            'employees': employees
        }
        return render(request, 'department_employees.html', context)

    except Exception as e:
        # send_message( f"An error occurred while fetching department data: {e}...line 402 in views.py/myapp/ironman")
        messages.error(request, f"An error occurred while fetching department data: {e}")
        return render(request, 'error.html')
    
def process_videos(request, company_id):
    if request.method == 'POST':
        # print('nayeee')
        try:
            # print('poda patti')
            
            company = get_object_or_404(CustomUser, company_id=company_id)
            # print(company_id)
            
            resized_frames_root_folder = 'resized_frames'
            input_folder = os.path.join(resized_frames_root_folder, str(company.company_id))
            users = os.listdir(input_folder)
            # print(users)

            uniqueid = set()
           
            if not users:
                # print("not working ")
                return JsonResponse({'error': 'No frame files found for the company'}, status=404)

            for user in users:
                input_json_path = os.path.join(input_folder, user)
                
                # Flag to check if any JSON file is found
                json_file_found = False

                for filename in os.listdir(input_json_path):
                    if filename.endswith('.json'):
                        json_file_found = True
                        js = filename
                        # print(js)

                        with open(f"{input_json_path}/{js}", "r") as json_file:
                            data = json.load(json_file)
                            name, empid, cmpny_id = data["name"], data["employeeid"], data["companyid"]
                            # print(name,empid,cmpny_id)

                            if not os.path.exists(cmpny_id):
                                os.makedirs(cmpny_id)

                            outjson = os.listdir(cmpny_id) #if not
                            # print(f'outjson is {outjson}')

                            if f"Forward_{cmpny_id}.json" in outjson:
                                with open(os.path.join(cmpny_id, f"Forward_{cmpny_id}.json"), 'r') as ref:
                                    data1 = json.load(ref)
                                    for item in data1:
                                        image_path = item.get("image_path", None)
                                        split_data = image_path.split(',')
                                        refid = split_data[1]
                                        # print(refid)

                                        if refid not in uniqueid:
                                            uniqueid.add(refid)
                                        else:
                                            pass
                                            # send_message(f"User Already In Dataframe {refid}")
                                            # print("User Already In Dataframe")

                            if empid not in uniqueid:
                                persondetails = f"{name},{empid},{cmpny_id}"
                                insf.extract_face_features(input_json_path, persondetails, cmpny_id)
                                # shutil.rmtree(input_json_path)
                                # send_message(f'process completedd {persondetails}')
                                # print('process completedd , deletd 64 folder')

                                # jsz = [file for file in outjson if file.endswith('.json')]
                                # for file in jsz:
                                #     # print('api section')
                                #     apipush(f"{company_id}\{file}")
                            else:
                                pass
                                # print('Id already available')

                # Check if no JSON file was found and # print statement
                if not json_file_found:

                    # send_message(f"No JSON files found in {input_json_path}")
                    print(f"No JSON files found in {input_json_path}")

        except Exception as e:
            # send_message(f'Error : {e}....line 482 in views.py/myapp/ironman')
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'error.html')  # Redirect to an error page or another appropriate view

        return HttpResponseRedirect(reverse('company_page', args=[company_id]))

    return HttpResponseRedirect(reverse('company_page', args=[company_id]))



@never_cache
def logout_view(request):
    # Log out the user
    logout(request)

    # Clear all session data
    request.session.flush()

    # Add additional headers to the response to discourage caching
    response = redirect('first')  # Redirect to the login page

    response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


def video_feed(request, employee_name,employee_id):
    # Pass the employee_name to the template
    return render(request, 'loki.html', {'employee_name': employee_name, 'employee_id': employee_id})


from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def split_video_to_frames(video_path, output_directory):
    # print(f"Attempting to open video file at: {video_path}")
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        # print("Error: Unable to open video file.")
        return

    os.makedirs(output_directory, exist_ok=True)
    frame_count = 0
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        frame_filename = f"{output_directory}/frame_{frame_count:04d}.jpg"
        cv2.imwrite(frame_filename, frame)
        frame_count += 1

    video_capture.release()
    # print('Frames extraction completed.')

@csrf_exempt
@require_POST

def video_upload_view(request):
    # print("Video upload view called.")  # Initial entry # print statement

    if request.method == 'POST' and 'video' in request.FILES:
        # print("Processing POST request with video.")
        video = request.FILES['video']
        employee_id = request.POST.get('employee_id')
        employee_name = request.POST.get('employee_name')

        try:
            employee = Employee.objects.get(employee_id=employee_id)
            company = employee.company
            # print(f"Employee found: {employee_name}, Company: {company.company_name}")
            # # send_message(f"Employee found: {employee_name}, Company: {company.company_name}")

            company_folder_path = os.path.join('media', f"{str(company.company_name)}_{str(company.company_id)}")
            # print(f"Creating company folder at path: {company_folder_path}")
            os.makedirs(company_folder_path, exist_ok=True)

            filename = f"{employee_id}_{company.company_id}_{video.name}"
            fs = FileSystemStorage(location=company_folder_path)
            saved_video_path = os.path.join(company_folder_path, fs.save(filename, video))
            # print(f"Video saved at path: {saved_video_path}")
            # # send_message(f"Video saved at path: {saved_video_path}")
            
            json_name = os.path.splitext(filename)[0] + '.json'
            json_path = os.path.join(company_folder_path, json_name)
            
            jsdata = {
                "name": employee_name,
                "company": company.company_name,
                "employeeid": employee_id,
                "companyid": company.company_id,
                "filename": filename
            }
            with open(json_path, "w") as json_file:
                json.dump(jsdata, json_file)
            # print("JSON metadata saved.")
            time.sleep(10)

            VideoRecord.objects.create(employee=employee, company=company, video_path=saved_video_path, is_approved=False)
            # print("VideoRecord created and saved.")

            return JsonResponse({'message': 'Video uploaded successfully'}, status=200)
        except Employee.DoesNotExist:
            # send_message(f"Error: Employee not found.{employee_id} ..line 588 in views.py/myapp/ironman")
            # print("Error: Employee not found.")
            return JsonResponse({'error': 'Employee not found'}, status=404)
    else:
        # send_message("Error: Invalid request. Either method is not POST or video not in request...line592 in vies.py/myapp/ironman")
        # print("Error: Invalid request. Either method is not POST or video not in request.")
        return JsonResponse({'error': 'Invalid request'}, status=400)

# Import your specific video processing functions here
from .models import VideoRecord


def approve_video_view(request, video_id):
    try:
        video_record = VideoRecord.objects.get(id=video_id, is_approved=False)
        employee = video_record.employee
        company = video_record.company

        # Fetch the saved video path from the database
        saved_video_path = video_record.video_path
        company_folder_path=os.path.dirname(saved_video_path)
        # print(saved_video_path)
        # print(company_folder_path)

        # Fetch the employee's name and employee_id from the database
        # Replace 'name' and 'employee_id' with the actual fields in your Employee model
        employee_id = employee.employee_id
        company_id=str(company.company_id)
        # ups3(saved_video_path,company_id)

        # Fetch the JSON name from the saved video path
        json_name = os.path.splitext(os.path.basename(saved_video_path))[0] + '.json'
        # print(json_name)
        # ups3(f'{company_folder_path}/{json_name}',company_id)
        
        
        

        # Construct the paths for various processing stages
        frames_root_folder = 'extracted_frames'
        employee_frames_folder = os.path.join(frames_root_folder, company_id,  employee_id)

        processed_frames_root_folder = 'processed_frames'
        processed_employee_folder = os.path.join(processed_frames_root_folder, company_id,  employee_id)

        augmented_frames_root_folder = 'augmented_frames'
        augmented_employee_folder = os.path.join(augmented_frames_root_folder, company_id, employee_id)

        resized_frames_root_folder = 'resized_frames'
        resized_employee_folder = os.path.join(resized_frames_root_folder, company_id,  employee_id)


        # Create necessary directories
        os.makedirs(employee_frames_folder, exist_ok=True)
        os.makedirs(processed_employee_folder, exist_ok=True)
        os.makedirs(augmented_employee_folder, exist_ok=True)
        os.makedirs(resized_employee_folder, exist_ok=True)

        split_video_to_frames(saved_video_path, employee_frames_folder)
        time.sleep(1)
        for frame_file in os.listdir(employee_frames_folder):
            frame_path = os.path.join(employee_frames_folder, frame_file)
            process_image(frame_path, processed_employee_folder)
        # print('Process image completed')
        
        shutil.rmtree(employee_frames_folder)
        time.sleep(1)
        # print(f"Beginning augmentation of frames in {processed_employee_folder}")
        process_images_in_subfolders(processed_employee_folder, augmented_employee_folder,)
        # print("Augmentation of frames completed.")

        shutil.rmtree(processed_employee_folder)
        time.sleep(1)
        target_size = 64  # Set the target size for resizing  
        resize_images_and_save(augmented_employee_folder, resized_employee_folder, target_size,employee_id,company_id)
        # print("resize_images_and_save of frames completed.")
        # # send_message(f'approve video process completed for user : {employee_id} , company : {company_id}')

        shutil.rmtree(augmented_employee_folder)
        time.sleep(1)
        new_path=os.path.join(resized_employee_folder,json_name)

        shutil.copy(os.path.join(company_folder_path,json_name),new_path)

        # print('bla blaaaa')
        # os.remove(saved_video_path)
        os.remove(f'{company_folder_path}/{json_name}')
        # print('succesfully deleted s3 files')
        # Mark the video as approved

        video_record.is_approved = True
        video_record.save()

        return redirect('video_approval_page')
    except VideoRecord.DoesNotExist:
        # send_message('error: Video not found...line 680 in views/myapp/ironman')
        return JsonResponse({'error': 'Video not found'}, status=404)

def admin_approval_view(request):
    unapproved_videos = VideoRecord.objects.filter(is_approved=False)
    return render(request, 'approval.html', {'videos': unapproved_videos})


def filter_and_update_file(file_path, excluded_value):
    with open(file_path, 'r') as file:
        data = json.load(file)
    filtered_data = [entry for entry in data if entry.get('image_path', '').split(',')[1] != excluded_value]
    with open(file_path, 'w') as file:
        json.dump(filtered_data, file)
    
    

def delete_employee(request, employee_id):
    try:
        employee = get_object_or_404(Employee, id=employee_id)
        company_id = employee.company.company_id
        employee1 = employee.employee_id
        # print(employee1)
        # print(company_id)

        try:
            x64_folder_path = os.path.join('resized_frames',company_id,employee1)
            if os.path.exists(x64_folder_path):
                shutil.rmtree(x64_folder_path)
        except:
            pass

        try:
            company_path=os.listdir(company_id)
            for jsons in company_path:
                json_path=os.path.join(company_id,jsons)
                # print(jsons)
                # print(json_path)
                filter_and_update_file(json_path,employee1) #Remove From Json Files
                #Removed From Json, Update by sending request
                updatejson = upload_file(UPLOAD_URL, json_path, API_KEY, company_id, FILE_STATUS)
                while updatejson != 200:
                    # print('error updationg, attempting to reconnect to server')
                    updatejson = upload_file(UPLOAD_URL, json_path, API_KEY, company_id, FILE_STATUS)
        except:
            # print('unable to delete user json data')
            # send_message(f'unable to delete user {employee1} json data')
            pass
        employee.delete()
        messages.success(request, f"Employee ID {employee_id} deleted successfully.")
        # send_message(f"Employee ID :{employee_id}_Company ID :{company_id} deleted successfully.")

    except Exception as e:
        # send_message(f'An error occurred while deleting the employee: {e}.....line 745 in views.py/myapp/ironman')
        messages.error(request, f"An error occurred while deleting the employee: {e}")
        return render(request, 'error.html')  # Redirect to an error handling page or another appropriate view

    return redirect('company_page', company_id=company_id)
s3 = S3model.objects.first()


def ups3(filename,uploadpath):
    video_name = os.path.basename(filename)
    # print(video_name)

    # print(f"Access ID = {s3.access_id}")
    # print(f"Access Key = {s3.access_key}")
    # print(f"Access Region = {s3.region}")
    # print(f"Access Bucket Name = {s3.bucket_name}")

    # # print(f"access id = {S3model.access_id}")
    # # print(f"acess key = {S3model.access_key}")
    # # print(f"acess region = {S3model.region}")
    # # print(f"acess bucket name{S3model.bucket_name}")

    upload_file_to_s3(

        aws_access_key_id=s3.access_id, 
        aws_secret_access_key=str(s3.access_key), 
        aws_region=s3.region,
        bucket_name=s3.bucket_name,

        local_file_path=filename,
        s3_object_key=f'Companies/{uploadpath}/{video_name}'
    )

