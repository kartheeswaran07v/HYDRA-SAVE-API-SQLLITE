from django.shortcuts import render
from django.utils import timezone
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializer import *
from django.core.exceptions import ObjectDoesNotExist
import random
from .domain import getDomain, checkWebmail, checkCompetitor, linear_graph
from django.core.mail import send_mail
from django.http import HttpResponse
import copy
import csv
from datetime import datetime

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
        "username": user.id, 
        "email": user.emailID,
        "firstName": user.firstName,
        "lastName": ""
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


# View all Plants: http://127.0.0.1:8000/api/plant/dashPlants
@api_view(['GET'])
def dashPlants(request):
    plants = plantMaster.objects.filter(createdById=userMaster.objects.get(id=1)).all()
    serializer = dashPlantSerializer(plants, many=True)
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
    pass_count = 0
    train_count = 0
    for train_data in trains_data:
        passes_data = train_data.pop('passes')
        train_element = trainMaster.objects.filter(trainUniqueId=train_data['trainUniqueId']).all()
        if len(train_element) > 0:
            train_count += 1
        for pass_data in passes_data:
            stages_data = pass_data.pop('stages')
            pass_element = passMaster.objects.filter(passUniqueId=pass_data['passUniqueId']).all()
            if len(pass_element) > 0:
                pass_count += 1
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
    param = request.data['param']
    stage_element = stageMaster.objects.filter(stageUniqueId=request.data['stageId']).first()
    tsDatas = timeSeriesData.objects.filter(stageId=stage_element.id).all()
    data_trim = tsDatas[:100]
    json_data_sspn = {param: [],
                        'linear': [],
                        'timeseries': []}
    for i in data_trim:
        json_data_sspn[param].append(round(i.__dict__[param], 3))
        json_data_sspn['timeseries'].append(str(i.date)[:10])
    
    json_data_sspn['linear'] = linear_graph(json_data_sspn[param])[0]
    # serializer = tsDataSerializer(tsDatas, many=True)
    return Response(json_data_sspn)


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



def get_param_details(param, param_object):
    percent_param = ((float(param)-float(param_object.reference))/param)*100
    if float(param_object.low) < percent_param <= float(param_object.high):
        status = 'normal'
    elif percent_param <= float(param_object.highhigh):
        status = 'high'
    elif percent_param > float(param_object.highhigh):
        status = 'highhigh'
    elif float(param_object.lowlow) <= percent_param < float(param_object.low):
        status = 'low'
    elif float(param_object.lowlow) > percent_param:
        status = 'lowlow'
    
    return {'percent_value': percent_param, 'status': status}


# View all Plants: http://127.0.0.1:8000/plant/setPoint
@api_view(['POST'])
def setPoint(request):
    plant_element = plantMaster.objects.get(plantUniqueId=request.data['plantUniqueId'])
    train_element = trainMaster.objects.get(plantId=plant_element, trainName=request.data['trainName'])
    stage_elements = stageMaster.objects.filter(passId__trainId=train_element).all()
    train_data = []
    for stage in stage_elements:
        set_point_nsp = setPoints.objects.filter(stageId=stage, parameter='NSP').first()
        set_point_npf = setPoints.objects.filter(stageId=stage, parameter='NPF').first()
        set_point_ndp = setPoints.objects.filter(stageId=stage, parameter='NDP').first()
        ts_data_latest = timeSeriesData.objects.filter(stageId=stage).last()
        nsp, npf, ndp = ts_data_latest.normSaltPassage, ts_data_latest.normPermFlow, ts_data_latest.normDP
        stage_set_dict = {
            "stageUniqueId": stage.stageUniqueId,
            "data": {
                "NDP": get_param_details(ndp, set_point_ndp),
                "NSP": get_param_details(nsp, set_point_nsp),
                "NPF": get_param_details(npf, set_point_npf)
            }
        }
        train_data.append(stage_set_dict)

    json_ = {
        "status": "OK",
        "status_code": 200,
        "data": train_data
    }
    return Response(json_)


