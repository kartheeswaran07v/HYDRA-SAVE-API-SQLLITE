from django.shortcuts import render
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import stageMaster, setPoints, domainMaster, OTP, regionMaster, industryMaster, timeSeriesData
from .serializer import PlantSerializer, UserSerializer
from django.core.exceptions import ObjectDoesNotExist
import math


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



validated_data = {
    "date": "2023-10-13",
    "time": "12:47:40",
    "turbidity": 0.09,
    "sdi": 2.6,
    "pH": 7.76,
    "temperature": 29.14,
    "feedConc": 52810,
    "permConc": 396,
    "rejectConc": None,
    "feedFlow": None,
    "permFlow": 179,
    "rejectFlow": 340,
    "permPres": 0.95,
    "feedPres": 49.14,
    "rejectPres": 47.95
}


def getNormData(**kwargs):
    Turbidity = kwargs.get('turbidity')
    SDI = kwargs.get('sdi')
    PH = kwargs.get('pH')
    Temperature = kwargs.get('temperature')
    FeedConcentration = kwargs.get('feedConc')
    PermeateConcentration = kwargs.get('permConc')
    ConcentrationFlows = kwargs.get('rejectFlow')
    PermeateFlows = kwargs.get('permFlow')
    FeedPressure = kwargs.get('feedPres')
    ConcentrationPressure = kwargs.get('rejectPres')
    PermeatePressure = kwargs.get('permPres')
    V = 1.00
    EPV = 1.00
    Ke = 2700.00
    EMAe = 400.00
    Qpe = 9000.00
    # print(f"{norm.SSPn:.2f}\t{norm.QSPn:.2f}\t{norm.DPn:.2f}")

    recovery = PermeateFlows / (PermeateFlows + ConcentrationFlows)
    DP = FeedPressure - ConcentrationPressure
    To = Temperature
    Cfo = FeedConcentration
    Cpo = PermeateConcentration
    Qco = ConcentrationFlows
    Qpo = PermeateFlows
    Pfo = FeedPressure
    Pco = ConcentrationPressure
    Ppo = PermeatePressure
    Conf = math.log(1 / (1 - recovery)) / recovery
    Cf_ave = Cfo * Conf
    FOP_ave = Cf_ave * 0.03851 * (273 + To) / (1000 - Cf_ave / 1000)
    POP = Cpo * 0.03851 * (273 + To) / (1000 - Cpo / 1000)
    DPo = Pfo - Pco
    NDP = Pfo - (0.5 * DPo) - Ppo - FOP_ave + POP
    SFX = 1440 * Qpo / (EPV * V * EMAe)
    SSP = 100 * Cpo / Cf_ave
    SSR = 100 - SSP
    TCF = math.exp(Ke * ((1 / 298) - (1 / (273 + To))))
    ASPn = SSP * (SFX / (Qpe / EMAe)) / TCF
    SSPn = SSP * (PermeateFlows / PermeateFlows)
    QSPn = PermeateFlows * (NDP / NDP)
    DPn = ((DP * math.pow((PermeateFlows / 2 + ConcentrationFlows), 1.4) / math.pow(
        ((PermeateFlows / 2) + ConcentrationFlows), 1.4)) * (1 + 0.01 * (To - 25)))
    result_dict = {"nsp": round(SSPn, 3), "npf": round(QSPn,3), "ndp": round(DPn,3)}
    return result_dict




def get_param_details(percent_param, param_object, param_name):
    if param_name == "NPF":
        if float(param_object.low) < percent_param <= float(param_object.high):
            status = 'normal'
        elif percent_param <= float(param_object.highhigh):
            status = 'high'
        elif float(param_object.highhigh) < percent_param:
            status = 'highhigh'
        elif float(param_object.lowlow) < percent_param <=float(param_object.low):
            status = 'low'
        elif float(param_object.lowlow) >= percent_param:
            status = 'lowlow'
    else:
        if percent_param <= float(param_object.high):
            status = 'normal'
        elif percent_param <= float(param_object.highhigh):
            status = 'high'
        elif float(param_object.highhigh) < percent_param:
            status = 'highhigh'
    return status


def getHighStatus(nsp, npf, ndp):
    if 'highhigh' in [nsp, npf, ndp]:
        status = 'critical'
    elif 'lowlow' in [nsp, npf, ndp]:
        status = 'critical'
    elif 'high' in [nsp, npf, ndp]:
        status = 'alert'
    elif 'low' in [nsp, npf, ndp]:
        status = 'alert'
    else:
        status = 'normal'
    return status


def dashData(stage_element):
    # Get the latest ts data object
    last_ts = timeSeriesData.objects.filter(stageId=stage_element).last()
    nsp, npf, ndp = last_ts.normSaltPassage, last_ts.normPermFlow, last_ts.normDP

    # Declare colors for gauge graph
    colors = ["#DB454C", "#86D1F2", "#171C8F", "#232D3F"]
    colors_npf = ["#171C8F", "#86D1F2", "#DB454C", "#60B044"]

    # Get set point objects for a particular stage and parameter
    nsp_set = setPoints.objects.filter(stageId=stage_element, parameter='NSP').last()
    npf_set = setPoints.objects.filter(stageId=stage_element, parameter='NPF').last()
    ndp_set = setPoints.objects.filter(stageId=stage_element, parameter='NDP').last()

    # Get percentage difference between last data and reference data
    nsp_percent = round(((nsp-nsp_set.reference)/nsp_set.reference), 3) * 100
    npf_percent = round(((npf-npf_set.reference)/npf_set.reference), 3) * 100
    ndp_percent = round(((ndp-ndp_set.reference)/ndp_set.reference), 3) * 100

    # Get status of the parameter
    nsp_status = get_param_details(nsp_percent, nsp_set, "NSP")
    npf_status = get_param_details(npf_percent, npf_set, "NPF")
    ndp_status = get_param_details(ndp_percent, ndp_set, "NDP")

    print(nsp_percent, npf_percent, ndp_percent)
    # Get overall status for a particular stage
    overall_status = getHighStatus(nsp_status, npf_status, ndp_status)

    # Structure json as per requirement
    json_ = {
      "data": [
        {
            "value": round(nsp_percent, 3),
            "ranges": [nsp_set.low, nsp_set.high, nsp_set.highhigh, nsp_set.highhigh + 10],
            "colors": colors,
            "max": nsp_set.highhigh + 10,
            "min": nsp_set.lowlow - 10,
            "label": "NSP"
        },
        {
            "value": round(npf_percent,3),
            "ranges": [npf_set.low, npf_set.high, npf_set.highhigh, npf_set.highhigh + 10],
            "colors": colors_npf,
            "max": npf_set.highhigh + 10,
            "min": npf_set.lowlow - 10,
            "label": "NPF"
        },
        {
            "value": round(ndp_percent,3),
            "ranges": [ndp_set.low, ndp_set.high, ndp_set.highhigh, ndp_set.highhigh + 10],
            "colors": colors,
            "max": ndp_set.highhigh + 10,
            "min": ndp_set.lowlow - 10,
            "label": "NDP"
        }
      ],
      "status": overall_status,
      "stageName": stage_element.stageUniqueId
    }

    return json_


# a = ts_data_date('2018-03-13', '2018-04-06')
# print(a)