import cv2
import requests
import time
import json
import glob
import sys
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.storage.blob import BlobServiceClient 
from datetime import datetime

# Variables
path = 'C:\\Users\\ricardo.cauduro\OneDrive - Kumulus\\Desktop\\Data\\NTB'

credential = json.load(open('{}\\key.json'.format(path)))
KEY = credential['KEY']
ENDPOINT = credential['ENDPOINT']

storage_account_key = credential['storage_account_key']
storage_account_name = credential['storage_account_name']
connection_string = credential['connection_string']
container_name = credential['container_name']

face_api_url = "https://eastus.api.cognitive.microsoft.com/face/v1.0/detect"
headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': KEY}
params = {'detectionModel': 'detection_01', 'returnFaceId': 'true', 'returnFaceRectangle': 'true', 'returnFaceAttributes': 'age, gender, emotion'}

GRUPOS = []
PESSOAS = []
ID = []

face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

# Functions
def criar_grupo(grupo):
    face_client.person_group.create(person_group_id=grupo, name=grupo)
    print('Criado o grupo {}'.format(grupo))

def criar_pessoa(pessoa, grupo):
    globals()[pessoa] = face_client.person_group_person.create(grupo, pessoa)
    print('Person ID:', globals()[pessoa].person_id)
    ID.append(globals()[pessoa].person_id)

    listaFotos = [file for file in glob.glob('*.jpg') if file.startswith(pessoa)]
    time.sleep(1)
    for image in listaFotos:
        face_client.person_group_person.add_face_from_stream(
            GRUPOS[0], globals()[pessoa].person_id, open(image, 'r+b'))
        print('Incluida foto {}'.format(image))
        time.sleep(1)

def treinar(grupo):
    print('Iniciando treino de {}'.format(grupo))
    face_client.person_group.train(grupo)
    while (True):
        training_status = face_client.person_group.get_training_status(grupo)
        print("Training status de {}: {}.".format(grupo, training_status.status))
        if (training_status.status == 'succeeded'):
            break
        elif (training_status.status == 'failed'):
            face_client.person_group.delete(person_group_id=grupo)
            sys.exit('Training the person group has failed.')
        time.sleep(5)

def uploadToBlobStorage(file_path,file_name)
   blob_service_client = BlobServiceClient.from_connection_string(connection_string)
   blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
   with open(file_path,'rb') as data:
      blob_client.upload_blob(data)
      print('Uploaded {}.'.format(file_name))

def iniciar():
    GRUPOS.append(input('Defina o nome do grupo -> ').lower())
    list(map(lambda x: criar_grupo(x), GRUPOS))
    
    lista_pessoas = []
    nome_pessoa = None
    while nome_pessoa != 'fim':
        nome_pessoa = input("Digite o nome da pessoa para associar ao grupo '{}' ou digite 'fim' para terminar. -> ".format(GRUPOS[0])).lower()
        if nome_pessoa != 'fim':
            PESSOAS.append(nome_pessoa)
            lista_pessoas.append(nome_pessoa)
    
    if len(lista_pessoas) == 1:
        print('{} foi adicionado ao grupo {}'.format(PESSOAS[0], GRUPOS[0]))
    else:
        ultimo_nome = lista_pessoas.pop()
        nomes = ', '.join(lista_pessoas)
        print('{} e {} foram adicionados ao grupo {}'.format(nomes, ultimo_nome, GRUPOS[0]))

    list(map(lambda x: criar_pessoa(x,GRUPOS[0]), PESSOAS))
    list(map(lambda x: treinar(x), GRUPOS))

    cam = cv2.VideoCapture(0)

    while True:
        folder_date = datetime.now().date().strftime('%Y%m%d')
        filename_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        ret, frame = cam.read()
        image = cv2.imencode('.jpg', frame)[1].tobytes()

        response = requests.post(face_api_url, params=params, headers=headers, data=image)
        response.raise_for_status()
        faces = response.json()
        face_ids = [face['faceId'] for face in faces]

        global results
        for face in face_ids:
            results = face_client.face.identify(face_ids, GRUPOS[0])

        # Get landmarks
        for n, (face, person, id, nome) in enumerate(zip(faces, results, ID, PESSOAS)):
            rect = face['faceRectangle']
            left, top = rect['left'], rect['top']
            right = int(rect['width'] + left)
            bottom = int(rect['height'] + top)

            draw_rect = cv2.rectangle(frame,(left, top), (right, bottom),(0, 255, 0), 3)
            
            att = face['faceAttributes']
            age = att['age']

            if len(person.candidates) > 0 and str(person.candidates[0].person_id) == str(id):
                print('Person for face ID {} is identified in {}.{}'.format(person.face_id, 'Frame',person.candidates[0].person_id))
                draw_text = cv2.putText(frame, 'Nome: {}'.format(nome), (left, bottom + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 255), 1,cv2.LINE_AA)
                faces[n]['nome'] = str(nome)  
            else:
                draw_text = cv2.putText(frame, 'Nome: Desconhecido', (left,bottom+50),cv2.FONT_HERSHEY_TRIPLEX , 0.5,(0 ,0 ,255 ),1,cv2.LINE_AA)
                faces[n]['nome'] ='Desconhecido'
        
        cv2.imshow('face_rect', draw_rect)

        # Create the file with the video captured data
        faces = [{**face, 'timeStamp': str(datetime.now()), 'bottomSize': str(bottom), 'location': 'Casa'} for face in faces]
        json_string = json.dumps(faces, separators=(',', ':'))

        with open('output\mydata-{}.json'.format(filename_date), 'w') as f:
            json.dump(json.JSONDecoder().decode(json_string), f)
            
        # Calling a function to perform upload
        uploadToBlobStorage('output\mydata-{}.json'.format(filename_date),'{}/mydata-{}.json'.format(folder_date,filename_date))

        k = cv2.waitKey(1) & 0xFF # bitwise AND operation to get the last 8 bits
        if k == 27:
            print("Escape hit, closing...")
            break

def fim(nome_do_grupo):
    cv2.destroyAllWindows()
    face_client.person_group.delete(person_group_id = nome_do_grupo)

# Start the code
iniciar()

# Stop and clean
fim('nome_do_grupo')