# View all Plants: http://127.0.0.1:8000/plant/dropdown
@api_view(['POST'])
def dropdown(request):
    plant_elements = plantMaster.objects.filter(createdById=userMaster.objects.get(emailID=request.data['username'])).all()
    plant_list = []
    for i in plant_elements:
        plant_dict = {i.plantUniqueId: i.plantName}
        plant_list.append(plant_dict)
        # train_elements = trainMaster.objects.filter(plantId=i).all()
        # train_list.append(train_elements)
    train_dict = {}
    for i in plant_elements:
        train_elements = trainMaster.objects.filter(plantId=i).all()
        train_list = []
        for train in train_elements:
            train_dict_ = {train.trainUniqueId: train.trainName}
            train_list.append(train_dict_)
        
        train_dict[i.plantUniqueId] = train_list

    pass_dict = {}
    for i in plant_elements:
        train_elements = trainMaster.objects.filter(plantId=i).all()
        for train in train_elements:
            pass_elements = passMaster.objects.filter(trainId=train).all()
            pass_list = []
            for pass_ in pass_elements:
                pass_dict_ = {pass_.passUniqueId: pass_.passName}
                pass_list.append(pass_dict_)
            
            pass_dict[train.trainUniqueId] = pass_list
    
    stage_dict = {}
    for i in plant_elements:
        train_elements = trainMaster.objects.filter(plantId=i).all()
        for train in train_elements:
            pass_elements = passMaster.objects.filter(trainId=train).all()
            for pass_ in pass_elements:
                stage_elements = stageMaster.objects.filter(passId=pass_).all()
                stage_list = []
                for stage in stage_elements:
                    stage_dict_ = {stage.stageUniqueId: stage.stageNumber}
                    stage_list.append(stage_dict_)
                stage_dict[pass_.passUniqueId] = stage_list 


    response_dict = {
        "plants": plant_list,
        "trains": train_dict,
        "passes": pass_dict,
        "stages": stage_dict
    }

    return Response(response_dict)


# def addData():
    filename = 'C:\\Users\\FCC\\Documents\\NITTO\\NITTO Code\\HYDRA-SAVE API SQLLITE\\hydrasaveAPI\\norm_data_clean_2.csv'
    fields = []
    rows = []

    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields_ = next(csvreader)
        for row in csvreader:
            rows.append(row)



    print(fields_)
    # print(rows[:6])

    for row in rows:
        e = row[1][:10]
        d = datetime.strptime(e, '%d-%m-%Y')
        timeSeriesData.objects.create(
            date=d,
            time=datetime.now(),
            turbidity=row[3],
            sdi=row[4],
            pH=row[5],
            temperature=row[6],
            feedConc=row[7],
            permConc=row[8],
            rejectConc=0,
            feedFlow=row[9],
            permFlow=row[10],
            rejectFlow=0,
            feedPres=row[11],
            permPres=row[12],
            rejectPres=row[13],
            normSaltPassage=row[14],
            normPermFlow=row[15],
            normDP=row[16],
            stageId=stageMaster.objects.get(stageUniqueId="3456")
        )

# # View all Plants: http://127.0.0.1:8000/plant/addData
# @api_view(['POST'])
# def addLargeData(request):
#     addData()
#     return Response({"message": "success"})

# View all Plants: http://127.0.0.1:8000/api/plant/get/setPoints
@api_view(['POST'])
def getSetPoints(request):
    set_points = setPoints.objects.filter(stageId=stageMaster.objects.get(stageUniqueId=request.data['stageId'])).all()
    serializer = setPointsSerializer(set_points, many=True)
    return Response(serializer.data)


# View all Plants: http://127.0.0.1:8000/api/plant/addSetPoints
@api_view(['POST'])
def addSetPoints(request):
    stage_element = stageMaster.objects.get(stageUniqueId=request.data['stageId'])
    for data_ in request.data['data']:
        print(data_)
        serializer = addSetPointsSerializer(data=data_)
        if serializer.is_valid():
            serializer.save(stageId=stage_element)
        else:
            print('data invalid')
    
    return Response({"message": "success"})