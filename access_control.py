import face_recognition
import cv2
import numpy as np
import os
import glob
import re
import urllib.request
from datetime import datetime
import json
from azure.storage.blob import BlobServiceClient
import time

def sendRequest(url):
    try:
        urllib.request.urlopen("{}/open".format(root_url))
    except Exception as e:
        if e == "Remote end closed connection without response":
            pass

def get_name(nome):
    padrao = r"\\([^\\]+?)\."
    match = re.search(padrao, nome)
    if match:
        name = match.group(1)
        return name

def uploadToBlobStorage(data,file_name):
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    blob_client.upload_blob(data)


# ESP-01 web server address
root_url = "http://192.168.0.174"

# Storage variables
connect_str = os.getenv("connect_str")
container_name = "landing-zone"

# Load the face and eye cascade classifiers
classificador = cv2.CascadeClassifier("haarcascade-frontalface-default.xml")
classificadorOlho = cv2.CascadeClassifier("haarcascade-eye.xml")

# Open the camera
camera = cv2.VideoCapture(0)

# Part I -> Capture
amostra = 1
numeroAmostra = 1
nome = input("Digite seu nome: ")
id = input("Digite seu identificador: ")
largura, altura = 220, 220
print("Capturando as faces...")

while(True):
    # Read the camera frame
    conectado, imagem = camera.read()

    # Convert the frame to grayscale
    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    facesDetectadas = classificador.detectMultiScale(imagemCinza, scaleFactor=1.5, minSize=(150,150))

    for(x, y, l, a) in facesDetectadas:
        # Draw a rectangle around the detected face
        cv2.rectangle(imagem, (x,y), (x + l, y+ a), (0, 0, 255), 2)

        # Extract the region of interest (face)
        regiao = imagem[y:y + a, x:x + l]

        # Convert the region of interest to grayscale
        regiaoCinzaOlho = cv2.cvtColor(regiao, cv2.COLOR_BGR2GRAY)

        # Detect eyes within the region of interest
        olhosDetectatos = classificadorOlho.detectMultiScale(regiaoCinzaOlho)
        for (ox, oy, ol, oa) in olhosDetectatos:
            # Draw a rectangle around the detected eyes
            cv2.rectangle(regiao, (ox, oy), (ox + ol, oy + oa), (0, 255, 0), 2)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                # Capture if we got a good quality image
                if np.average(imagemCinza) > 110:

                    # Resize the captured face image to a fixed size
                    imagemFace = cv2.resize(imagemCinza[y:y + a, x:x + l], (largura, altura))

                    # Save the resized image
                    cv2.imwrite("fotos/{}.{}.{}.jpg".format(nome, str(id),str(amostra)), imagemFace)
                    print("[foto {} capturada com sucesso]".format(str(amostra)))
                    amostra += 1

    # Display the results
    cv2.imshow("Face", imagem)
    cv2.waitKey(1)

    # If enough pictures were collected, then stop capture
    if(amostra >= numeroAmostra +1):
        break

print ("Faces capturadas com sucesso")
camera.release()
cv2.destroyAllWindows()


# Part II -> Encoding

# Initialize empty lists to store face data
faces_encodings = []
faces_names = []
cur_direc = os.getcwd()
path = os.path.join(cur_direc, "fotos/")
list_of_files = [f for f in glob.glob("{}*.jpg".format(path))]


for i, v in enumerate(list_of_files):
    globals()["image_{}".format(i)] = face_recognition.load_image_file(list_of_files[i])
    globals()["image_encoding_{}".format(i)] = face_recognition.face_encodings(globals()["image_{}".format(i)])[0]
    faces_encodings.append(globals()["image_encoding_{}".format(i)])
    faces_names.append(get_name(v))
    print("encoding ok")

# Part II -> Validate and Display
    
# Initialize empty lists to store face data
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
acesso = False

# Create VideoCapture object to access the webcam
video_capture = cv2.VideoCapture(0)
while True:
    folder_date = datetime.now().date().strftime("%Y%m%d")
    filename_date = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Read the video frame
    ret, frame = video_capture.read()

    # Resize the frame for faster processing
    small_frame = cv2.resize(frame, (200, 200))

    # Convert the frame from BGR to RGB format
    rgb_small_frame = small_frame[:, :, ::-1]
    if process_this_frame:
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # Clear the list of face names
        face_names = []

        # Iterate over each face encoding
        for face_encoding in face_encodings:

            # Compare face encoding with known faces
            matches = face_recognition.compare_faces(faces_encodings, face_encoding)
            name = "Unknown"
            
            # Compute face distances to find the best match
            face_distances = face_recognition.face_distance(faces_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            # If there is a match, assign the corresponding name
            if matches[best_match_index]:
                name = faces_names[best_match_index]

            # Add the name to the list of face names
            face_names.append(name)

    process_this_frame = not process_this_frame
    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top = top * 4 - 200
        right = right * 4 - 100
        bottom = bottom * 4 - 200
        left = left * 4 - 100

        # Draw a rectangle around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Input text label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow("Video", frame)

        if (right > 480) and (name != "Unknown"):
            sendRequest(root_url)
            acesso = True
        
    # Gerando o arquivo com as informações captadas pelo video
    faces = [{"nome": name, "acesso": acesso, "timeStamp": str(datetime.now()), "bottomSize": str(bottom), "location": "Casa"} for face in zip(face_locations, face_names)]
    json_string = json.dumps(faces, separators=(",", ":"))
    time.sleep(1)
    uploadToBlobStorage(json_string,"{}/mydata-{}.json".format(folder_date,filename_date))

    acesso = False

    # Hit "q" on the keyboard to quit!
    k = cv2.waitKey(1)
    if k%256 == 27:
        print("Escape hit, closing...")
        break

video_capture.release()
cv2.destroyAllWindows()
