from django.urls import path
from .views import (
    postDataFromPageCreate,
    postDataFromPageJoin,
    getRoomStatus,
    set_ready_status,
    start_game,
)

urlpatterns = [
    path("create/", postDataFromPageCreate),
    path("join/", postDataFromPageJoin),
    path("room-status/", getRoomStatus),
    path("set-ready/", set_ready_status),
    path("start_game/", start_game),
]
