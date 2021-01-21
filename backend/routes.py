from flask import Flask, jsonify, request, json
import glob
import re
import base64
from io import BytesIO,StringIO
from PIL import Image, ImageDraw, ImageFont
from main import app,face_client,db
from forms import *
from database import *
from azure.cognitiveservices.vision.face.models import APIErrorException
import sys
sys.path.append('.')
from azure.utils import *
from azure.register import *

import random


@app.route("/")

def homepage():
    return "Homepage for sanity"

@app.route("/add")
def add_person():
    rand = random.randint(0,1000000)
    customer1=Customer(id=rand,first_name='Temp',last_name='Yu',phone_number='6479365120',card_number='1234123412341234',cvv='123',expire_date='0922')
    db.session.add_all([customer1])
    db.session.commit()
    return "ran :" + str(rand)

@app.route("/list")
def list_person():
    show_compare = []
    cust2 = Customer.query.filter().all()
    for item in cust2:
        show_compare.append(item.id)
    cust1 = Customer.query.count()
    print(cust1)
    return 'list' + str(cust1) + str(show_compare)

@app.route("/testing", methods=['POST'])
def testing():
    data = json.loads(request.data, strict=False)
    print (data)
    return data

@app.route("/register/info", methods=['POST'])
def post_info():
    data = json.loads(request.data, strict=False)
    print (data)
    print (type(data))

    if (check_form_not_none(data)): 
        person_name_at_bank_acc = data['first_name'] + "_" + data['last_name'] + "@" + data['card_number']
        print (person_name_at_bank_acc)
        #MM_todo - check person whether exist in data base instead of AI model
        if (check_person_exist(face_client,person_name_at_bank_acc)):
            print ("user exist")
            return jsonify({'message': 'user already exist','name@bank':person_name_at_bank_acc}),200
        else:
            person_id = create_person(face_client,person_name_at_bank_acc)
            if person_id is None:
                return jsonify({'message': 'AI model can not create a person'}),200
            print (person_id)
            #because 2nd time called this, we dont have the id, we need to store it frist 

            customer_info = Customer(
                    id=person_id,
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    phone_number=data.get('phone_number'),
                    card_number=data.get('card_number'),
                    cvv=data.get('cvv'),
                    expire_date=data.get('expire_date')
                    #MM_todo - register payment cnt intialize t0 0

                    )
            db.session.add_all([customer_info])
            db.session.commit()

            return jsonify({'message': 'ok, the text info is added into db', 'person_id': person_id}),200

    else:
        print ("form contains None")
        return jsonify({'message': 'require more info'}),200
    
@app.route("/register/photo/test", methods=['POST'])
def post_photo_test():
    data = json.loads(request.data, strict=False)
    #print (data)
    print (type(data))

    #im = Image.new("RGB", (300, 30), (220, 180, 180))
    ##im.format'JPEG'
    #dr = ImageDraw.Draw(im)
    #font = ImageFont.truetype(os.path.join("fonts", "msyh.ttf"), 16)
    #text =time.strftime("%m/%d  %H:%M:%S") +u"这是一段测试文本。"
    #dr.text((10, 5), text, font=font, fill="#000000")

    return jsonify({'message': 'reponse'}),200

@app.route("/register/photo/<person_id>", methods=['POST'])
def post_photo(person_id = None):
    data = json.loads(request.data, strict=False)
    #print (data.get('photo'))
    print (type(data))
    if (person_id == None or data.get('photo') == None or person_id == "undefined"):
        return jsonify({'message': 'person_id not returned to the backend neither the photo'}),200
    else:
        print ("got person id" + person_id)
        [image_type,image_content] = re.split(",",data['photo'])
        print (image_type)
        if (image_type != "data:image/jpeg;base64"):
            return jsonify({'message': 'the image is not a jpeg type'}),200
        #print (type(image_content))
        #print (type(base64.b64decode(image_content)))
        nparr = np.fromstring(base64.b64decode(image_content), np.uint8)
        #print (type(nparr))
        #img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        #print (type(img))
        #cv2.imshow('img',img)
        #cv2.imwrite(constant.REG_PHOTO_FOLDER+'{person_id_name}.jpg'.format(person_id_name = person_id), img) 
        file_p = open(constant.REG_PHOTO_FOLDER+'{person_id_name}.jpg'.format(person_id_name = person_id), 'r+b')
        #when we add face, we can also add the name@bank as the argument
        #PersistedFace_id = face_client.person_group_person.add_face_from_stream(constant.PERSON_GROUP_ID, person_id, image_content, name="ma@123")
        try:
            response_info = face_client.person_group_person.add_face_from_stream(constant.PERSON_GROUP_ID, person_id, file_p)#, name="ma@123")
            print (response_info)
        except APIErrorException:
            print ("no face is detected")
            return jsonify({'message': "no face is detected"}),200
        train_person_group(face_client)
        #try:
        #    train_person_group(face_client)
        #except:
        #    print ("training not succeed")
        #    return jsonify({'message': "training not succeed"}),200
        
        if (constant.KEEP_CACHE_PHOTO == 0 ):
            try:
                os.remove(constant.REG_PHOTO_FOLDER+'{person_id_name}.jpg'.format(person_id_name = person_id))
                print ("photo is removed")
            except PermissionError:
                print ("delete photo permission denied")
            
        return jsonify({'message': 'photo is added'}),200

    return jsonify({'message': 'reponse'}),200


