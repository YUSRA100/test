from Config import config
import re
import requests
import time
import numpy as np
import cv2
from PIL import Image
import csv
import itertools
import os
import os.path
from os import path
from collections import Counter
#from imutils.video import VideoStream

def ANPR_Enable():
    try:    
        totalFrames = 0
        timer = 0
        videowriter = None
        width = None
        height = None
        image_save = None
        words = []
        temp_text_array = []
       #---------------------- DATA FOLDER CREATION SNIPPET ---------------------------                            
        csv_folder_name = config.csv_folder_name
        image_folder_name = config.image_folder_name
        
        print("current dir is: %s" % (os.getcwd()))            
        if os.path.isdir(csv_folder_name) and os.path.isdir(image_folder_name):
            print("Excel and Image Data Folder Exists")
        else:
            print("Excel and Image Data Folder Created")
            try:
                os.mkdir(csv_folder_name)
                os.mkdir(image_folder_name) 
            except FileExistsError:
                pass
                        
        def ArrayMatch(temp_text_array, time_stamp, image_save, image_save_date_time):
            print("------------INSIDE ARRAY FUNCTION----------------")
            if temp_text_array:
                counts = Counter(temp_text_array).most_common()
#                print("The frequencey list is : ", counts)
                if len(counts) < 3:
                    #---------------------- NUMBER PLATE TEXT SENDING IN EXCEL TO BE STORED ---------------------------                    
                    SaveText(counts[-1][0], time_stamp)
                    image_name = counts[-1][0]+ image_save_date_time
                    #--------------------- NUMBER PLATE IMAGE SAVED WITH EXTRACTED NAME AND DATE-TIME FORMAT DEFINATION -------------------                    
                    image_save.save(image_folder_name+'/'+image_name+ '.jpg')
                else:                                                    
                    print("Targetted value to be stored", counts[0][0])
                    SaveText(counts[0][0], time_stamp)
                    image_name = counts[0][0]+ image_save_date_time
                    #--------------------- NUMBER PLATE IMAGE SAVED WITH EXTRACTED NAME AND DATE-TIME FORMAT DEFINATION -------------------
                    image_save.save(image_folder_name+'/'+image_name+'.jpg')
            else:
                print("List is empty, no response recorded yet")
        #-------------------------------- FUNCTION FOR SAVING EXTRACTED INFORMATION TO CSV FILE--------------------------
        def SaveText(joinwords, time_stamp):
            print("-----------INSIDE DATA STORING FUNCTION------------")
            joinwords = [joinwords]    
            print("Text converted: ", joinwords)
            csv_file_name =  config.csv_file_name            
            file = csv_folder_name+'/'+csv_file_name
            header = ['Number Plate', 'Date_Time']
            if path.exists(file):
                print("Excel File exists")
                with open(file, 'r+',newline='') as f:
                    read_data = f.readlines()
                    lastRow = read_data[-1]
                    if joinwords[0] in lastRow:
                        print("Repetitive entry")
                        joinwords=[]
                    else:
                        joinwords.append(time_stamp)
                        csv_writer = csv.writer(f)
                        csv_writer.writerow(joinwords)
                        print("Data has been entered")
                        joinwords= []
            else:
               try:
                   with open(file, "w", newline='') as f:
                       csv_writer = csv.writer(f, delimiter=',')
                       csv_writer.writerow(header)
                       joinwords.append(time_stamp)
                       csv_writer.writerow(joinwords)
                       print("New File has been made")
               except:
                    print("An error occurred while writing the file.")
        #-------------------------------------------- READING VIDEO DATA--------------------------------------------------                               
        vs = cv2.VideoCapture(config.video)
        print("[INFO]---starting video stream...") 
        ''' 
        USE src = 0 IF WEBCAM ACCESS IS REQUIRED , e.g vs = VideoStream(src=0).start()
        USE src = config.video IF LOCAL VIDEO TESTING IS REQUIRED, e.g vs = VideoStream(src=config.video).start()
        '''
#        vs = VideoStream(src=config.url).start()  
#        time.sleep(2.0)
        if (vs.isOpened()== False): 
            print("Error opening video file")
        car_detect_flag = False
        numplate_detect_flag = False        
        custom_vision_resp = None
        #------------------------ SECTION FOR TRIMIMING VIDEO AS PER FRAME RATE (fps)---------------------------------------------                               
        fps = vs.get(cv2.CAP_PROP_FPS)                        # Get the frames per second
        frame_count = vs.get(cv2.CAP_PROP_FRAME_COUNT)        # Get the total numer of frames in the video.
