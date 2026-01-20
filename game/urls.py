from django.urls import path
from .views import postDataFromPageCreate, postDataFromPageJoin, getRoomStatus

urlpatterns = [
    path("create/", postDataFromPageCreate, name="create"),
    path("join/", postDataFromPageJoin, name="join"),
    path("room-status/", getRoomStatus, name="room-status"),
]
