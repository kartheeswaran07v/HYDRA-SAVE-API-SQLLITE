from django.shortcuts import render
from django.utils import timezone
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializer import PlantSerializer, UserSerializer, tsPlantSerializer, tsDataSerializer
from django.core.exceptions import ObjectDoesNotExist
import random
from .domain import getDomain, checkWebmail, checkCompetitor
from django.core.mail import send_mail
from django.http import HttpResponse
import copy

API_KEY = "API_KEY"
 
# Create your views here.
# View all User records: endpoint: http://127.0.0.1:8000/
@api_view(['GET'])
def getData(request):
    food = userMaster.objects.all()
    serializer = UserSerializer(food, many=True)
    return Response(serializer.data)


# Check type of user: endpoint: http://127.0.0.1:8000/user/check/
@api_view(['POST'])
def check(request):
    data = request.data
    username = data['username']
    api_key = data['api_key']
    message = ''
    # Check API Key
    if api_key == API_KEY:
        
    # Check if user exists
        try:
            profile = userMaster.objects.get(emailID=username)
            isexist = True
        except ObjectDoesNotExist:
            isexist = False

        # Check if domain is Webmail
        if checkWebmail(username):
            message = "You have entered a Webmail, which will take further processing from the Sales side to gain access to the application. Do you want to continue"


        # Check if domain is Competitor
        if checkCompetitor(username):
            message = "Please contact Nitto-Hydranautics Regional Sales"

        # Check if domain is Nitto
        if getDomain(username) == 'nitto':
            isNitto = True
            message = "Please contact system administrator"
        else:
            isNitto = False

        # Response JSON Structure
        json_={
            "status": "OK",
            "status_code": 200,
            "isExisting": isexist,
            "isNitto": isNitto,
            "isCompetitor": checkCompetitor(username),
            "isWebmail": checkWebmail(username),
            "errorMessage": message
        }

    else:
        json_ = {
            "status": "Incorrect API key",
            "status_code": 401,
            "errorMessage": "You've provided incorrect API Key. Kindly check again!"
        }
    return Response(json_)


# Check Password: endpoint: http://127.0.0.1:8000/user/checkPW/
@api_view(['POST'])
def checkPassword(request):
    # Data as input example
    # {"username": "USERNAME", "password": "PASSWORD"}
    data=request.data
    username = data['username']
    user = userMaster.objects.get(emailID=username)
    if user.password == data['password']:
        isCorrectPW = True
    else:
        isCorrectPW = False
    json_ = {
        "status": "OK",
        "status_code": 200,
        "isCorrectPW": isCorrectPW,
        "userId": user.id
    }

    return Response(json_)


# Send OTP: endpoint: http://127.0.0.1:8000/user/register-otp/
@api_view(['POST'])
def sendOTP(request):
    # Data as input example
    # {"username": "USERNAME"}
    data = request.data
    # Code block to send OTP to registered EMAIL ID
    # Generate Random INT
    random_decimal = random.random()
    random_int = round(random_decimal*10**6)

    
    # send_mail(
    #     "Subject here",
    #     f"Here is the message. {random_int}",
    #     "kartheeswaran@07v@gmail.com",
    #     ["kartheeswaran@1707@gmail.com"],
    #     fail_silently=False,
    # )
    # Store OTP in DB

    OTP.objects.create(username=data['username'], otp=random_int, time=timezone.now())

    # End Code block

    json_ = {
        "status": "OK",
        "status_code": 200,
        "message": f"OTP Sent to Email ID: {data['username']}"
    }

    return Response(json_)


# Check OTP: endpoint: http://127.0.0.1:8000/user/check-otp/
@api_view(['POST'])
def checkOTP(request):
    # Data as input example
    # {"username": "USERNAME", "OTP": "OTP"}
    data = request.data
    otp_data = OTP.objects.filter(username=data['username']).last()

    if data['OTP'] == otp_data.otp:
        json_ = {
            "status": "OK",
            "status_code": 200,
            "message": "OTP is correct, proceed with registration"
        }
    else:
        json_ = {
            "status": "Failure",
            "status_code": 400,
            "message": "OTP is incorrect"
        }
    
    return Response(json_)


