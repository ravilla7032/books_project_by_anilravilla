from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signupuser', views.RegisterUser.as_view(http_method_names=['post']), name='Register the User.'),
    path('forgetpassword_otp', views.ForgetPassword.as_view(http_method_names=['get']), name='triggering OTP for forget password'),
    path('verify_otp', views.OTPVerification.as_view(http_method_names=['get']), name='Verifying OTP to reset password.'),
    path('reset_password', views.ResetPassword.as_view(http_method_names=['post']), name='Reset Users password.'),
]