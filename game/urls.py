from django.urls import path
from . import views

urlpatterns = [
    # ✅ Room Management
    path('create/', views.create_room, name='create_room'),
    path('join/', views.join_room, name='join_room'),
    path('room-status/', views.get_room_status, name='room_status'),  # ✅ Unified endpoint
    
    # ✅ Ready Status
    path('set-ready/', views.set_ready_status, name='set_ready'),
    path('reset-ready/', views.reset_ready, name='reset_ready'),
    
    # ✅ Game
    path('start_game/', views.start_game, name='start_game'),
    path('result/', views.result, name='result'),
    
    # ✅ Data Management
    path('reload-csv/', views.reload_csv, name='reload_csv'),
    path('delete-room/', views.delete_room, name='delete_room'),
    path('reset-room-images/', views.reset_room_images, name='reset_room_images'),
]