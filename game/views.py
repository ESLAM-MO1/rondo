from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Room


# Create Room
@api_view(["POST"])
def postDataFromPageCreate(request):
    name = request.data.get("name")
    key = request.data.get("key")

    if not name or not key:
        return Response({
            "success": False,
            "message": "name and key are required"
        }, status=400)

    if Room.objects.filter(key=key).exists():
        return Response({
            "success": False,
            "message": "Room already exists"
        }, status=400)

    Room.objects.create(
        key=key,
        player1=name
    )

    return Response({
        "success": True,
        "message": "Room created successfully",
        "player2": None,   # لسه مستني Player2
        "key": key
    })


# Join Room
@api_view(["POST"])
def postDataFromPageJoin(request):
    name = request.data.get("name")
    key = request.data.get("key")

    if not name or not key:
        return Response({
            "success": False,
            "message": "name and key are required"
        }, status=400)

    try:
        room = Room.objects.get(key=key)
    except Room.DoesNotExist:
        return Response({
            "success": False,
            "message": "Code is incorrect"
        }, status=404)

    if room.player2:
        return Response({
            "success": False,
            "message": "Room is full"
        }, status=400)

    room.player2 = name
    room.save()

    return Response({
        "success": True,
        "message": "Joined successfully",
        "player1": room.player1,  # اسم الخصم
        "key": key
    })

@api_view(["GET"])
def getRoomStatus(request):
    key = request.GET.get("key")

    if not key:
        return Response({
            "success": False,
            "message": "Room key is required"
        }, status=400)

    try:
        room = Room.objects.get(key=key)
    except Room.DoesNotExist:
        return Response({
            "success": False,
            "message": "Room not found"
        }, status=404)

    ready = room.player2 not in [None, ""]

    both_ready = room.player1_ready and room.player2_ready

    return Response({
        "success": True,
        "player1": room.player1,
        "player2": room.player2,
        "ready": ready,
        "player1_ready": room.player1_ready,
        "player2_ready": room.player2_ready,
        "both_ready": both_ready
    })

@api_view(["POST"])
def set_ready_status(request):
    key = request.data.get("key")
    name = request.data.get("name")
    ready = request.data.get("ready")

    if key is None or name is None or ready is None:
        return Response({
            "success": False,
            "message": "key, name and ready are required"
        }, status=400)

    try:
        room = Room.objects.get(key=key)
    except Room.DoesNotExist:
        return Response({
            "success": False,
            "message": "Room not found"
        }, status=404)

    # تحديد مين اللاعب اللي بيبعت
    if room.player1 == name:
        room.player1_ready = bool(ready)
    elif room.player2 == name:
        room.player2_ready = bool(ready)
    else:
        return Response({
            "success": False,
            "message": "Player not found in this room"
        }, status=400)

    room.save()

    both_ready = room.player1_ready and room.player2_ready

    return Response({
        "success": True,
        "message": "Ready status updated",
        "player1_ready": room.player1_ready,
        "player2_ready": room.player2_ready,
        "both_ready": both_ready
    })



import random
from .models import GameImage

@api_view(["GET"])
def start_game(request):
    category = request.GET.get("category")

    if not category:
        return Response({
            "success": False,
            "message": "Category is required"
        }, status=400)

    images = GameImage.objects.filter(category=category)

    if images.count() < 2:
        return Response({
            "success": False,
            "message": "Not enough images in this category"
        }, status=400)

    selected = random.sample(list(images), 2)

    return Response({
        "success": True,
        "player1_image": selected[0].image_url,
        "player2_image": selected[1].image_url,
        "category": category
    })
