from django.urls import path
from .views import (
    StudentListCreateAPIView, StudentDetailAPIView,
    UniListCreateAPIView, UniDetailAPIView,
    HubListCreateAPIView, HubDetailAPIView,
    RideListCreateAPIView, RideDetailAPIView
)

urlpatterns = [
    path('students/', StudentListCreateAPIView.as_view()),
    path('students/<int:pk>/', StudentDetailAPIView.as_view()),

    path('unis/', UniListCreateAPIView.as_view()),
    path('unis/<int:pk>/', UniDetailAPIView.as_view()),

    path('hubs/', HubListCreateAPIView.as_view()),
    path('hubs/<int:pk>/', HubDetailAPIView.as_view()),

    path('rides/', RideListCreateAPIView.as_view()),
    path('rides/<int:pk>/', RideDetailAPIView.as_view()),
]