#        frame_number = 2970                            # for all other cars
        frame_number = 640                              # for first car
        vs.set(cv2.CAP_PROP_POS_FRAMES, frame_number)   # starts reading video from defined 'frame_number' value
        #--------------------------------------------------------------------------------------------------                               

        while (vs.isOpened()== True):  
            ret, frame = vs.read()
            if frame is None:                
                print("frame not found")
                if temp_text_array is not None: # if video ends, save the data stored in array
                    ArrayMatch(temp_text_array, time_stamp, image_save, image_save_date_time)
                break
                
            if width is None or height is None:
                (height, width) = frame.shape[:2]
            # check to see if we should write the frame to disk
#            frame = frame[170:550,300:850]
#            frame = frame[230:550,300:900] #with resize
            frame = frame[250:690,400:1300]                 # ROI DEFINATION
            #--------------------------------------- VIDEO SAVING ------------------------------------
            if videowriter is None:
                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                videowriter = cv2.VideoWriter(image_folder_name+'/'+'ANPR_HEC_trim.avi', fourcc, 15, (width, height), True)
            #--------------------------------------- PROCESSING INITIATES ---------------------------    
            if totalFrames % config.frame_skip == 0: 
              
                im = Image.fromarray(frame) 
                im.save(image_folder_name+'/videoframe.jpg')
                data = open(image_folder_name+'/videoframe.jpg', 'rb').read()
                print("----------Frame saved and passed for object detection response-------------") 
                img = cv2.imdecode(np.array(bytearray(data), dtype='uint8'), cv2.IMREAD_COLOR) #Decoding byte image array
                try:
                    custom_vision_resp = requests.post(url = config.custom_vision_imgurl, data=data, headers = config.custom_vision_headers).json()
                except:
                    print("Problem getting response")
                    pass
                #--------------------------------- CUSTOM VISION RESPONSE CHECKS --------------------                       
                if custom_vision_resp is None:
                    print("Response not found")
                else:
                    for i in custom_vision_resp['predictions']: 
                        if i['tagName'] == 'car':
                            if i['probability'] > config.car_threshold:
                                print("Car detected with probability greater than 0.5")
                                pass
                                car_detect_flag= True
                        if i['tagName'] == 'number plate': 
                            if i['probability'] > config.numberplate_threshold:
                                print("Number plate detected ")
                                numplate_detect_flag = True
                                bbox = i      
    #                            break
                if car_detect_flag:
                    if numplate_detect_flag:
                        boundingbox = bbox['boundingBox']
                        l,t,w,h = (boundingbox['left'], boundingbox['top'], boundingbox['width'], boundingbox['height'])
                        print(l,t,w,h) 
    #                    cv2.rectangle(frame,(l,t),(w,h), (0, 0, 255), 2)
                        polylines1 = np.multiply([[l,t],[l+w,t],[l+w,t+h],[l,t+h]], [img.shape[1],img.shape[0]])
                        img2 = cv2.polylines(img, np.int32([polylines1]), 1, (255,255,0), 4, lineType=cv2.LINE_AA )
                        crop_x = polylines1[:,0].astype('uint16')
                        crop_y = polylines1[:,1].astype('uint16')
                        img_crop = img2[np.min(crop_y):np.max(crop_y), np.min(crop_x):np.max(crop_x)]
#                        print("Cropped image shape is",img_crop.shape)
                        if (img_crop.shape[0] < 50) or (img_crop.shape[1] < 50):
                            img_crop = cv2.resize(img_crop, (50, 50)) 
#                            print("Image has been resized, new size is: ", img_crop.size)
            # ------------------------------------ CROPPED-FRAME PREPROCESSING  ----------------------------------
                        gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)   
                        crop_bytes =bytes(cv2.imencode('.jpg', gray)[1]) 
            # ---------------------------------- SENDING RESPONSE TO TEXT RECOGNITION API--------------------------
                        response = requests.post(
                            url= config.text_recognition_url, 
                            data = crop_bytes, 
                            headers = {'Ocp-Apim-Subscription-Key': config.subscription_key, 'Content-Type': config.content_type})
                        # Holds the URI used to retrieve the recognized text.
                        if response.text == '':
                            print("Response not avaliable")
                            pass
                        response.raise_for_status()
                        # The recognized text isn't immediately available, so poll to wait for completion.
                        analysis = {}
                        poll = True
                        while (poll):
                            response_final = requests.get(
                                response.headers["Operation-Location"], headers={'Ocp-Apim-Subscription-Key': config.subscription_key})
                            analysis = response_final.json()
