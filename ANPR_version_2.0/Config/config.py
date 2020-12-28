# ------------------- CUSTOM VISION KEYS ------------------------------ #
custom_vision_key = '744fd5a0b6284d5685fd5f185d744634'
subscription_key = '4e6eae17c8924b058f16d2f59ff2b90f'
prediction_key = '39f1ac34bc8246ccbd22ad93ae0b7d36'
content_type = 'application/octet-stream'
custom_vision_endpoint = 'https://customvission.cognitiveservices.azure.com/'

#---------------------HEADERS------------------------------------------#
custom_vision_headers = {'Content-Type': content_type, 'Prediction-Key': prediction_key}

# ------------------- MODEL ITERATION VERSION ------------------------ #
iteration_name =  'Iteration3'

# ------------------- Number Plate Detection ------------------------- #
custom_vision_imgurl = custom_vision_endpoint + 'customvision/v3.0/Prediction/10f14000-1d93-4139-89ac-f51eafa69d4e/detect/iterations/' + iteration_name + '/image'
#'https://customvission.cognitiveservices.azure.com/customvision/v3.0/Prediction/10f14000-1d93-4139-89ac-f51eafa69d4e/detect/iterations/Iteration2/image'
# ------------------- TEXT RECOGNITION URL -------------------------- #
text_recognition_url = custom_vision_endpoint + "vision/v2.1/read/core/asyncBatchAnalyze"
# 'https://customvission.cognitiveservices.azure.com/vision/v2.1/read/core/asyncBatchAnalyze'
# ------------------- CAMERA URLS ------------------------------------ #
url= 'http://192.168.2.32:8080/video'
#url= 'http://192.168.2.163:8080/video'

# ------------------- MP4 Files -------------------------------------- #
#video = 'testing_images/testvideo3.mp4'
#video = 'F:\MetisWork\HEC_ANPR\HEC Cameras Recording\HEC-Exit Gate-Bullet Cam.mp4'
#video = 'F:\MetisWork\HEC_ANPR\HEC Cameras Recording\HEC_trim.mp4'
video = 'F:\MetisWork\Metis_projects\HEC-POC-demo-template\HEC-ENTRY-GATE-Bullet Cam.mp4'

#-------------------- THRESHOLD DEFINATION---------------------------- #
car_threshold = 0.5
numberplate_threshold = 0.4
frame_skip = 5
delay_counter = 0                 # increase if there is need of skipping sending response to text API  

#------------------------Parameters for saving data in excel------------#
csv_folder_name = 'Excel'
csv_file_name = 'testing.csv'
image_folder_name = 'Data'
date_time_format = '%Y-%m-%d - Time: '+'%H:%M'

img_save_date_time = "-%Y-%m-%d-Time-"+"%H_%M"
