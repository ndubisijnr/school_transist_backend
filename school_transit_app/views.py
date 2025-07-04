from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Uni, Hub, Ride, Student, Location
from .serializer import StudentSerializer, UniSerializer, UserLoginSerializer, LocationRequestSerializer, LocationSerializer, UserLoginRequestSerializer, HubSerializer, RideSerializer, UniversityRequestSerializer, UserRequestSerializer, HubRequestSerializer, RequestRideRequestSerializer, StudentRequestSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import jwt
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from get_user_token import  get_user_HTTP_Auth_token
from django.http import JsonResponse

load_dotenv()
token_key = os.getenv("token_secret_key")
algorithm_key = os.getenv("algorithm_type")
current_time = datetime.now(timezone.utc)


def validate_token(request):
    token = get_user_HTTP_Auth_token(request)
    if not token:
        return Response({},status=status.HTTP_401_UNAUTHORIZED)
    decoded_token = jwt.decode(token, token_key, algorithms=[algorithm_key])
    user = User.objects.get(id=decoded_token['id'])
    return user


class AuthenticationView(APIView):
    serializer_class = UserLoginSerializer

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

            serialize_data = UserSerializer(user)
            student = Student.objects.filter(user_id=user.id).first()
            hub = Hub.objects.filter(user_id=user.id).first()
            uni = None
            driver_uni = None
            if student is not None:
                uni = UniSerializer(Uni.objects.filter(id=student.uni_id).first()).data
            if hub is not None:
                driver_uni = UniSerializer(Uni.objects.filter(id=hub.uni_id).first()).data

            return Response({
                'data': {'user':serialize_data.data,
                         'student': StudentSerializer(student).data if student else None,
                         'uni':uni,
                         'driver_uni':driver_uni,
                         'hub':HubSerializer(hub).data if hub else None
                         },
                
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

        if validate_token(request):
            students = Student.objects.all()
            serializer = StudentSerializer(students, many=True)
            return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_200_OK)
        return Response({},status=status.HTTP_400_BAD_REQUEST)


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
            if validate_token(request):
                serializer.save()
                return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_201_CREATED)
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
        if validate_token(request):
            student = get_object_or_404(Student, pk=pk)
            serializer = StudentSerializer(student)
            return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_200_OK)
    

    """
    update students details.
    """
    serializer_class = StudentSerializer


    @swagger_auto_schema(
        request_body=StudentRequestSerializer,  # Document the request body
       
        operation_description="update a student",
    )

    def put(self, request, pk):
        if validate_token(request):
            student = get_object_or_404(Student, pk=pk)
            serializer = StudentSerializer(student, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'code':'01', 'message':'something went wrong', 'data':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    """
    remove students.
    """
    serializer_class = StudentSerializer


    @swagger_auto_schema(
        operation_description="Authenticate a new user",
    )
    def delete(self, request, pk):
        if validate_token(request):
            student = get_object_or_404(Student, pk=pk)
            student.delete()
            return Response({'code':'00', 'message':'success'}, status=status.HTTP_200_OK)

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
        if validate_token(request):
            unis = Uni.objects.all()
            serializer = UniSerializer(unis, many=True)
            return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_200_OK)
    """
    registered a university.
    """
    serializer_class = UniSerializer


    @swagger_auto_schema(
        request_body=UniversityRequestSerializer,  # Document the request body
        operation_description="Register a university",
    )
    def post(self, request):
        if validate_token(request):
            serializer = UniSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'code':'01', 'message':'something went wrong', 'data':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UniDetailAPIView(APIView):
    """
    get registered universities details.
    """
    serializer_class = UniSerializer


    @swagger_auto_schema(
        operation_description="get university details",
    )
    def get(self, request, pk):
        if validate_token(request):
            uni = get_object_or_404(Uni, pk=pk)
            serializer = UniSerializer(uni)
            return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_200_OK)


    """
    update registered universities details.
    """
    serializer_class = UniSerializer


    @swagger_auto_schema(
        request_body=UniversityRequestSerializer,  # Document the request body
        operation_description="update university details",
    )
    def put(self, request, pk):
        if validate_token(request):
            uni = get_object_or_404(Uni, pk=pk)
            serializer = UniSerializer(uni, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'code':'01', 'message':'something went wrong', 'data':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    """
    remove registered universities.
    """
    serializer_class = StudentSerializer


    @swagger_auto_schema(
        operation_description="reomve universities",
    )
    def delete(self, request, pk):
        if validate_token(request):
            uni = get_object_or_404(Uni, pk=pk)
            uni.delete()
            return Response({'code':'00', 'message':'success'},status=status.HTTP_200_OK)


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
        if validate_token(request):
            hubs = Hub.objects.all()
            serializer = HubSerializer(hubs, many=True)
            return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_200_OK)


    """
    get all listed hubs.
    """
    serializer_class = HubSerializer


    @swagger_auto_schema(
        request_body=HubRequestSerializer,  # Document the request body
        operation_description="register a hub(a)",
    )
    def post(self, request):
        if validate_token(request):
            serializer = HubSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'code':'01', 'message':'something went wrong', 'data':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class HubDetailAPIView(APIView):
    
    def get(self, request, pk):
        if validate_token(request):
            hub = get_object_or_404(Hub, pk=pk)
            serializer = HubSerializer(hub)
            return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_200_OK)

    """
    updated hubs.
    """
    serializer_class = HubSerializer


    @swagger_auto_schema(
        request_body=HubRequestSerializer,  # Document the request body
        operation_description="update a hub(a)",
    )
    def put(self, request, pk):
        if validate_token(request):
            hub = get_object_or_404(Hub, pk=pk)
            serializer = HubSerializer(hub, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'code':'01', 'message':'something went wrong', 'data':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if validate_token(request):
            hub = get_object_or_404(Hub, pk=pk)
            hub.delete()
            return Response({'code':'00', 'message':'success'},status=status.HTTP_200_OK)


# ---- LOCATION CRUD ----

class LocationDetailAPIView(APIView):
    
    def get(self, request, pk):
        if validate_token(request):
            location = Location.objects.filter(uni=pk)
            serializer = LocationSerializer(location, many=True)
            return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_200_OK)

    """
    updated hubs.
    """
    serializer_class = LocationSerializer


    @swagger_auto_schema(
        request_body=LocationRequestSerializer,  # Document the request body
        operation_description="update a hub(a)",
    )
    def put(self, request, pk):
        if validate_token(request):
            location = get_object_or_404(Location, pk=pk)
            serializer = Location(location, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'code':'01', 'message':'something went wrong', 'data':serializer.error}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if validate_token(request):
            location = get_object_or_404(Location, pk=pk)
            location.delete()
            return Response({'code':'00', 'message':'success'},status=status.HTTP_200_OK)

