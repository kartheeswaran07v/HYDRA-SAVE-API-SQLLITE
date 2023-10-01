from django.urls import path
from . import views
from django.conf import settings
 
urlpatterns = [
    path('', views.getData),
    path('user/check/', views.check, name = 'check'),
    path('user/checkPW/', views.checkPassword, name = 'check PW'),
    path('user/register-otp/', views.sendOTP, name = 'sendOTP'),
    path('user/check-otp/', views.checkOTP, name='checkOTP'),
    path('user/register/', views.registration, name='register'),
    path('user/reset-pw/', views.resetPassword, name='Reset Password'),
    path('plant/allPlants/', views.allPlants, name='All Plants'),
    path('plant/addPlant/', views.addPlant, name="Add Plant"),
    path('plant/tsData/', views.tsData, name='tsData'),
    path('plant/addTsData/', views.addTsData, name='Add Time series Data')
]