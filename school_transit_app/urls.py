from django.urls import path
from .views import (
    StudentListCreateAPIView, StudentDetailAPIView,
    UniListCreateAPIView, UniDetailAPIView,
    HubListCreateAPIView, HubDetailAPIView,
    RideListCreateAPIView, RideDetailAPIView,
    AuthenticationView, UserView, LocationDetailAPIView, RideDetailByUniIdAPIView
)

urlpatterns = [
    path('login/', AuthenticationView.as_view()),
    path('register/', UserView.as_view()),


    path('students/', StudentListCreateAPIView.as_view()),
    path('students/<int:pk>/', StudentDetailAPIView.as_view()),

    path('unis/', UniListCreateAPIView.as_view()),
    path('unis/<int:pk>/', UniDetailAPIView.as_view()),

    path('hubs/', HubListCreateAPIView.as_view()),
    path('hubs/<int:pk>/', HubDetailAPIView.as_view()),

    path('rides/', RideListCreateAPIView.as_view()),
    path('rides/<int:pk>/', RideDetailAPIView.as_view()),
    path('rides/uni/<int:id>/', RideDetailByUniIdAPIView.as_view()),


    path('locations/<int:pk>/', LocationDetailAPIView.as_view()),
]