# Registration POST Request: http://127.0.0.1:8000/user/register/
@api_view(['POST'])
def registration(request):
    # Data as input example
    # {"username":"USERNAME","password":"PASSWORD","name":"NAME","address":"ADDRESS","city":"CITY","region":"REGION","country":"COUNTRY","zipcode":100000,"mobile":"+91-XXXXXXXXXX","industry":"INDUSTRY","company_name":"COMPANY_NAME","designation":"DESIGNATION"}
    data_ = request.data

    # Check if record already exists
    try:
        user = userMaster.objects.get(emailID=data_['emailID'])

        json_ = {
            "status": "Failed",
            "status_code": 400,
            "status_message": "Record Already exists or Record is under approval process",
            "username": data_['emailID']
        }

    # if new record
    except ObjectDoesNotExist:
        # To save data in database
        serializer = UserSerializer(data=request.data)

        # Get relational data
        data = request.data
        region_string = data.pop('region')
        industry_string = data.pop('industry')
        region_ = regionMaster.objects.get(name=region_string)
        industry_ = industryMaster.objects.get(name=industry_string)

        if serializer.is_valid():
            serializer.save(regionID=region_, industryId=industry_)
        else:
            print('data not valid')

        json_ = {
            "status": "OK",
            "status_code": 200,
            "status_message": "Record created in Database",
            "username": data_['emailID'],
            "isWebmail": checkWebmail(data_['emailID'])
        }


    
    return Response(json_)


# Reset Password POST Request: http://127.0.0.1:8000/user/reset-pw/
@api_view(['POST'])
def resetPassword(request):
    user_object = userMaster.objects.get(emailID=request.data['username'])
    user_object.password = request.data['newPassword']
    user_object.save()
    json_ = {
            "status": "OK",
            "status_code": 200,
            "message": "Password Reset Successfully"
        }
    return Response(json_)

 
# View all Plants: http://127.0.0.1:8000/plant/allPlants/
@api_view(['GET'])
def allPlants(request):
    plants = plantMaster.objects.filter(createdById=userMaster.objects.get(id=1)).all()
    serializer = PlantSerializer(plants, many=True)
    return Response(serializer.data)


# View Add Plants: http://127.0.0.1:8000/plant/addPlant/
@api_view(['POST'])
def addPlant(request):
    validated_data = request.data
    validated_data2 = copy.deepcopy(validated_data)
    trains_data = validated_data.pop('trains')
    trains_data2 = validated_data2.pop('trains')
    plantUniqueId_ = request.data['plantUniqueId']
    plant_element = plantMaster.objects.filter(plantUniqueId=plantUniqueId_).all()

    # check for unique Stages
    stage_count = 0
    for train_data in trains_data:
        passes_data = train_data.pop('passes')
        for pass_data in passes_data:
            stages_data = pass_data.pop('stages')
            for stage_data in stages_data:
                elements_data = stage_data.pop('elements')
                stage_element = stageMaster.objects.filter(stageUniqueId=stage_data['stageUniqueId']).all()
                if len(stage_element) > 0:
                    stage_count += 1
    
    # If data is unique
    if len(plant_element) == 0 and stage_count == 0:
        plant = plantMaster.objects.create(createdById=userMaster.objects.get(id=1), **validated_data2)
        for train_data in trains_data2:
            print(train_data)
            passes_data = train_data.pop('passes')
            train = trainMaster.objects.create(plantId=plant, **train_data)
            for pass_data in passes_data:
                stages_data = pass_data.pop('stages')
                pass_ = passMaster.objects.create(trainId=train, **pass_data)
                for stage_data in stages_data:
                    elements_data = stage_data.pop('elements')
                    stage_ = stageMaster.objects.create(passId=pass_, **stage_data)
                    for element_data in elements_data:
                        elementMaster.objects.create(stageId=stage_, **element_data)

        json_ = {
            "status": "OK",
            "status_code": 200,
            "message": "Data added successfully"
        }
    elif len(plant_element) > 0:
        json_ = {
            "status": "Failure",
            "status_code": 500,
            "message": "Unique Id Constraint not satisified - Plant"
        }
    else:
        json_ = {
            "status": "Failure",
            "status_code": 500,
            "message": "Unique Id Constraint not satisified - Stage"
        }

    return Response(json_)

    
    
        

 
# View all Plants: http://127.0.0.1:8000/plant/tsData/
@api_view(['POST'])
def tsData(request):
    # plants = plantMaster.objects.filter(createdById=userMaster.objects.get(id=1)).all()
    # serializer = tsPlantSerializer(plants, many=True)
    stage_element = stageMaster.objects.filter(stageUniqueId=request.data['stageId']).first()
    tsDatas = timeSeriesData.objects.filter(stageId=stage_element.id).all()
    serializer = tsDataSerializer(tsDatas, many=True)
    return Response(serializer.data)


# View all Plants: http://127.0.0.1:8000/plant/addTsData/
@api_view(['POST'])
def addTsData(request):
    stage_element = stageMaster.objects.filter(stageUniqueId=request.data['stageId']).first()
    ts_data = request.data['tsData']
    if stage_element:
        for data in ts_data:
            timeSeriesData.objects.create(stageId=stage_element, **data)
        json_ = {
            "status": "OK",
            "status_code": 200,
            "message": f"{len(ts_data)} number of data added to stage element: {stage_element.stageUniqueId}"
        }
    else:
        json_ = {
            "status": "Failure",
            "status_code": 500,
            "message": f"No Such Stage exists with stageUniqueId: {request.data['stageId']}"
        }

    return Response(json_)