def check_form_not_none(data):
    if (
        data.get('first_name') is not None and
        data.get('last_name') is not None and
        data.get('phone_number') is not None and
        data.get('card_number') is not None and
        data.get('cvv') is not None and
        data.get('expire_date') is not None and
        True #dummy value to keep format
        ): 
        return True
    else:
        return False

@app.route("/payment", methods=['POST'])
def payment_photo():
    data = json.loads(request.data, strict=False)
    #print (data.get('photo'))
    print (type(data))
    if (data.get('photo') == None):
        return jsonify({'message': 'the photo not returned to the backend '}),200
    else:
        [image_type,image_content] = re.split(",",data['photo'])
        print (image_type)
        if (image_type != "data:image/jpeg;base64"):
           return jsonify({'message': 'the image is not a jpeg type'}),200
        nparr = np.fromstring(base64.b64decode(image_content), np.uint8)
        #img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        #cv2.imwrite(constant.PAY_PHOTO_FOLDER+'{person_id_name}.jpg'.format(person_id_name = "temp"), img) 
        file_p = open(constant.PAY_PHOTO_FOLDER+'{person_id_name}.jpg'.format(person_id_name = "temp"), 'r+b')
        # Detect faces
        face_ids = []
        try:
            faces =face_client.face.detect_with_stream(file_p,recognition_model=constant.RECOGNITION_MODEL)
        except APIErrorException:
           print ("detect failure")
           return jsonify({'message': "detect failure"}),200

        for face in faces:
            face_ids.append(face.face_id)
            print('face ID in faces {}.\n'.format(face.face_id)) 
        if (len(face_ids) == 0):
            print ("No face detected in this verify image")
            return jsonify({'message': "No face detected in this verify image"}),200
        elif (len(faces) > 1):
            print ("More than 1 faces detected in this verify image. Please retake the photo")
            return jsonify({'message': "More than 1 faces detected in this verify image. Please retake the photo"}),200
        else:
            try:
                results = face_client.face.identify(face_ids,constant.PERSON_GROUP_ID)
            except APIErrorException:
                print ("identify failure, possibly person group not train")
                return jsonify({'message': "identify failure, possibly person group not train"}),200

            if not results:
                print('No person in AI database matched with this verification')
                return jsonify({'message': "No person in AI database matched with this verification"}),200
            else:
                #should be only 1 face
                first_face = results[0]
                first_candidates = first_face.candidates[0]
                print ("test")
                print (first_face)
                print (type(first_face))
                print (first_candidates)
                print (type(first_candidates))
                if (len(first_face.candidates) == 0):
                    print('No candidates person in this database matched with this verification')
                    return jsonify({'message': "No candidates person in this database matched with this verification"}),200
                else :
                    first_person_id = first_candidates.person_id
                    first_person_confidence = first_candidates.confidence
                    first_person_name = face_client.person_group_person.get(constant.PERSON_GROUP_ID,first_candidates.person_id).name
                    print('Person name {} with person_id {} matched with this cerification with a confidence of {}.'.format(first_person_name, first_person_id, first_person_confidence)) 
                        
                    #MM_todo query database, return user all info
                    #MM_todo set confidence threholds, check payment_cnt
                    return jsonify({'message': 'succeed', 'person_id' : first_person_id, 'require_phone_number' : 0, 'confidence' : first_person_confidence}),200
    return jsonify({'message': 'reponse'}),200
