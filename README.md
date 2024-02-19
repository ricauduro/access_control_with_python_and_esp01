# Access control with Python and ESP01 (under construction)

 Formerly, this project was using Azure Face API to perform face recognition, but once this service is not available anymore for personal accounts, only for managed partners, I decided to build my own face recognition model, to use it with this project. It´s not an advanced model, but it will do the work for us.

 The goal of this project is to create an access control system, which will grant or deny access to any place based on the video captured with a camera in front of a door...something like this

![image](https://github.com/ricauduro/access_control_with_python_and_esp01/assets/58055908/8ca84e1c-1a71-4caf-9948-ba82b54be8cc)


 
 We´ll use python face_recognition module for this project, so these are our imports:

 ```python
import face_recognition
import cv2
import numpy as np
import os
import glob
import re
```
 I faced a lot of issues to install face_recognition module with "pip install face_recognition". This was the way I managed to make it work:
 <pre>
	Step 1: Download and run Build Tools for Visual Studio 2022 https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019
	Step 2: Go to Individual Components and select C++ CMake tools for Windows and run through the install.
	Step 3: Proceed to build your python application (e.g. dlib)
	Step 4: Download dlib whl file, save it into your python folder, then  run "pip install dlib-19.22.99-cp39-cp39-win_amd64.whl"
	Step 5: pip install face_recognition
	 
	https://stackoverflow.com/questions/63648184/error-installing-packages-using-pip-you-must-use-visual-studio-to-build-a-pyth
	https://stackoverflow.com/questions/76629574/error-could-not-build-wheels-for-dlib-which-is-required-to-install-pyproject
 </pre>
 About OpenCV, some moduled are only present in opencv-contrib-python, so , if you already have OpenCV installed, it´s better to use an virtual-env and install it with 
<pre>
	 pip install opencv-contrib-python
</pre>

 We can split the code in 3 main parts -> capture, encode and validate.

 Let´s start with capture

```python

# Load the face and eye cascade classifiers
classificador = cv2.CascadeClassifier("haarcascade-frontalface-default.xml")
classificadorOlho = cv2.CascadeClassifier("haarcascade-eye.xml")

# Open the camera
camera = cv2.VideoCapture(0)

# Initialize variables
amostra = 1
numeroAmostra = 1
nome = input('Digite seu nome: ')
id = input('Digite seu identificador: ')
largura, altura = 220, 220
print("Capturando as faces...")

while True:
    # Read the camera frame
    conectado, imagem = camera.read()

    # Convert the frame to grayscale
    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    facesDetectadas = classificador.detectMultiScale(imagemCinza, scaleFactor=1.5, minSize=(150, 150))

    for (x, y, l, a) in facesDetectadas:
        # Draw a rectangle around the detected face
        cv2.rectangle(imagem, (x, y), (x + l, y + a), (0, 0, 255), 2)

        # Extract the region of interest (face)
        regiao = imagem[y:y + a, x:x + l]

        # Convert the region of interest to grayscale
        regiaoCinzaOlho = cv2.cvtColor(regiao, cv2.COLOR_BGR2GRAY)

        # Detect eyes within the region of interest
        olhosDetectatos = classificadorOlho.detectMultiScale(regiaoCinzaOlho)

        for (ox, oy, ol, oa) in olhosDetectatos:
            # Draw a rectangle around the detected eyes
            cv2.rectangle(regiao, (ox, oy), (ox + ol, oy + oa), (0, 255, 0), 2)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                #Capture if we got a good quality image
                if np.average(imagemCinza) > 110:

                    # Resize the captured face image to a fixed size
                    imagemFace = cv2.resize(imagemCinza[y:y + a, x:x + l], (largura, altura))

                    #Save the resized image
                    cv2.imwrite("fotos/{}.{}.{}.jpg".format(nome, str(id),str(amostra)), imagemFace)
                    print("[foto {} capturada com sucesso]".format(str(amostra)))
                    amostra += 1

    #Display the results
    cv2.imshow("Face", imagem)
    cv2.waitKey(1)

    #If enough pictures were collected, then stop capture
    if(amostra >= numeroAmostra +1):
        break
```
The classifiers used in this code are pre-trained XML files that contain information about specific visual features of faces and eyes. They are used to detect and locate regions of interest, such as faces and eyes, in an image.

The **haarcascade-frontalface-default.xml** classifier is trained to identify frontal facial features, such as the position of the eyes, nose, mouth, and facial contours. It is used to detect and delimit the regions where faces are located.

The **haarcascade-eye.xml** classifier is trained to identify eye features, such as shape and position. It is used to detect and delimit the regions where eyes are located within the previously detected faces.

These classifiers are used together to enable the detection of faces and eyes in the images captured by the camera in real-time. They provide an efficient way to perform this detection, as they have been trained on a large dataset of images containing faces and eyes.

I believe that the comments are enough to explain the rest of the code, wich is very simple

Here´s the encode part

```python
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
```

The code essentially loads images from the **'fotos/'** directory, encodes the faces in those images using the **face_recognition** library, and stores the face encodings along with their respective names in the faces_encodings and faces_names lists.

So, we need to assign to variables, **faces_encodings** and **faces_name**, that will be used to store the face encodings and corresponding names, respectively.

Then we´ll use **glob.glob()** to retrieve a list of file names with the extension '.jpg' in the **'fotos/'** directory, and store it in the **list_of_files** list.

We´re using **globals()['image_{}'.format(i)]** to dynamically create a variable name using the iteration number **i** and assign the person name using **face_recognition.load_image_file()** to that variable. For example, if i is 0, the variable name would be **image_0**, and so on.

Then with **face_recognition.face_encodings(globals()['image_{}'.format(i)])[0]** we´re encoding the faces captured and assign to use along with **globals()['image_{}'.format(i)]**, this way we can compare our encoded face and assign a name for it. 
The [0] index is used to get the first face encoding in case multiple faces are detected in the image.

Now we´ll see how to validate and display our results

```python
# Initialize empty lists to store face data
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# Create VideoCapture object to access the webcam
video_capture = cv2.VideoCapture(0)

while True:
    # Read the video frame
    ret, frame = video_capture.read()

    # Resize the frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    
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
                name = get_name(faces_names[best_match_index])
            
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
        cv2.imshow('Video', frame)
        
        # Hit 'q' on the keyboard to quit!
    k = cv2.waitKey(1)
    if k%256 == 27:
        print("Escape hit, closing...")
        break

video_capture.release()
cv2.destroyAllWindows()

```

Now we have to add the block which will comunicate with ESP-01 and control the door´s lock

```python
import urllib.request

root_url = "http://192.168.0.194"

def sendRequest(url):
	urllib.request.urlopen("{}/open".format(url)) 

if name != "Unknown":
	sendRequest(root_url)
```
It´s that simple... we´ll send a request to a url if the person in the video is know. 

When we reach ESP-01 set up I´ll explain how you can get root_url.


So I´ll start explaining how we can move the data to azure and then how we can set up the Arduino to control the lock.

## move data to blob storage
Now I´m going to explain how we can move the data we´re creating to a blob storage.

We´ll  need these values to our key.json to use as credentials to connect to our blob storage.

```Python
storage_account_key = credential['storage_account_key']
storage_account_name = credential['storage_account_name']
connection_string = credential['connection_string']
container_name = credential['container_name']
```
And we´ll need another function to create the blob

```Python
def uploadToBlobStorage(file_path,file_name)
   blob_service_client = BlobServiceClient.from_connection_string(connection_string)
   blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
   with open(file_path,'rb') as data:
      blob_client.upload_blob(data)
      print('Uploaded {}.'.format(file_name))
```

Inside our code´s loop we´ll need to create two variables that we´ll use to create a folder for each day in the blob storage and another one to create the file name

```Python
    while True:
        folder_date = datetime.now().date().strftime('%Y%m%d')
        filename_date = datetime.now().strftime('%Y%m%d_%H%M%S')
```

Then for each face we´ll append a timestamp value, the bottomSize a location, we´ll save the file locally and then call the function to send the file to our blob

```Python
  # Gerando o arquivo com as informações captadas pelo video
  faces = [{**face, 'timeStamp': str(datetime.now()), 'bottomSize': str(bottom), 'location': 'Casa'} for face in faces]
  json_string = json.dumps(faces, separators=(',', ':'))

  with open('output\mydata-{}.json'.format(filename_date), 'w') as f:
            json.dump(json.JSONDecoder().decode(json_string), f)
            
  # Calling a function to perform upload
  uploadToBlobStorage('output\mydata-{}.json'.format(filename_date),'{}/mydata-{}.json'.format(folder_date,filename_date))
```
This is how the data should be in our storage

![image](https://github.com/ricauduro/video_face_recognition/assets/58055908/b84120f9-c0e0-4894-b0fa-7eb3fbd38ab3)

![image](https://github.com/ricauduro/video_face_recognition/assets/58055908/3eea1219-c3c1-4d66-a8ad-dd09db8376fd)

## set up the ESP-01

Work with Arduino can be very gratifying, when our first led start blynking it´s awesome. I found this link that is explaining how to set the ESP-01 step by step the same way I did it. 

https://www.blogdarobotica.com/2020/09/18/programando-o-esp01-utilizando-o-adaptador-usb-serial-para-esp8266-esp-01/

The ESP-01 code is very simple, it works like a web server, that´s expecting a call, and depending on the value received, it will send or not an event to our door lock.

first we start with the imports and the definitions

```C++
#include <ESP8266WiFi.h>

#ifndef STASSID
#define STASSID "*****"
#define STAPSK "******"
#endif

const char* ssid = STASSID;
const char* password = STAPSK;
```

with this we start the server
```C++
WiFiServer server(80);
```

Here we´ll set the gpio0 and 2 as outputs and set the initial state as LOW,
```C++
void setup() {
  delay(5000);
  pinMode(0, OUTPUT);
  pinMode(2, OUTPUT);
  digitalWrite(0, LOW);
  digitalWrite(2, LOW);
  // Serial.begin(9600);
  // Serial.print("Connecting to ");
  // Serial.println(ssid);
```
Then we can set the wifi mode as station and begin the connection
```C++
  WiFi.mode(WIFI_STA);

  WiFi.begin(ssid,password);

  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    // Serial.print(".");
  }

  // Serial.println("ESP-01 is connected to the ssid");
  // Serial.println(WiFi.localIP());
  server.begin();
  delay(1000);
}
```
On the loop we expecting to receive an request like this 'http://192.168.0.1/open' to open the lock. So we´ll parse our result to check if we have the 'open' at the end, and if so, we´ll change the value of the pins to HIGH, openning the lock

```C++
void loop() {
  WiFiClient client;
  client = server.available();

  if (client == 1){
    String request = client.readStringUntil('\n');
    client.flush();
    // Serial.println(request);

    if (request.indexOf("open") != -1){
      digitalWrite(0, HIGH);
      delay(5000);
      digitalWrite(0, LOW);
      delay(1000);
      digitalWrite(2, HIGH);
      delay(5000);
      digitalWrite(2, LOW);
      // Serial.println("Openning door");
    }
    // Serial.print("Client Disconnected");
    // Serial.println(" ");
  }
}

```
After seting up the ESP, you can upload this sketch to the ESP-01, but with a little modification. 

I leave some lines commented, because we won´t need the serial output while running in production, but we´ll need it to get the ESP-01 IP to stabilish the communication between the ESP and our Python code. So before upload the first time, uncomment the lines, plug the ESP in the USB port, open the serial monitor and get the ESP-01 IP

![image](https://github.com/ricauduro/access_control_face_reco_and_arduino/assets/58055908/8ec8edf7-1b2a-493a-99cb-92b4435a0be9)

Th Python code that we need to add to the face_recogniton code is very simple. Just send a request to the IP we got from the ESP-01, with '/open' at the end.

```python
import urllib.request

root_url = "http://192.168.0.174"


def sendRequest(url):
    try:
        urllib.request.urlopen("{}/open".format(root_url))
    except Exception as e:
        if e == "Remote end closed connection without response":
            pass
```

The sendRequest we can insert into a IF conditon, to guarantee that the door will open when we get real close to it, and only if it recognize our faces.

```python
        if (right > 480) and (name != "Unknown"):
            sendRequest(root_url)
```
