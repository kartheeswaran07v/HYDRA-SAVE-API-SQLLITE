from django.db import models
from datetime import datetime
from datetime import date
import random
import uuid

# Create your models here.
class regionMaster(models.Model):
    name = models.CharField(max_length=45)

    def __str__(self):
        return self.name

class industryMaster(models.Model):
    name = models.CharField(max_length=45)

    def __str__(self):
        return self.name

class userMaster(models.Model):
    emailID = models.CharField(max_length=300)
    password = models.CharField(max_length=45)
    firstName = models.CharField(max_length=45)
    address = models.CharField(max_length=45)
    city = models.CharField(max_length=45)
    regionID = models.ForeignKey(regionMaster, on_delete=models.CASCADE, null=True)   
    country = models.CharField(max_length=45)
    pincode = models.BigIntegerField()
    industryId = models.ForeignKey(industryMaster, on_delete=models.CASCADE, null=True)   
    companyName = models.CharField(max_length=45)
    designation = models.CharField(max_length=45)
    isActive = models.BooleanField(help_text="1-True, 0-False", default=True)
    remarks = models.CharField(max_length=45, null=True)
    logo = models.ImageField(blank=True)
    mobileNo = models.CharField(max_length=45)
    cookies = models.CharField(max_length=100, default="ABCDEFGH")

    def __str__(self):
        return self.firstName



class plantMaster(models.Model):
    plantUniqueId = models.CharField(max_length=45, unique=True)
    plantName = models.CharField(max_length=45)
    description = models.CharField(max_length=300, null=True)
    capacity = models.FloatField()
    capacityUnit= models.CharField(max_length=45)
    feedWaterSource = models.CharField(max_length=45)
    application = models.CharField(max_length=45)
    pretreatment = models.CharField(max_length=45)
    modeOfInput = models.CharField(max_length=45, null=True)
    reportFrequecy = models.IntegerField()
    plantCreationDate = models.DateTimeField()
    createdById = models.ForeignKey(userMaster, on_delete=models.CASCADE)   
    flUnit = models.CharField(max_length=45)
    tempUnit = models.CharField(max_length=45)
    chemicalConcUnit = models.CharField(max_length=45)
    presUnit = models.CharField(max_length=45)
    energyUnit = models.CharField(max_length=45)
    
    def __str__(self):
        return self.plantUniqueId

class trainMaster(models.Model):
    random_decimal = random.random()
    random_int = round(random_decimal*10**6)

    plantId = models.ForeignKey(plantMaster, related_name='trains', on_delete=models.CASCADE)
    trainName = models.CharField(max_length=45)
    trainNumber = models.IntegerField()
    trainUniqueId = models.CharField(max_length=45, unique=True)
    
    
    def __str__(self):
        return self.trainUniqueId

class passMaster(models.Model):
    random_decimal = random.random()
    random_int = round(random_decimal*10**6)

    trainId = models.ForeignKey(trainMaster, related_name='passes', on_delete=models.CASCADE)         
    passName = models.CharField(max_length=45)
    passNumber = models.IntegerField()
    passUniqueId = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.passUniqueId

class stageMaster(models.Model):
    passId = models.ForeignKey(passMaster, related_name='stages', on_delete=models.CASCADE)
    stageNumber = models.CharField(max_length=45)
    isHybrid_if = models.BooleanField(help_text="1-True, 0-False")   
    elementsPerVessel_if = models.IntegerField()
    numberOfVessels_if = models.IntegerField()
    stageUniqueId = models.CharField(max_length=45, unique=True)
    def __str__(self):
        return self.stageUniqueId



class OTP(models.Model):
    username = models.CharField(max_length=100)
    otp = models.BigIntegerField()
    time = models.DateTimeField()

class transactionMaster(models.Model):
    plantId = models.ForeignKey(plantMaster, on_delete=models.CASCADE)
    userId = models.ForeignKey(userMaster, on_delete=models.CASCADE) 
    transactionId = models.CharField(max_length=45)
    time = models.DateTimeField()
    amount =  models.FloatField()
    transactionStatus = models.CharField(max_length=45)
    paymentType = models.CharField(max_length=45)
    description = models.CharField(max_length=45)
    invoiceNumber = models.CharField(max_length=45)

class roleMaster(models.Model):
    name = models.CharField(max_length=45)

    def __str__(self):
        return self.name

class plantUserRelationship(models.Model):
    plantId = models.ForeignKey(plantMaster, on_delete=models.CASCADE)
    userId = models.ForeignKey(userMaster, on_delete=models.CASCADE)
    roleId = models.ForeignKey(roleMaster, on_delete=models.CASCADE)
    isActive = models.BooleanField(help_text="1-True, 0-False")

class deviceMaster(models.Model):
    plcModel = models.CharField(max_length=45)   
    plcMake = models.CharField(max_length=45)
    commType = models.CharField(max_length=45)
    isActive = models.CharField(max_length=45)
    plantId = models.ForeignKey(plantMaster, on_delete=models.CASCADE)

    def __str__(self):
        return self.plcMake

