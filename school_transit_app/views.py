from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Uni, Hub, Ride
from .serializer import StudentSerializer, UniSerializer, UserLoginRequestSerializer, HubSerializer, RideSerializer, UniversityRequestSerializer, UserRequestSerializer, HubRequestSerializer, RequestRideRequestSerializer, StudentRequestSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import jwt
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema

load_dotenv()
token_key = os.getenv("token_secret_key")
algorithm_key = os.getenv("algorithm_type")
current_time = datetime.now(timezone.utc)


class AuthenticationView(APIView):
    serializer_class = UserSerializer

    """
    Authenticate users.
    """

    @swagger_auto_schema(
        request_body=UserLoginRequestSerializer,  # Document the request body
        operation_description="Authenticate a new user",
    )



    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            password = serializer.validated_data['password']
            email = serializer.validated_data['email']



            user = User.objects.filter(email=email).first()
            if not user:
                return Response({
                    'message': 'Invalid User',
                    'code': '03'
                }, status=status.HTTP_200_OK)

            if not user.check_password(password):
                return Response({
                    'message': 'Invalid password',
                    'code': '03'
                }, status=status.HTTP_200_OK)

            token_payload = {
                'id': user.id,
                # 'exp': datetime.now(timezone.utc) + timedelta(days=3),
                'iat': current_time,
            }
            token = jwt.encode(token_payload, token_key, algorithm=algorithm_key)

            serialize_data = self.serializer_class(user)
            return Response({
                'data': serialize_data.data,
                'token': token,
                'code': '00',
                'message': 'Login was successful'
            }, status=status.HTTP_200_OK)

        return Response({
            'message': serializer.errors,
            'code': '100'
        }, status=status.HTTP_400_BAD_REQUEST)
   
class UserView(APIView):
    serializer_class = UserSerializer

    """
    onboarding users.
    """

    @swagger_auto_schema(
        request_body=UserRequestSerializer,  # Document the request body
        operation_description="register a new user",
    )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        # Create the user
        if serializer.is_valid():  
            email = serializer.validated_data['email']

            try:
                existing_user1 = User.objects.filter(email=email).exists()

                if existing_user1:
                    return Response({'message': 'something went wrong, please contact support', 'code': '03'},status=status.HTTP_200_OK)
            
                serializer.save()

                user = User.objects.filter(email=email).first()
                token_payload = {
                            'id': user.id,
                            # 'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=60), #set session timeout for three days,
                            'iat': current_time,
                            ## secret decoder here for addtional layer security
                    }
                user.password = make_password(serializer.validated_data['password'])  # Hash the password
                user.save()

                token = jwt.encode(token_payload, token_key, algorithm=algorithm_key)
                data = {'data':serializer.data, 'token':token, 'code':'00', 'message':'Registration is successfull'}
                return Response(data, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'message': str(e), 'code': '01'})
        return Response({'message': serializer.errors, 'code': '100'})

  
    #return users
    def get(self, request):
        # token = request.META.get('HTTP_AUTHORIZATION')
        
        # if not token:
        #     return Response({'message': 'Authentication Failed', 'code': '01'})
        
        try:
            # decoded_token = jwt.decode(token, token_key, algorithms=[algorithm_key])
            # user = decoded_token['id']
            # print(user)
            users = User.objects.all()
            
            serializer = self.serializer_class(users, many=True)
            data = {'data':serializer.data, 'code':'00', 'message':'success'}
            return Response(data, status=status.HTTP_200_OK)
                
       
        except Exception as e:
            return Response({'message': str(e), 'code': '01'})




