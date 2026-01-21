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

import random
from .models import Room, GameImage
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def start_game(request):
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

    # لو الصور اتحجزت قبل كده، رجّعها زي ما هي
    if room.player1_image and room.player2_image:
        return Response({
            "success": True,
            "category": room.category,
            "player1_image": room.player1_image,
            "player2_image": room.player2_image,
        })

    # نختار category عشوائي
    categories = GameImage.objects.values_list("category", flat=True).distinct()
    if not categories:
        return Response({
            "success": False,
            "message": "No categories found"
        }, status=400)

    category = random.choice(list(categories))

    images = GameImage.objects.filter(category=category)
    if images.count() < 2:
        return Response({
            "success": False,
            "message": "Not enough images in this category"
        }, status=400)

    selected = random.sample(list(images), 2)

    # نخزن في الغرفة
    room.category = category
    room.player1_image = selected[0].image_url
    room.player2_image = selected[1].image_url
    room.save()

    return Response({
        "success": True,
        "category": category,
        "player1_image": room.player1_image,
        "player2_image": room.player2_image,
    })
