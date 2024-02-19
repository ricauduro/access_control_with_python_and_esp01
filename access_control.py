import face_recognition
import cv2
import numpy as np
import os
import glob
import re
import urllib.request
import time

root_url = "http://192.168.0.174"


def sendRequest(url):
    try:
        urllib.request.urlopen("{}/open".format(root_url))
    except Exception as e:
        if e == "Remote end closed connection without response":
            pass


def get_name(nome):
    padrao = r'\\([^\\]+?)\.'
    match = re.search(padrao, nome)
    if match:
        name = match.group(1)
        return name



classificador = cv2.CascadeClassifier("haarcascade-frontalface-default.xml")
classificadorOlho = cv2.CascadeClassifier("haarcascade-eye.xml")
camera = cv2.VideoCapture(0)
amostra = 1
numeroAmostra = 1
nome = input('Digite seu nome: ')
id = input('Digite seu identificador: ')
largura, altura = 220, 220
print("Capturando as faces...")


while(True):
    conectado, imagem = camera.read()
    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    facesDetectadas = classificador.detectMultiScale(imagemCinza, scaleFactor=1.5, minSize=(150,150))

    for(x, y, l, a) in facesDetectadas:
        cv2.rectangle(imagem, (x,y), (x + l, y+ a), (0, 0, 255), 2)
        regiao = imagem[y:y + a, x:x + l]
        regiaoCinzaOlho = cv2.cvtColor(regiao, cv2.COLOR_BGR2GRAY)
        olhosDetectatos = classificadorOlho.detectMultiScale(regiaoCinzaOlho)
        for (ox, oy, ol, oa) in olhosDetectatos:
            cv2.rectangle(regiao, (ox, oy), (ox + ol, oy + oa), (0, 255, 0), 2)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                if np.average(imagemCinza) > 110:
                    imagemFace = cv2.resize(imagemCinza[y:y + a, x:x + l], (largura, altura))
                    cv2.imwrite("fotos/{}.{}.{}.jpg".format(nome, str(id),str(amostra)), imagemFace)
                    print("[foto {} capturada com sucesso]".format(str(amostra)))
                    amostra += 1

    cv2.imshow("Face", imagem)
    cv2.waitKey(1)
    if(amostra >= numeroAmostra +1):
        break

print ("Faces capturadas com sucesso")
camera.release()
cv2.destroyAllWindows()


faces_encodings = []
faces_names = []
cur_direc = os.getcwd()
path = os.path.join(cur_direc, 'fotos/')
list_of_files = [f for f in glob.glob(path+'*.jpg')]
names = list_of_files.copy()

for i,v in enumerate(list_of_files):
    globals()['image_{}'.format(i)] = face_recognition.load_image_file(list_of_files[i])
    globals()['image_encoding_{}'.format(i)] = face_recognition.face_encodings(globals()['image_{}'.format(i)])[0]
    faces_encodings.append(globals()['image_encoding_{}'.format(i)])
    # Create array of known names
    names[i] = names[i].replace(cur_direc, "")  
    faces_names.append(names[i])
    print('encoding ok')


face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

print('ligando camera')
video_capture = cv2.VideoCapture(0)
while True:
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (200, 200))
    rgb_small_frame = small_frame[:, :, ::-1]
    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(faces_encodings, face_encoding)
            name = "Unknown"
            
            face_distances = face_recognition.face_distance(faces_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = get_name(faces_names[best_match_index])
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
        cv2.imshow('Video', frame)

        print((right, bottom))
        print(name)

        if (right > 480) and (name != "Unknown"):
            print('ok')
            sendRequest(root_url)
        else:
            print('não detectado')
        
        # Hit 'q' on the keyboard to quit!
    k = cv2.waitKey(1)
    if k%256 == 27:
        print("Escape hit, closing...")
        break

video_capture.release()
cv2.destroyAllWindows()
