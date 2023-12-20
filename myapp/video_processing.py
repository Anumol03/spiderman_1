import os
import cv2
import time
import mediapipe as mp
from .pose_estimation import calculate_head_pose  # Ensure this is correctly imported


def split_video_to_frames(video_path, output_directory):
    # Open the video file
    video_capture = cv2.VideoCapture(video_path)
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    # Initialize a frame counter
    frame_count = 0
    while True:
        # Read the next frame
        success, frame = video_capture.read()
        if not success:
            break
        # Save the frame as an image file
        frame_filename = f"{output_directory}/frame_{frame_count:04d}.jpg"
        cv2.imwrite(frame_filename, frame)
        # Increment the frame counter
        frame_count += 1
    # Release the video capture object
    video_capture.release()
    # print('Frames Extracted')



def process_image(filename,dir_folder):
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    os.makedirs(dir_folder,exist_ok=True)
    directions = ["Forward",  "Looking Down", "Looking Side"]
    threshold=10
    smooth_y = None
    directions_folders = [os.path.join(dir_folder, direction) for direction in directions]
    for folder in directions_folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        img = cv2.imread(filename)
        if img is not None:
            img = cv2.flip(img, 1)
            img_h, img_w, _ = img.shape
            img_for_recording = img.copy()
            results = face_mesh.process(img)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=img,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=drawing_spec,
                        connection_drawing_spec=drawing_spec)
                angles = calculate_head_pose(face_landmarks, img_h,img_w)
                x, y, z = angles[0] * 360, angles[1] * 360, angles[2] * 360
                if smooth_y is None:
                    smooth_y = y
                else:
                    smooth_y = smooth_y * 0.9 + y * 0.1
                # Determine the direction
                text = None
                if x > -threshold and -threshold < smooth_y < threshold  :
                    text = "Forward"
                elif x < -threshold:
                    text = "Looking Down"
                elif smooth_y > threshold or smooth_y < -threshold:
                    text = "Looking Side"
                else:
                    pass
                    # print('Undefined')
                if text:
                    frame_dir = os.path.join(dir_folder, text)
                    frame_filename = os.path.join(frame_dir, f"frame_{time.time()}.jpg")
                    # Check if the detected direction is "Looking Side"
                    if text == "Looking Side":
                        # Save a copy to the "Looking Down" folder as well
                        looking_down_dir = os.path.join(dir_folder, "Looking Down")
                        frame_filename_looking_down = os.path.join(looking_down_dir, f"frame_{time.time()}_Looking_Down.jpg")
                        cv2.imwrite(frame_filename_looking_down, img_for_recording)
                    cv2.imwrite(frame_filename, img_for_recording)
        else:
            pass
            print ('no imageeeeee')     
# if __name__ == "__main__":

    # input_video_path = r'C:\Users\user\Desktop\Thor\Batman\cam_dashboard\media\141\videos\Shijin 5656565.webm'
    # output_frames_directory = 'output_frames'
    # user_folder='akshay'
    # output_folder=os.path.join('output',user_folder)
    # folder_64=os.path.join('x64',user_folder)
    # split_video_to_frames(input_video_path, output_frames_directory)
    # for filename in os.listdir(output_frames_directory):
    #     img = os.path.join(output_frames_directory, filename)
    #     process_image(img,user_folder)

    # process_images_in_subfolders(user_folder,output_folder)
    # resize_images_and_save(output_folder,folder_64,64)
    # if os.path.exists(output_frames_directory):
    #     shutil.rmtree(output_frames_directory)
    # if os.path.exists(user_folder):
    #     shutil.rmtree(user_folder)
    # if os.path.exists(output_folder):
    #     shutil.rmtree(output_folder):