class invitesMaster(models.Model):
    invitedById = models.ForeignKey(userMaster, on_delete=models.CASCADE)
    emailId = models.CharField(max_length=300)
    roleId = models.ForeignKey(roleMaster, on_delete=models.CASCADE)
    plantId = models.ForeignKey(plantMaster, on_delete=models.CASCADE, null=True)
    status = models.BooleanField(help_text="1-True, 0-False")

class reviewMaster(models.Model):
    content = models.CharField(max_length=1000)
    reviewById = models.ForeignKey(userMaster, on_delete=models.CASCADE)
    stageId = models.ForeignKey(stageMaster, on_delete=models.CASCADE)
    date = models.DateField()

class errorLogs(models.Model):
    userId = models.ForeignKey(userMaster, on_delete=models.CASCADE)
    stageId = models.ForeignKey(stageMaster, on_delete=models.CASCADE)
    errorType = models.CharField(max_length=45)
    errorCode = models.CharField(max_length=45)
    errorDescription = models.CharField(max_length=45)
    time = models.DateTimeField()
    status = models.BooleanField(help_text="1-True, 0-False")
    resolutionDate = models.DateField()

class loginMaster(models.Model):
    userId = models.ForeignKey(userMaster, on_delete=models.CASCADE)
    logInTime = models.DateTimeField()
    logOutTime = models.DateTimeField()
    IPAddress = models.CharField(max_length=45) 
    deviceType = models.CharField(max_length=45)
    browserName = models.CharField(max_length=45)
    browserVersion = models.CharField(max_length=45)




class nittoUserMapping(models.Model):
    userId = models.ForeignKey(userMaster, on_delete=models.CASCADE)
    regionId = models.ForeignKey(regionMaster, on_delete=models.CASCADE)
    roleId = models.ForeignKey(roleMaster, on_delete=models.CASCADE)

class preferences(models.Model):
    userId = models.ForeignKey(userMaster, on_delete=models.CASCADE)
    language = models.CharField(max_length=45)
    modeOfInput = models.CharField(max_length=45)
    plantOrder = models.IntegerField()

class companyMaster(models.Model):
    companyName = models.CharField(max_length=300)
    enterpiseId = models.CharField(max_length=45)
    companyType = models.CharField(max_length=45)
    billingAddress = models.CharField(max_length=500)
    approved = models.BooleanField(help_text="1-True, 0-False")
    regionId = models.ForeignKey(regionMaster, on_delete=models.CASCADE)
    pincode = models.BigIntegerField()
    domain = models.CharField(max_length=45)
    createdById = models.ForeignKey(userMaster, on_delete=models.CASCADE)

    def __str__(self):
        return self.companyName


class enterpriseApproval(models.Model):
    enterpriseId = models.ForeignKey(companyMaster, on_delete=models.CASCADE)
    modifiedById = models.ForeignKey(userMaster, on_delete=models.CASCADE)
    isRejected = models.BooleanField(help_text="1-True, 0-False")
    remarks = models.CharField(max_length=45)
    datetime = models.DateTimeField()
    isApproved = models.CharField(max_length=45)

class stageUserRelationship(models.Model):
    userId = models.ForeignKey(userMaster, on_delete=models.CASCADE)
    stageId = models.ForeignKey(stageMaster, on_delete=models.CASCADE) 

class subscriptions(models.Model):
    stageId = models.ForeignKey(stageMaster, on_delete=models.CASCADE)
    startDate = models.DateField()
    endDate = models.DateField()
    tier = models.IntegerField(null=True, blank=True)
    transactionMaster_id = models.OneToOneField(transactionMaster, on_delete=models.CASCADE, primary_key=True)

class elementMaster(models.Model):
    stageId = models.ForeignKey(stageMaster, related_name='elements', on_delete=models.CASCADE)
    elementName_if = models.CharField(max_length=45)
    elementLocation_if = models.CharField(max_length=45)

    def __str__(self):
        return self.elementName_if

class alarmMaster(models.Model):
    alarmContent = models.CharField(max_length=45)
    datetime = models.DateTimeField()
    stageId = models.ForeignKey(stageMaster, on_delete=models.CASCADE)

    def __str__(self):
        return self.alarmContent

class setPoints(models.Model):
    stageId = models.ForeignKey(stageMaster, on_delete=models.CASCADE)
    reference = models.FloatField()
    high = models.FloatField()
    highhigh = models.FloatField()
    low = models.FloatField()
    lowlow = models.FloatField()
    parameter = models.CharField(max_length=45)

class deviceDetails(models.Model):
    variableName = models.CharField(max_length=45)
    registeredAddress = models.CharField(max_length=45)
    deviceId = models.ForeignKey(deviceMaster, on_delete=models.CASCADE)
    dataType = models.CharField(max_length=45) 
    registerAddress2 = models.CharField(max_length=45, null=True, blank=True)
    stageId = models.ForeignKey(stageMaster, on_delete=models.CASCADE)

    def __str__(self):
        return self.variableName

