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


# Room Status (Waiting Room)
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

    ready = room.player2 is not None and room.player2 != ""

    return Response({
        "success": True,
        "player1": room.player1,
        "player2": room.player2,
        "ready": ready
    })
