from django.shortcuts import render
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import plantMaster, userMaster, domainMaster, OTP, regionMaster, industryMaster
from .serializer import PlantSerializer, UserSerializer
from django.core.exceptions import ObjectDoesNotExist


def getDomain(username):
    domain_ = username.split('@')[1]
    domain = domain_.split('.')[0]
    return domain

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