# ---- RIDE CRUD ----
class RideListCreateAPIView(APIView):
    from .models import Ride, Student, Hub  # Ensure you import Hub

    def get(self, request):
        if validate_token(request):
            rides = Ride.objects.all()
            serializer = RideSerializer(rides, many=True)

            ride_list = []
            for ride_data in serializer.data:
                student_id = ride_data['student']
                hub_id = ride_data.get('hub')  # Use .get to avoid KeyError

                try:
                    student = Student.objects.get(id=student_id)
                except Student.DoesNotExist:
                    continue  # Skip this ride if student doesn't exist

                # Prepare student data
                student_data = {
                    'id': student.id,
                    'name': student.full_name,
                }

                # Try to fetch hub data if hub_id exists
                hub_data = None
                if hub_id:
                    try:
                        hub = Hub.objects.get(id=hub_id)
                        hub_data = {
                            'id': hub.id,
                            'name': hub.driver_fullname,
                            'vehicle_type': hub.driver_vehicle_type,
                            'vehicle_name': hub.driver_vehicle_name,
                            'vehicle_color': hub.driver_vehicle_color,
                            'vehicle_capacity': hub.driver_vehicle_capacity,
                            'vehicle_verified': hub.driver_is_verified,
                            'gender': hub.driver_gender,
                        }
                    except Hub.DoesNotExist:
                        pass  # hub_data stays None

                # Build the final ride dictionary
                ride_data = dict(ride_data)
                ride_data['student'] = student_data
                ride_data['hub'] = hub_data  # This can be None

                ride_list.append(ride_data)

            return Response({'code': '00', 'message': 'success', 'data': ride_list}, status=status.HTTP_200_OK)

    """
    request a ride.
    """
    serializer_class = RideSerializer


    @swagger_auto_schema(
        request_body=RequestRideRequestSerializer,  # Document the request body
        operation_description="request a hub(a)",
    )
    def post(self, request):
        if validate_token(request):
            serializer = RequestRideRequestSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                response_serializer = RideSerializer(instance)
                return Response({'code':'00', 'message':'success', 'data':response_serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'code':'01', 'message':'something went wrong', 'data':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RideDetailAPIView(APIView):
    def get(self, request, pk):
        if validate_token(request):
            ride = get_object_or_404(Ride, pk=pk)
            serializer = RideSerializer(ride)

            student_id = serializer.data.get('student')
            hub_id = serializer.data.get('hub')  # Corrected .get usage

            # Fetch student info
            try:
                student = Student.objects.get(id=student_id)
                student_data = {
                    'id': student.id,
                    'name': student.full_name,
                }
            except Student.DoesNotExist:
                return Response({'code': '01', 'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

            # Try to fetch hub info
            hub_data = None
            if hub_id:
                try:
                    hub = Hub.objects.get(id=hub_id)
                    hub_data = {
                        'id': hub.id,
                        'name': hub.driver_fullname,
                        'vehicle_type': hub.driver_vehicle_type,
                        'vehicle_name': hub.driver_vehicle_name,
                        'vehicle_color': hub.driver_vehicle_color,
                        'vehicle_capacity': hub.driver_vehicle_capacity,
                        'vehicle_verified': hub.driver_is_verified,
                        'gender': hub.driver_gender,
                    }
                except Hub.DoesNotExist:
                    pass  # hub_data stays None

            # Final ride data
            ride_data = serializer.data.copy()
            ride_data['student'] = student_data
            ride_data['hub'] = hub_data  # can be None

            return Response({'code': '00', 'message': 'success', 'data': ride_data}, status=status.HTTP_200_OK)

    """
    update a ride.
    """
    serializer_class = RideSerializer


    @swagger_auto_schema(
        request_body=RequestRideRequestSerializer,  # Document the request body
        operation_description="update a ride",
    )
    def put(self, request, pk):
        if validate_token(request):
            ride = get_object_or_404(Ride, pk=pk)
            serializer = RideSerializer(ride, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'code':'00', 'message':'success', 'data':serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'code':'01', 'message':'something went wrong', 'data':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if validate_token(request):
            ride = get_object_or_404(Ride, pk=pk)
            ride.delete()
            return Response({'code':'00', 'message':'success'}, status=status.HTTP_200_OK)
        

class RideDetailByStudentIdAPIView(APIView):
    def get(self, request, id):
        if validate_token(request):
            ride_by_uni = Ride.objects.filter(student=id)
            serializer = RideSerializer(ride_by_uni, many=True)

            ride_list = []
            for ride_data in serializer.data:
                student_id = ride_data['student']
                hub_id = ride_data.get('hub')  # Use .get to avoid KeyError

                try:
                    student = Student.objects.get(id=student_id)
                except Student.DoesNotExist:
                    continue  # Skip this ride if student doesn't exist

                # Prepare student data
                student_data = {
                    'id': student.id,
                    'name': student.full_name,
                }

                # Try to fetch hub data if hub_id exists
                hub_data = None
                if hub_id:
                    try:
                        hub = Hub.objects.get(id=hub_id)
                        hub_data = {
                            'id': hub.id,
                            'name': hub.driver_fullname,
                            'vehicle_type': hub.driver_vehicle_type,
                            'vehicle_name': hub.driver_vehicle_name,
                            'vehicle_color': hub.driver_vehicle_color,
                            'vehicle_capacity': hub.driver_vehicle_capacity,
                            'vehicle_verified': hub.driver_is_verified,
                            'gender': hub.driver_gender,
                        }
                    except Hub.DoesNotExist:
                        pass  # hub_data stays None

                # Build the final ride dictionary
                ride_data = dict(ride_data)
                ride_data['student'] = student_data
                ride_data['hub'] = hub_data  # This can be None

                ride_list.append(ride_data)

            return Response({'code': '00', 'message': 'success', 'data': ride_list}, status=status.HTTP_200_OK)

class RideDetailByHubIdAPIView(APIView):
    def get(self, request, id):
        if validate_token(request):
            ride_by_uni = Ride.objects.filter(hid=id)
            serializer = RideSerializer(ride_by_uni, many=True)

            ride_list = []
            for ride_data in serializer.data:
                student_id = ride_data['student']
                hub_id = ride_data.get('hub')  # Use .get to avoid KeyError

                try:
                    student = Student.objects.get(id=student_id)
                except Student.DoesNotExist:
                    continue  # Skip this ride if student doesn't exist

                # Prepare student data
                student_data = {
                    'id': student.id,
                    'name': student.full_name,
                }

                # Try to fetch hub data if hub_id exists
                hub_data = None
                if hub_id:
                    try:
                        hub = Hub.objects.get(id=hub_id)
                        hub_data = {
                            'id': hub.id,
                            'name': hub.driver_fullname,
                            'vehicle_type': hub.driver_vehicle_type,
                            'vehicle_name': hub.driver_vehicle_name,
                            'vehicle_color': hub.driver_vehicle_color,
                            'vehicle_capacity': hub.driver_vehicle_capacity,
                            'vehicle_verified': hub.driver_is_verified,
                            'gender': hub.driver_gender,
                        }
                    except Hub.DoesNotExist:
                        pass  # hub_data stays None

                # Build the final ride dictionary
                ride_data = dict(ride_data)
                ride_data['student'] = student_data
                ride_data['hub'] = hub_data  # This can be None

                ride_list.append(ride_data)

            return Response({'code': '00', 'message': 'success', 'data': ride_list}, status=status.HTTP_200_OK)