class timeSeriesData(models.Model):
    stageId =  models.ForeignKey(stageMaster, related_name='ts_data', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    turbidity = models.FloatField(blank=True, null=True)
    sdi = models.FloatField(blank=True, null=True)
    pH = models.FloatField(blank=True, null=True)
    temperature = models.FloatField()
    feedConc = models.FloatField()
    permConc = models.FloatField()
    rejectConc = models.FloatField(blank=True, null=True)
    feedFlow = models.FloatField(blank=True, null=True)
    permFlow = models.FloatField()
    rejectFlow = models.FloatField()
    permPres = models.FloatField()
    feedPres = models.FloatField()
    rejectPres = models.FloatField()
    normSaltPassage = models.FloatField(blank=True, null=True)
    normPermFlow = models.FloatField(blank=True, null=True)
    normDP = models.FloatField(blank=True, null=True)
    remarks = models.CharField(max_length=500, blank=True, null=True) 
    energy = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.stageId.stageUniqueId}-{self.date}"


class referenceData(models.Model):
    stageId =  models.ForeignKey(stageMaster, on_delete=models.CASCADE)
    date = models.DateField()
    remarks = models.CharField(max_length=45) 
    timeSeriesDataId = models.ForeignKey(timeSeriesData, on_delete=models.CASCADE)

class cipOrFlushing(models.Model):
    pH = models.FloatField(blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True) 
    recirculationTime = models.FloatField(blank=True, null=True)
    soakingTime = models.FloatField(blank=True, null=True)
    flushingTime = models.FloatField(blank=True, null=True)
    comments = models.FloatField(blank=True, null=True)
    stageId =  models.ForeignKey(stageMaster, related_name="cips", on_delete=models.CASCADE)

class resourceData(models.Model):
    energy = models.FloatField()
    date = models.DateField()
    stageId = models.ForeignKey(stageMaster, on_delete=models.CASCADE)
    dummyColumn1 = models.CharField(max_length=45) 
    dummyColumn2 = models.CharField(max_length=45) 


class energyEfficienty(models.Model):
    motorEff = models.FloatField()
    pumpEff = models.FloatField()
    vfdEff = models.FloatField()
    stageId = models.ForeignKey(stageMaster, on_delete=models.CASCADE)

class pricingParameters(models.Model):
    parameterType = models.CharField(max_length=45)   
    parameter = models.CharField(max_length=45) 

    def __str__(self):
        return self.parameterType

class factorMaster(models.Model):
    parameterId = models.ForeignKey(pricingParameters, on_delete=models.CASCADE)
    regionId = models.ForeignKey(regionMaster, on_delete=models.CASCADE)   
    factor = models.FloatField()

class contactsMaster(models.Model):
    name = models.CharField(max_length=100) 
    mobile = models.CharField(max_length=45) 
    email = models.CharField(max_length=45) 
    isSuperUserd = models.BooleanField(help_text="1-True, 0-False") 
    enterpriseId = models.ForeignKey(companyMaster, on_delete=models.CASCADE)

class discountDetails(models.Model):
    discount = models.FloatField()
    period = models.CharField(max_length=45) 
    companyId = models.ForeignKey(companyMaster, on_delete=models.CASCADE)

class graphScreens(models.Model):
    stageUserRelId = models.ForeignKey(stageUserRelationship, on_delete=models.CASCADE)
    screenName = models.CharField(max_length=45)  

    def __str__(self):
        return self.screenName

class parametersScreen(models.Model):
    parameterName = models.CharField(max_length=45)
    config = models.CharField(max_length=45)
    screenId = models.ForeignKey(graphScreens, on_delete=models.CASCADE)

    def __str__(self):
        return self.parameterName

class cipChemicals(models.Model):
    chemicalName = models.CharField(max_length=200)
    chemicalConc = models.FloatField()
    cipId = models.ForeignKey(cipOrFlushing, on_delete=models.CASCADE)

    def __str__(self):
        return self.chemicalName

class languageMaster(models.Model):
    englishContent = models.CharField(max_length=45)  
    chineseContent = models.CharField(max_length=45)
    spanishContent = models.CharField(max_length=45)
    portugueseContent = models.CharField(max_length=45)
    japaneseContent = models.CharField(max_length=45)
    lang1Content = models.CharField(max_length=45)
    lang2Content = models.CharField(max_length=45)
    lang3Content = models.CharField(max_length=45)
    lang4Content = models.CharField(max_length=45)
    lang5Content = models.CharField(max_length=45)


class contentMaster(models.Model):
    languageId = models.ForeignKey(languageMaster, on_delete=models.CASCADE)
    typeOfMessage = models.CharField(max_length=45)
    buttons = models.CharField(max_length=45)
    autoDissapear = models.BooleanField(help_text="1-True, 0-False")

class emailDraftMaster(models.Model):
    formatNumber = models.IntegerField()
    subjectContentId = models.ForeignKey(languageMaster, on_delete=models.CASCADE, related_name='email_drafts_subject')
    bodyContentId = models.ForeignKey(languageMaster, on_delete=models.CASCADE, related_name='email_drafts_body')
    bccEmailAddress = models.CharField(max_length=45)         

class domainMaster(models.Model):
    domain = models.CharField(max_length=45)
    types = models.BooleanField(help_text="1-True, 0-False") 
    # True means Webmail, False means Competitor

    def __str__(self):
        return self.domain



