import numpy as np
import cv2
from imgaug import augmenters as iaa
import os
from PIL import Image

def calculate_head_pose(face_landmarks, img_h, img_w):
    face_3d = []
    face_2d = []
    for idx, lm in enumerate(face_landmarks.landmark):
        if idx in [33, 263, 1, 61, 291, 199]:
            x, y = int(lm.x * img_w), int(lm.y * img_h)
            face_2d.append([x, y])
            face_3d.append([x, y, lm.z])
    face_2d = np.array(face_2d, dtype=np.float64)
    face_3d = np.array(face_3d, dtype=np.float64)
    # Assuming focal length is a fraction of the image width
    focal_length = 0.5 * img_w
    cam_matrix = np.array([
        [focal_length, 0, img_w / 2],
        [0, focal_length, img_h / 2],
        [0, 0, 1]
    ])
    dist_matrix = np.zeros((4, 1), dtype=np.float64)
    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
    rmat, jac = cv2.Rodrigues(rot_vec)
    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
    return angles

def process_images_in_subfolders(input_folder, output_parent_folder):
        print(f"Starting image augmentation from {input_folder} to {output_parent_folder}")
        os.makedirs(output_parent_folder, exist_ok=True)
        augmentation = iaa.Sequential([
            iaa.Fliplr(0.5),
            iaa.Affine(rotate=(-20, 20)),
            iaa.GaussianBlur(sigma=(0, 1.0)),
            iaa.GammaContrast(gamma=(0.5, 2.0))
        ])
        for root, subfolders, files in os.walk(input_folder):
            for subfolder in subfolders:
                subfolder_path = os.path.join(root, subfolder)
                output_subfolder = os.path.join(output_parent_folder, subfolder)
                os.makedirs(output_subfolder, exist_ok=True)
                for image_filename in os.listdir(subfolder_path):
                    if image_filename.endswith(('.jpg', '.jpeg', '.png')):
                        image_path = os.path.join(subfolder_path, image_filename)
                        image_name = os.path.splitext(image_filename)[0]
                        image = cv2.imread(image_path)
                        # Augment the image
                        num_augmentations = 5
                        for i in range(num_augmentations):
                            augmented_image = augmentation.augment_image(image)
                            augmented_filename = os.path.join(output_subfolder, f'{image_name}_augmented_{i}.jpg')
                            cv2.imwrite(augmented_filename, augmented_image)
        process = print("Images in subfolders processed and augmented.")
        return(process)

def resize_images_and_save(input_folder, output_folder, target_size,id,cmpny_id):
    print(f"Starting resizing of images in {input_folder} to {target_size}x{target_size} pixels.")
    os.makedirs(output_folder, exist_ok=True)
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                img = Image.open(os.path.join(root, filename))
                resized_img = img.resize((target_size, target_size), Image.BILINEAR)
                relative_path = os.path.relpath(root, input_folder)
                output_subfolder = os.path.join(output_folder, relative_path)
                os.makedirs(output_subfolder, exist_ok=True)
                resized_filename =f"{id}_{cmpny_id}"+ os.path.splitext(filename)[0] + f'_resized_{target_size}.jpg'
                resized_img.save(os.path.join(output_subfolder, resized_filename))