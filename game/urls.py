from django.urls import path
from .views import postDataFromPageCreate, postDataFromPageJoin, getRoomStatus, set_ready_status,  getRoomStatus

urlpatterns = [
    path("create/", postDataFromPageCreate, name="create"),
    path("join/", postDataFromPageJoin, name="join"),
    path("set-ready/", set_ready_status, name="set-ready"),
    path("room-status/", getRoomStatus, name="room-status"),

]