# ---- STUDENT CRUD ----
class StudentListCreateAPIView(APIView):
    """
    get all registered students.
    """

    @swagger_auto_schema(
        operation_description="list all students",
    )
    def get(self, request):
        students = User.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


    """
    Register a students.
    """

    @swagger_auto_schema(
        request_body=StudentRequestSerializer,  # Document the request body
        operation_description="regsiter a students",
    )
    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StudentDetailAPIView(APIView):
    """
    get students details.
    """
    serializer_class = StudentSerializer


    @swagger_auto_schema(
        operation_description="get a student details",
    )
    def get(self, request, pk):
        student = get_object_or_404(User, pk=pk)
        serializer = StudentSerializer(student)
        return Response(serializer.data)
    

    """
    update students details.
    """
    serializer_class = StudentSerializer


    @swagger_auto_schema(
        request_body=StudentRequestSerializer,  # Document the request body
       
        operation_description="update a student",
    )

    def put(self, request, pk):
        student = get_object_or_404(User, pk=pk)
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    """
    remove students.
    """
    serializer_class = StudentSerializer


    @swagger_auto_schema(
        operation_description="Authenticate a new user",
    )
    def delete(self, request, pk):
        student = get_object_or_404(User, pk=pk)
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- UNIVERSITY CRUD ----
class UniListCreateAPIView(APIView):
    """
    get all registered universities.
    """
    serializer_class = UniSerializer


    @swagger_auto_schema(
        operation_description="list all universities",
    )
    def get(self, request):
        unis = Uni.objects.all()
        serializer = UniSerializer(unis, many=True)
        return Response(serializer.data)

    """
    registered a university.
    """
    serializer_class = UniSerializer


    @swagger_auto_schema(
        request_body=UniversityRequestSerializer,  # Document the request body
        operation_description="Register a university",
    )
    def post(self, request):
        serializer = UniSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UniDetailAPIView(APIView):
    """
    get registered universities details.
    """
    serializer_class = UniSerializer


    @swagger_auto_schema(
        operation_description="get university details",
    )
    def get(self, request, pk):
        uni = get_object_or_404(Uni, pk=pk)
        serializer = UniSerializer(uni)
        return Response(serializer.data)


    """
    update registered universities details.
    """
    serializer_class = UniSerializer


    @swagger_auto_schema(
        request_body=UniversityRequestSerializer,  # Document the request body
        operation_description="update university details",
    )
    def put(self, request, pk):
        uni = get_object_or_404(Uni, pk=pk)
        serializer = UniSerializer(uni, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    """
    remove registered universities.
    """
    serializer_class = StudentSerializer


    @swagger_auto_schema(
        operation_description="reomve universities",
    )
    def delete(self, request, pk):
        uni = get_object_or_404(Uni, pk=pk)
        uni.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- HUB CRUD ----
class HubListCreateAPIView(APIView):
    """
    get all listed hubs.
    """
    serializer_class = HubSerializer


    @swagger_auto_schema(
        operation_description="get all listed hub(a)",
    )
    def get(self, request):
        hubs = Hub.objects.all()
        serializer = HubSerializer(hubs, many=True)
        return Response(serializer.data)

    """
    get all listed hubs.
    """
    serializer_class = HubSerializer


    @swagger_auto_schema(
        request_body=HubRequestSerializer,  # Document the request body
        operation_description="register a hub(a)",
    )
    def post(self, request):
        serializer = HubSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HubDetailAPIView(APIView):
    def get(self, request, pk):
        hub = get_object_or_404(Hub, pk=pk)
        serializer = HubSerializer(hub)
        return Response(serializer.data)

    """
    updated hubs.
    """
    serializer_class = HubSerializer


    @swagger_auto_schema(
        request_body=HubRequestSerializer,  # Document the request body
        operation_description="update a hub(a)",
    )
    def put(self, request, pk):
        hub = get_object_or_404(Hub, pk=pk)
        serializer = HubSerializer(hub, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        hub = get_object_or_404(Hub, pk=pk)
        hub.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- RIDE CRUD ----
class RideListCreateAPIView(APIView):
    def get(self, request):
        rides = Ride.objects.all()
        serializer = RideSerializer(rides, many=True)
        return Response(serializer.data)

    """
    request a ride.
    """
    serializer_class = RideSerializer


    @swagger_auto_schema(
        request_body=RequestRideRequestSerializer,  # Document the request body
        operation_description="request a hub(a)",
    )
    def post(self, request):
        serializer = RideSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RideDetailAPIView(APIView):
    def get(self, request, pk):
        ride = get_object_or_404(Ride, pk=pk)
        serializer = RideSerializer(ride)
        return Response(serializer.data)

    """
    update a ride.
    """
    serializer_class = RideSerializer


    @swagger_auto_schema(
        request_body=RequestRideRequestSerializer,  # Document the request body
        operation_description="update a ride",
    )
    def put(self, request, pk):
        ride = get_object_or_404(Ride, pk=pk)
        serializer = RideSerializer(ride, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ride = get_object_or_404(Ride, pk=pk)
        ride.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)