#                            print(analysis)
                            time.sleep(1)
                            if ("recognitionResults" in analysis):
                                poll = False
                            if ("status" in analysis and analysis['status'] == 'Failed'):
                                poll = False
                        #--------------------------------- EXTRACTING RETURNED RESPONSE FROM JSON -------------------------------------------               
                        empty = [] 
                        for i,l in enumerate(analysis['recognitionResults'][0]['lines']): 
                             print("Checking the values in words", words)
                             words.append([w['text'] for w in l['words']])
                             print(i, ': text found: ', [w['text'] for w in l['words']])
                             for word in words:
                                 if word not in empty:
                                     empty.append(word)
                             words = []
                        #---------------------------------- MERGING AND JOINING LISTS OF EXTRACTED WORDS -----------------------------------
                        mergewords = list(itertools.chain.from_iterable(empty))
                        joinwords = ['-'.join(mergewords)]
                        print("The extracted string word is:", joinwords)
                        # REPLACING SPECIAL CHARACTHERS WITH DASH
                        replaced = re.sub("[>]+|[<]+|[$]+|[.]+|[-]+|[:]+|[#]+|[(]+|[)]+|[\"]+","-",joinwords[0])
                        # REPLACING MULTIPLE DASHES
                        replaced = re.sub("[-]+","-",replaced)
                        print("Replaced String is: ",replaced)
                         # CHECKING SEQUENCE AND RANGE OF LETTERS AND NUMERALS
                        sequence_check = re.search("([A-Z][-]+[A-Z])|([0-9][-]+[0-9])|(^[-])|([-]$)",replaced)
                        check4 = re.search("[A-Z]{2,3}-[0-9]{1,2}-[0-9]{1,4}",replaced)
                        if check4:
                           a, b, c = check4[0].split('-')
                           replaced = a+'-'+c
                           print("SPECIAL CASE REPLACED VALUE", replaced)
                        #----------------CUSTOMIZED NUMBER PLATE-----------------------------
#                            check5=re.search("[A-Z]{5,7}-[A-Z]{1,2}-[0-9]{1,4}",replaced)
#                            if check5:
#                                print("super Special case alert")
#                                print("-------", check5[0])
                        #--------------------------------------------------------------------    
                        if sequence_check is not None:
                            print("Misleading sequence found, skipping the data")
                        replace_check = re.search("[A-Z]{2,3}-[0-9]{2,4}",replaced)
                        if replace_check is not None:
                            print("Both letters and numbers are in range: ",replace_check[0])
                            replaced = replace_check[0]                        
                            print("THE VALUE IN TEXT VARIABLE IS: ",temp_text_array)
                            if len(temp_text_array) == 0:
#                                print("text array initiates")
                                temp_text_array.append(replaced)                                
                                time_stamp = time.strftime(config.date_time_format)  # time format
                                print("text final string is: ",temp_text_array)
                                image_save_date_time = time.strftime(config.img_save_date_time)
                                image_save = Image.fromarray(frame)                                
                            else:
                                if len(temp_text_array) != 0:
                                    forward_alphabet, forward_number = replaced.split('-')
                                    if temp_text_array[-1] == replaced:
                                        print("--------REPEATITIVE string FOUND-----")                                                                                  
                                    else:
                                        reverse_alphabet, reverse_number = temp_text_array[-1].split('-')
                                        if forward_number in reverse_number or forward_alphabet in reverse_alphabet:
                                                print("Found recurring alphabets or numbers from the last entry") 
                                                temp_text_array.append(replaced)
                                        else:                                                
                                            ################------Function call---##############
                                            print("ARRAY MATCH FUNCTION CALL")
                                            ArrayMatch(temp_text_array,time_stamp, image_save, image_save_date_time)
                                            temp_text_array = []    #CLEAR ARRAY FOR NEXT ENTRY
                                            image_save = Image.fromarray(frame)     #SAVING CORRESPONDING IMAGE
                                            image_save_date_time = time.strftime(config.img_save_date_time)
                                            time_stamp = time.strftime(config.date_time_format)
                                            print("NEW LIST", temp_text_array)                                                
                        else:
                            timer += 1
                            print("Not saving data in database, value of response variable is", timer)     
                            if timer > 10:
                                print("Response Time Exceeded, text array contents are : ", temp_text_array)
                                if image_save is not None:
                                    ArrayMatch(temp_text_array, time_stamp, image_save, image_save_date_time)
                                    timer = 0
                                else:
                                    print("No Image and text found")
                # check to see if we should write the frame to disk
                if videowriter is not None:
                    videowriter.write(frame)                                            
            totalFrames+=1
            cv2.imshow("Frame", frame)          
            # if the `q` key was pressed, break from the loop
            if cv2.waitKey(1) & 0xFF == ord("q"):                
                break
 
        cv2.destroyAllWindows()
        vs.release()
    except:
        print("Problem found while detection")
        ANPR_Enable()
        
#ANPR_Enable()
        