from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from .models import *
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()

class UserRegistation(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializers = UserSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()

            subject = request.data.get('subject', 'Sucess Full Registaion')
            message = request.data.get('message', 'We Reached ')
            from_email = 'biwinfelix@example.com'
            recipient_list = [request.data.get('to_email', request.data.get('email'))]

            try:
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                return Response({'detail': 'Email sent successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'detail': f'Failed to send email. Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                # return Response ('Data Saved')
        
        else:
            return Response('Data Missing')
        

class Login(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        email = request.data.get('email')
        password = request.data.get('password')
        # return Response(1)
        user = User.objects.get(email=email)
        if user:
            refresh = RefreshToken.for_user(user)

            custom_data = {
                'email': user.email,
                'id': user.id
            }
            refresh['custom_data'] = custom_data 
            refresh.access_token.payload['custom_data'] = custom_data 

            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'id': user.id
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class StockAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stocks = Stock.objects.all()
        serializer = CreateStockSerializer(stocks, many=True)
        return Response(serializer.data)

    def post(self, request):
        if 'stock' == request.data.get('name'):
            serializer = ListStockSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)  # Associate the stock with the current user
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Wrong API Call')
    

class LogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stocks = Log.objects.all()
        serializer = CreateLogSerializer(stocks, many=True)
        return Response(serializer.data)

    def post(self, request):
        if 'stock' == request.data.get('name'):
            serializer = ListLogSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)  # Associate the stock with the current user
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Wrong API Call')