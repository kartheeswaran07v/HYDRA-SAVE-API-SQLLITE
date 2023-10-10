from django.shortcuts import render
from django.utils import timezone
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializer import *
from django.core.exceptions import ObjectDoesNotExist
import random
from .domain import *
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
            "errorMessage": "",
            "message": "Validation Error"
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
        code_ = 200
    else:
        isCorrectPW = False
        code_ = 401
    json_ = {
        "status": "OK",
        "status_code": code_,
        "isCorrectPW": isCorrectPW,
        "username": user.id, 
        "email": user.emailID,
        "firstName": user.firstName,
        "lastName": ""
    }
    response = Response(json_)

    if isCorrectPW:
        random_decimal = random.random()
        random_int = round(random_decimal*10**6)
        user.cookies = random_int
        user.save()
        # response = Response({"message": "success"})
        response.set_cookie(key='token', value=random_int)

    return response


# Logout: endpoitn: http://127.0.0.1:8000/api/user/logout
def logOut(request):
    emailID = request.data['emailID']
    user_ = userMaster.objects.get(emailID=emailID)
    user_.cookies = round((random.random()*10**6))
    user_.save()
    return Response({'message': "logout success", "status": "OK", "status_code": 200})

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
            json_ = {
                "status": "OK",
                "status_code": 200,
                "status_message": "Record created in Database",
                "username": data_['emailID'],
                "isWebmail": checkWebmail(data_['emailID'])
            }
        else:
            print('data not valid')

            json_ = {
                "status": "OK",
                "status_code": 400,
                "status_message": "Error in data provided",
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
    # param = request.data['param']
    stage_element = stageMaster.objects.filter(stageUniqueId=request.data['stageId']).first()
    # tsDatas = timeSeriesData.objects.filter(stageId=stage_element.id).all()
    # data_trim = tsDatas[:100]
    data_trim = ts_data_date(request.data['from'], request.data['to'], stageId=stage_element)
    # json_data_sspn = {param: [],
    #                     'linear': [],
    #                     'timeseries': []}

    json_graph = {
        "data": [
            {
                "nsp": [],
                "linear": [],
                "timeseries": []
            },
            {
                "npf":[],
                "linear":[],
                "timeseries": []
            },
            {
                "ndp": [],
                "linear":[],
                "timeseries": []
                
            }
        ],
        "statisticalData": []
    }

    for i in data_trim:
        # json_data_sspn[param].append(round(i.__dict__[param], 3))
        # json_data_sspn['timeseries'].append(str(i.date)[:10])
        json_graph['data'][0]['nsp'].append(round(i.normSaltPassage, 3))
        json_graph['data'][1]['npf'].append(round(i.normPermFlow, 3))
        json_graph['data'][2]['ndp'].append(round(i.normDP, 3))
        
        json_graph['data'][0]['timeseries'].append(str(i.date)[:10])
        json_graph['data'][1]['timeseries'].append(str(i.date)[:10])
        json_graph['data'][2]['timeseries'].append(str(i.date)[:10])
    
    # json_data_sspn['linear'] = linear_graph(json_data_sspn[param])[0]
    try:
        json_graph['data'][0]['linear'] = linear_graph(json_graph['data'][0]['nsp'])[0]
        json_graph['data'][1]['linear'] = linear_graph(json_graph['data'][1]['npf'])[0]
        json_graph['data'][2]['linear'] = linear_graph(json_graph['data'][2]['ndp'])[0]
        # serializer = tsDataSerializer(tsDatas, many=True)

        # Statistical Data
        json_graph['statisticalData'].append(statisticalData(json_graph['data'][0]['nsp']))
        json_graph['statisticalData'].append(statisticalData(json_graph['data'][1]['npf']))
        json_graph['statisticalData'].append(statisticalData(json_graph['data'][2]['ndp']))
    except ZeroDivisionError:
        pass

    return Response(json_graph)


# View all Plants: http://127.0.0.1:8000/plant/tsDataTable
@api_view(['POST'])
def tsDataTable(request):
    # cookie = request.COOKIES['token']
    # if cookie == userMaster.objects.get(emailID=request.data['emailID']).cookies:
    stage_element = stageMaster.objects.filter(stageUniqueId=request.data['stageId']).first()
    # tsDatas = timeSeriesData.objects.filter(stageId=stage_element.id).all()
    # data_trim = tsDatas[:10]

    # json_table = {
    #     "timeseries": [],
    #     "nsp": [],
    #     "npf": [],
    #     "ndp": []
    # }

    # for i in data_trim:
    #     json_table['nsp'].append(round(i.normSaltPassage, 3))
    #     json_table['npf'].append(round(i.normPermFlow, 3))
    #     json_table['ndp'].append(round(i.normDP, 3))
    #     json_table['timeseries'].append(str(i.date)[:10])
    
    data_trim = ts_data_date(request.data['from'], request.data['to'], stageId=stage_element)
    # print(a)   
    json_table = {
        "data": [],
        "columns": [
            {
                "dataField": "timeseries",
                "text": "Time Series"
            },
            {
                "dataField": "nsp",
                "text": "NSP"
            },
            {
                "dataField": "ndp",
                "text": "NDP"
            },
            {
                "dataField": "npf",
                "text": "NPF"
            }
        ]
    }

    for i in data_trim:
        single_data = {
            "timeseries": str(i.date)[:10],
            "nsp": round(i.normSaltPassage, 3),
            "ndp": round(i.normDP, 3),
            "npf": round(i.normPermFlow, 3)
        }
        json_table['data'].append(single_data)


    return Response(json_table)
    # else:
    #     return Response({'status_code': 403})
# View all Plants: http://127.0.0.1:8000/plant/addTsData/
@api_view(['POST'])
def addTsData(request):
    stage_element = stageMaster.objects.filter(stageUniqueId=request.data['stageId']).first()
    ts_data = request.data['tsData']
    if stage_element:
        for data in ts_data:
            data['normSaltPassage'],data['normPermFlow'],data['normDP'], data['rejectConc'], data['feedFlow']   = getNormData(**data)['nsp'], getNormData(**data)['npf'], getNormData(**data)['ndp'], None, None
            timeSeriesData.objects.update_or_create(stageId=stage_element, date=data['date'], defaults=data)
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






# # View all Plants: http://127.0.0.1:8000/plant/setPoint
# @api_view(['POST'])
# def setPoint(request):
#     plant_element = plantMaster.objects.get(plantUniqueId=request.data['plantUniqueId'])
#     train_element = trainMaster.objects.get(plantId=plant_element, trainUniqueId=request.data['trainName'])
#     stage_elements = stageMaster.objects.filter(passId__trainId=train_element).all()
#     train_data = []
#     for stage in stage_elements:
#         set_point_nsp = setPoints.objects.filter(stageId=stage, parameter='NSP').first()
#         set_point_npf = setPoints.objects.filter(stageId=stage, parameter='NPF').first()
#         set_point_ndp = setPoints.objects.filter(stageId=stage, parameter='NDP').first()
#         ts_data_latest = timeSeriesData.objects.filter(stageId=stage).last()
#         nsp, npf, ndp = ts_data_latest.normSaltPassage, ts_data_latest.normPermFlow, ts_data_latest.normDP
#         stage_set_dict = {
#             "stageUniqueId": stage.stageUniqueId,
#             "data": {
#                 "NDP": get_param_details(ndp, set_point_ndp),
#                 "NSP": get_param_details(nsp, set_point_nsp),
#                 "NPF": get_param_details(npf, set_point_npf)
#             },
#             "data2": [["NDP", get_param_details(ndp, set_point_ndp)['percent_value']], ["NSP", get_param_details(nsp, set_point_nsp)['percent_value']], ["NPF", get_param_details(npf, set_point_npf)['percent_value']]]
#         }
#         train_data.append(stage_set_dict)

#     json_ = {
#         "status": "OK",
#         "status_code": 200,
#         "data": train_data
#     }
#     return Response(json_)


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
#     filename = 'C:\\Users\\FCC\\Documents\\NITTO\\NITTO Code\\HYDRA-SAVE API SQLLITE\\hydrasaveAPI\\stage_norm_data_u2.csv'
#     fields = []
#     rows = []

#     with open(filename, 'r') as csvfile:
#         csvreader = csv.reader(csvfile)
#         fields_ = next(csvreader)
#         for row in csvreader:
#             rows.append(row)



#     print(fields_)
#     # print(rows[:6])

#     for row in rows:
#         # e = row[1][:10]
#         # d = datetime.strptime(e, '%d-%m-%Y')
#         timeSeriesData.objects.create(
#             date=row[0],
#             time=datetime.now(),
#             turbidity=row[1],
#             sdi=row[2],
#             pH=row[3],
#             temperature=row[4],
#             feedConc=row[5],
#             permConc=row[6],
#             rejectConc=0,
#             feedFlow=row[7],
#             permFlow=row[8],
#             rejectFlow=0,
#             feedPres=row[9],
#             permPres=row[10],
#             rejectPres=row[11],
#             normSaltPassage=row[12],
#             normPermFlow=row[13],
#             normDP=row[14],
#             stageId=stageMaster.objects.get(stageUniqueId=row[15])
#         )

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
        # serializer = addSetPointsSerializer(data=data_)
        setPoints.objects.update_or_create(stageId=stage_element, parameter=data_['parameter'], defaults=data_)
        # if serializer.is_valid():
        #     serializer.save(stageId=stage_element)
        # else:
        #     print('data invalid')
    
    return Response({"message": "success"})



# View all Plants: http://127.0.0.1:8000/api/cookies
# @api_view(['POST'])
# def cookies(request):
#     user_element = userMaster.objects.get(emailID=request.data['emailID'])
#     random_decimal = random.random()
#     random_int = round(random_decimal*10**6)
#     random_uid = str(uuid.uuid3)
#     user_element.cookies = random_int
#     user_element.save()

#     response = Response({"message": "success"})
#     response.set_cookie(key='token', value=random_int)

#     # Response.set_cookie(self='',key='token', value=random_uid)

#     return response


# View all Plants: http://127.0.0.1:8000/api/plant/gaugeData
@api_view(['GET'])
def gaugeData(request):
    train_element = trainMaster.objects.get(trainUniqueId=request.data['trainId'])
    stages = stageMaster.objects.filter(passId__trainId=train_element).all()
    dashboard_data = []
    for stage in stages:
        ts_data = timeSeriesData.objects.filter(stageId=stage).all()
        set_points = setPoints.objects.filter(stageId=stage).all()
        if len(ts_data) > 0 and len(set_points) > 0:
            dashboard_data.append(dashData(stage))
        # else:
        #     print(stage.stageUniqueId)
    
    return Response({"data": dashboard_data})



# FTP Check