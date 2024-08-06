from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import IntegrityError
import string, secrets
from rest_framework import status
from datetime import datetime,timedelta
from django.utils import timezone

from .helpers import mobile_number_validator,email_validator,password_validator, send_welcome_email, send_otp_email
from . import serializer
from .models import User,Profile

class RegisterUser(APIView):
    def post(self, request):
        serializer_data = serializer.UserSerializer(data = request.data)
        serializer_data.is_valid(raise_exception=True)
        data = serializer_data.validated_data
        if not mobile_number_validator(str(data.get('mobile_number'))):
            return Response({'message':'invalid mobile number.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        if not email_validator(str(data.get('email'))):
            return Response({'message':'invalid email.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        
        user = User()
        try: 
            user.mobile_number = data.get('mobile_number')
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.email = data.get('email')
            user.username = data.get('email')
            user.age = data.get('age')
            user.is_staff = data.get('is_staff')
            user.set_password(data.get('password'))
            user.save()
        except IntegrityError as e:
            return Response({'message':'Mobile number/ Email/ Username mustbe unique.','exception':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
        Profile.objects.create(user=user,address = data.get('address'),gender=data.get('gender'))
        subject = "Thanks for Joining Books Buzz World!"
        send_welcome_email(to_email=user.email, subject=subject, user_name=user.first_name)

        return Response({'message':f'User Got created with username: {user.username}','user_id':user.id,'status':True},status=status.HTTP_201_CREATED)

class ForgetPassword(APIView):
    def get(self, request):
        request = request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["email"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        email = request.get('email')
        if not email:
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        if not email_validator(email=email):
            return Response({'message':'Invalid email.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        
        characters = string.ascii_letters + string.digits
        security_code = ''.join(secrets.choice(characters) for _ in range(6))

        user = User.objects.filter(email=email,is_active=True).first()
        if not user:
            return Response({'message':f'No user Found with the email {email}','status':False}, status=status.HTTP_400_BAD_REQUEST)
        user_profile = Profile.objects.get(user__pk=user.pk)
        user_profile.security_code = security_code
        user_profile.verified = False
        user_profile.security_code_validated_upto = datetime.now()+timedelta(minutes=5)
        user_profile.save()

        subject="Password Reset Request for Books Buzz"        
        send_otp_email(to_email=email, user_name=user.first_name, subject=subject, otp=security_code)
        return Response({'message':f"Hi {user.first_name}, OTP sent to given Email, please check",'user_id':user.pk,'status':True},status=status.HTTP_200_OK)

class OTPVerification(APIView):
    def get(self,request):
        request = request.GET
        if not(len(request.keys())==2 and all(key in request for key in ["otp", "user_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        security_code = request.get('otp')
        user_id = request.get('user_id')
        if not(security_code and user_id and user_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        user_profile = Profile.objects.filter(user__pk=user_id,user__is_active=True).first()
        if not user_profile:
            return Response({'message':'User Not Found/User is inactive','status':False},status=status.HTTP_400_BAD_REQUEST)
        
        if security_code == user_profile.security_code:
            if not timezone.now() <= user_profile.security_code_validated_upto:
                return Response({'message': 'OTP has expired.', 'status': False}, status=status.HTTP_400_BAD_REQUEST)
            if user_profile.verified==True:
                return Response({'message':'The OTP has already been verified. Please request a new OTP','status':False},status=status.HTTP_400_BAD_REQUEST)
            user_profile.verified = True
            user_profile.save()
            return Response({'message':'OTP verified.','status':True},status=status.HTTP_200_OK)
        else: return Response({'message':'Incorrect OTP.','status':False},status=status.HTTP_400_BAD_REQUEST)

class ResetPassword(APIView):
    def post(self, request):
        data = request.data
        if not (type(data)==dict and len(data.keys())==2 and all(key in data for key in ["password", "user_id"])):
            return Response({"message": "The request data is invalid.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        password = request.data.get('password')
        user_id = request.data.get('user_id')
        if not(user_id and password and type(user_id)==int and type(password)==str):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(pk=user_id,is_active=True).first()
        if not user:
            return Response({'message':'No user found with the request data.','status':False},status=status.HTTP_400_BAD_REQUEST)
        user_profile = Profile.objects.filter(user__pk=user.pk,user__is_active=True).first()
        if not user_profile:
            return Response({'message':'No user found with the request data.','status':False},status=status.HTTP_400_BAD_REQUEST)
        if not password_validator(password):
            return Response({'message':'Password must Contain a special character,a number, and length must be more than 8 letters.','status':False},status=status.HTTP_400_BAD_REQUEST)
        if not user_profile.verified:
            return Response({'message':'OTP not verified/ Do Request for Reset password.','status':False},status=status.HTTP_400_BAD_REQUEST)
        if user.check_password(password):
            return Response({'message':'Password should not be same like OLD password','status':False},status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(password)
        user_profile.verified = False
        user_profile.security_code = None
        user_profile.otp = None
        user_profile.save()
        user.save()
        return Response({'message':'password Sucessfully changed.','status':True},status=status.HTTP_201_CREATED)
