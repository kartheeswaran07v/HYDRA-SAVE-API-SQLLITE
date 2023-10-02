from rest_framework import serializers
from .models import *
 
class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model=plantMaster
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=userMaster
        fields = ['emailID', 'password', 'firstName', 'address', 'city', 'country', 'pincode', 'companyName', 'designation', 'isActive', 'remarks', 'mobileNo']


class elementSerializer(serializers.ModelSerializer):
    class Meta:
        model = elementMaster
        fields = "__all__"

class StageSerializer(serializers.ModelSerializer):
    elements = elementSerializer(many=True, read_only=True)
    class Meta:
        model=stageMaster
        fields="__all__"

class PassSerializer(serializers.ModelSerializer):
    stages = StageSerializer(many=True, read_only=True)
    class Meta:
        model=passMaster
        fields="__all__"

class TrainSerializer(serializers.ModelSerializer):
    passes = PassSerializer(many=True, read_only=True)
    class Meta:
        model=trainMaster
        fields="__all__"
 
class PlantSerializer(serializers.ModelSerializer):
    trains = TrainSerializer(many=True, read_only=True)
    class Meta:
        model=plantMaster
        fields="__all__"



class tsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = timeSeriesData
        fields = "__all__"

class tsStageSerializer(serializers.ModelSerializer):
    ts_data = tsDataSerializer(many=True, read_only=True)
    class Meta:
        model=stageMaster
        fields=["stageUniqueId", "ts_data"]

class tsPassSerializer(serializers.ModelSerializer):
    stages = tsStageSerializer(many=True, read_only=True)
    class Meta:
        model=passMaster
        fields="__all__"

class tsTrainSerializer(serializers.ModelSerializer):
    passes = tsPassSerializer(many=True, read_only=True)
    class Meta:
        model=trainMaster
        fields="__all__"
 
class tsPlantSerializer(serializers.ModelSerializer):
    trains = tsTrainSerializer(many=True, read_only=True)
    class Meta:
        model=plantMaster
        fields=["plantUniqueId", "plantName", "trains"]


class dashTrainSerializer(serializers.ModelSerializer):
    class Meta:
        model=trainMaster
        fields=["trainName", "trainNumber"]
 
class dashPlantSerializer(serializers.ModelSerializer):
    trains = dashTrainSerializer(many=True, read_only=True)
    class Meta:
        model=plantMaster
        fields=["id","plantName", "plantUniqueId", "trains"]