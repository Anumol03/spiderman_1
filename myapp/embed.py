import os
import cv2
import json
import django
from insightface.app import FaceAnalysis
from myapp.models import SpiderApi
from myapp.req import upload_file,send_message



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JeztX.settings')
django.setup()

# Fetch the first SpiderApi object from the database
# Note: Modify this part as per your requirement, e.g., using filters
spider_api = SpiderApi.objects.first() if SpiderApi.objects.exists() else None

if spider_api:
    API_KEY = spider_api.api_key
    FILE_STATUS = spider_api.file_status
    UPLOAD_URL = spider_api.url


# #Models
# API_KEY = 'ApiKeyForUser2'   #Key For Spider man
# # FILE_ID = '534343'
# FILE_STATUS = 'New'
# # FILE_PATH = 'rrr.txt'
# UPLOAD_URL = 'http://192.168.29.143:1122/upload/' #upload url


def extract_face_features(user_folder, person_name, companyid):

    faceapp = FaceAnalysis(name='buffalo_l',
                           root='insightface_model',
                           providers=['CPUExecutionProvider'])
    
    faceapp.prepare(ctx_id=0, det_size=(640, 640), det_thresh=0.5)

    # Create the 'output' folder if it doesn't exist
    output_folder = companyid

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate through each subfolder in the main folder
    for subfolder in os.listdir(user_folder):
        subfolder_path = os.path.join(user_folder, subfolder)
        
        # Check if it's a directory
        if os.path.isdir(subfolder_path):
            output_json_file = os.path.join(output_folder, f"{subfolder}_{companyid}.json")
            embeddings = []

            # Load existing data if the file exists
            if os.path.isfile(output_json_file):
                with open(output_json_file, 'r') as json_file:
                    embeddings = json.load(json_file)

            # Process each image in the subfolder
            for file in os.listdir(subfolder_path):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                    image_path = os.path.join(subfolder_path, file)
                    img = cv2.imread(image_path)
                    res = faceapp.get(img, max_num=0)

                    for i, rt in enumerate(res):
                        bbox = rt['bbox'].astype(int)
                        score = int(rt['det_score'] * 100)
                        embed = rt['embedding']
                        y = embed.reshape(1, 512)

                        embeddings.append({
                            'image_path': person_name,
                            'bbox': bbox.tolist(),
                            'det_score': score,
                            'Facial_Features': y.tolist()
                        })

            # Save the updated embeddings to the JSON file
            with open(output_json_file, 'w') as json_file:
                json.dump(embeddings, json_file)

            print(f"Embeddings for {subfolder} saved to: {output_json_file}")
            try:
                response = upload_file(UPLOAD_URL, output_json_file, API_KEY, companyid, FILE_STATUS)
                print(response.text)
            except:
                send_message(f"api unable to fetch {subfolder}")
                print("api unable to fetch")
                pass


            
            
            


