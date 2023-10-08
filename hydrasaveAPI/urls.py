from django.urls import path
from . import views
from django.conf import settings
 
urlpatterns = [
    path('', views.getData),
    path('api/user/check', views.check, name = 'check'),
    path('api/user/checkPW', views.checkPassword, name = 'check PW'),
    path('api/user/register-otp', views.sendOTP, name = 'sendOTP'),
    path('api/user/check-otp', views.checkOTP, name='checkOTP'),
    path('api/user/register', views.registration, name='register'),
    path('api/user/reset-pw', views.resetPassword, name='Reset Password'),
    path('api/plant/allPlants', views.allPlants, name='All Plants'),
    path('api/plant/addPlant', views.addPlant, name="Add Plant"),
    path('api/plant/tsData', views.tsData, name='tsData'),
    path('api/plant/addTsData', views.addTsData, name='Add Time series Data'),
    path('api/plant/setPoint', views.setPoint, name='Set Points'),
    path('api/plant/dashPlants', views.dashPlants, name='Plant Trains'),
    path('api/plant/dropdown', views.dropdown, name='Dropdown'),
    path('api/plant/getSetPoints', views.getSetPoints, name='Set Points'),
    path('api/plant/addSetPoints', views.addSetPoints, name='Add Set Points'),
    path('api/plant/tsDataTable', views.tsDataTable, name='Table Data'),
    path('api/cookies', views.cookies, name='cookies'),
    # path('api/addLargeData', views.addLargeData, name="addLargeData")
]