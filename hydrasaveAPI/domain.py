from django.shortcuts import render
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import plantMaster, userMaster, domainMaster, OTP, regionMaster, industryMaster, timeSeriesData
from .serializer import PlantSerializer, UserSerializer
from django.core.exceptions import ObjectDoesNotExist


def getDomain(username):
    domain_ = username.split('@')[1]
    domain = domain_.split('.')[0]
    return domain.lower()

def checkWebmail(username):
    domain = getDomain(username)
    webmail = domainMaster.objects.filter(domain=domain, types=True).first()
    if webmail:
        isWebmail = True
    if not webmail:
        isWebmail = False

    return isWebmail

def checkCompetitor(username):
    domain = getDomain(username)
    competitor = domainMaster.objects.filter(domain=domain, types=False).first()
    if competitor:
        isCompetitor = True
    else:
        isCompetitor = False
    return isCompetitor

def bestApproximate(x, y):
    sum_x = 0
    sum_y = 0
    sum_xy = 0
    sum_x2 = 0
    n = len(x)
    for i in range(0, n):
        sum_x += x[i]
        sum_y += y[i]
        sum_xy += x[i] * y[i]
        sum_x2 += pow(x[i], 2)

    m = float((n * sum_xy - sum_x * sum_y)
              / (n * sum_x2 - pow(sum_x, 2)))

    c = float(sum_y - m * sum_x) / n

    # print("m = ", m)
    # print("c = ", c)
    return m, c


def linear_graph(y):
    len_x = len(y)
    x = range(len_x)
    m, c = bestApproximate(x, y)
    # m = 0.0002854681878130317
    # c = -11.655193900327705
    y_linear_list = []
    for i in x:
        y = m * i + c
        y_linear_list.append(round(y, 3))
    # print(m, c)
    return y_linear_list, m, c


def ts_data_date(fromDate, toDate, stageId):
    # from_data = timeSeriesData.objects.filter(date=fromDate, stageId=stageId).first()
    # to_data = timeSeriesData.objects.filter(date=toDate, stageId=stageId).first()
    range_data = timeSeriesData.objects.filter(date__range=[fromDate, toDate], stageId=stageId)

    return range_data


def statisticalData(data):
    mean = sum(data) / len(data)

    min_ = min(data)

    max_ = max(data)

    std = sum([(i - mean) ** 2 for i in data]) / (len(data) - 1)

    return {'mean': round(mean, 3), 'min': round(min_, 3), 'max': round(max_, 3), 'std': round(std, 3)}


# a = ts_data_date('2018-03-13', '2018-04-06')
# print(a)