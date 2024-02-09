from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from .models import *
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Sum
from rest_framework.pagination import PageNumberPagination
import math
from shapely.geometry import Point, Polygon
from django.core.exceptions import ObjectDoesNotExist


User = get_user_model()
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100



class UserRegistation(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializers = UserSerializer(data=request.data)
        if serializers.is_valid():
            
            subject = request.data.get('subject', 'Sucess Full Registaion')
            message = request.data.get('message', 'We Reached ')
            from_email = 'biwinfelix@gmail.com'
            recipient_list = [request.data.get('to_email', request.data.get('email'))]
            serializers.save()
            print('User Saved')
            try:
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                
                return Response({'detail': 'Email sent successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'detail': f'Failed to send email. Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                # return Response ('Data Saved')
            
            
        
        else:
            return Response(serializers.errors)
        
    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response({'detail': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        

# def is_inside_geo_fence(latitude, longitude):   
#     fence_coordinates = [(10.933942, 76.737375), (10.943666, 76.737467), (10.944398, 76.748322), (10.932758, 76.747158)] 
#     point = Point(longitude, latitude)
#     polygon = Polygon(fence_coordinates)
#     return polygon.contains(point)



def is_inside_geo_fence(lat, long):
    fence_points = [(10.933942, 76.737375), (10.943666, 76.737467), (10.944398, 76.748322), (10.932758, 76.747158)]

    if not isinstance(lat, (float, int)):
        raise ValueError("Latitude must be a number.")
    if not isinstance(long, (float, int)):
        raise ValueError("Longitude must be a number.")
    if not isinstance(fence_points, list) or not all(isinstance(point, tuple) for point in fence_points):
        raise ValueError("Fence points must be a list of tuples.")

    lat_rad = lat * math.pi / 180
    long_rad = long * math.pi / 180

    num_intersections = 0
    for i in range(len(fence_points)):
        start_point = fence_points[i]
        start_lat_rad = start_point[0] * math.pi / 180
        start_long_rad = start_point[1] * math.pi / 180

        next_point = fence_points[(i + 1) % len(fence_points)]
        next_lat_rad = next_point[0] * math.pi / 180
        next_long_rad = next_point[1] * math.pi / 180

        dx = next_long_rad - start_long_rad
        dy = next_lat_rad - start_lat_rad

        if (dy > 0) != (dy * (long_rad - start_long_rad) - dx * (lat_rad - start_lat_rad) > 0):
            if start_lat_rad <= lat_rad <= next_lat_rad or next_lat_rad <= lat_rad <= start_lat_rad:
                num_intersections += 1
    return num_intersections % 2 == 1


class Login(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email,password=password)
        if user:
            if user.block==False and is_inside_geo_fence(request.data.get('latitude'),request.data.get('longitude')):
                

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
                user = User.objects.get(email=email)
                if user.warning >=2:
                    return Response('Contact Administator')
                elif user.warning <2:
                    user.warning+=1
                    user.save()
                    return Response('You are not in the location')

        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination

    def get(self, request):
        stocks = Log.objects.all().order_by('-id')
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(stocks, request)
        serializer = ListLogSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
            
        if email:
            user = User.objects.filter(email=email).first()
        elif phone_number:
            user = User.objects.filter(phone_number=phone_number).first()
        else:
            return Response('Email or phone number is required', status=status.HTTP_400_BAD_REQUEST)
            
        if user:
            user_logs = Log.objects.filter(user=user).order_by('-id')
            serializer = ListLogSerializer(user_logs, many=True)
            stock = Stock.objects.filter(user=user)
            stock_serializer = CreateStockSerializer(stock,many = True)
            user_serializer = UserSerializer(user)
            res = {
                'Log' : serializer.data,
                'stock1': stock_serializer.data,
                'user': user_serializer.data
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            return Response('User not found', status=status.HTTP_404_NOT_FOUND)


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
    



class Stock1(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stock_name = request.data.get('stock_name')
        if 'stock' == stock_name:
            serializer = CreateLogSerializer(data=request.data)

            usr = User.objects.get(pk= request.data.get('user'))
            if serializer.is_valid():
                stock_quantity = request.data.get('quantity')
                try:
                    stock = Stock.objects.get(user=request.user)

                    if request.data.get('operations') == 'buy':
                        if usr.bank_balance >= request.data.get('total_amount'):
                            usr.bank_balance -= request.data.get('total_amount')
                            stock.stock_quantity += stock_quantity
                            stock.save()
                            usr.save()
                        else:
                            return Response('You cannot buy this much stock. Lack Of money')

                    if request.data.get('operations') == 'sell':
                        print(stock_quantity,stock.stock_quantity)
                        if stock.stock_quantity >= stock_quantity:  
                            usr.bank_balance += request.data.get('total_amount')
                            stock.stock_quantity -= stock_quantity
                            stock.save()
                            usr.save()
                        else:
                            return Response('Invalid Stock qunatity')
                    
                except Stock.DoesNotExist:
                    if usr.bank_balance >= request.data.get('total_amount') and request.data.get('operations') == 'buy':
                        stock = Stock.objects.create(user=request.user, stock_quantity=stock_quantity)

                    elif request.data.get('operations') == 'sell':
                        return Response('You dont have any stock to sell')
                
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Wrong API Call')



class UpdateStockPricesView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        
        # For demonstration, let's assume the stock prices are provided as keys in the request data
        stock1_price = data.get('stock1_price', 0)
        stock2_price = data.get('stock2_price', 0)
        stock3_price = data.get('stock3_price', 0)
        
        # Now, calculate the total stock worth
        total_stock_worth = (
            Stock.objects.aggregate(total=models.Sum('stock_quantity'))['total'] * stock1_price 
            # Stock2.objects.aggregate(total=models.Sum('stock_quantity'))['total'] * stock2_price +
            # Stock3.objects.aggregate(total=models.Sum('stock_quantity'))['total'] * stock3_price
        )
        
        user_bank_balance = User.objects.get(pk=request.user.pk).bank_balance
        
        total_amount = total_stock_worth + user_bank_balance
        
        return Response({'total_amount': total_amount})


from django.db.models import Sum, F
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()

class ForAllUpdateStockPricesView(APIView):
    permission_classes = [AllowAny]
    def get_net_balance(self, user, stock_price):
        total_stock_worth = (
            user.stock_set.aggregate(total=Sum(F('stock_quantity') * stock_price))['total'] or 0
        )
        user_bank_balance = user.bank_balance
    
        net_balance = total_stock_worth + user_bank_balance
        return net_balance

    def post(self, request):
        users = User.objects.all()
        stock_price = request.data.get('stock1_price', 0)
        user_net_balances = {}
        
        for user in users:
            user_net_balances[user.name] = self.get_net_balance(user, stock_price)
        
        sorted_users = sorted(user_net_balances.items(), key=lambda x: x[1], reverse=True)
        
        return Response(dict(sorted_users))



class GeoFensingChecking(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        if is_inside_geo_fence(request.data.get('latitude'),request.data.get('longitude'))== False:
            user = User.objects.get(pk=request.user.id)
            if user.warning ==2:
                return Response('Contact Administator')
            else:
                user.warning+=1
                user.save()
                return Response('You are not in the location')
        return Response(True)
            
class AdminRemoval(APIView):
    permission_classes = [IsAdminUser]
    def post(self,request):
        user = User.objects.get(phone_number=request.data.get('phone_number'))
        user.warning -=1
        user.block= False
        user.save()
        return Response('Updated Sucess Fully')

