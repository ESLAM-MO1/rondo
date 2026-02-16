from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import random
import csv
import os
from datetime import datetime

# Database simulation
rooms = {}
used_images = {}

# CSV Path
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'images.csv')

# Store all images by theme
ALL_IMAGES = {
    'classic': [],
    'liar': [],
    'footBall': [],
}

def load_images_from_csv():
    """Load images from CSV file and categorize by theme"""
    global ALL_IMAGES
    
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                image_data = {
                    'name': row['name'],
                    'url': row['image_url'],
                    'category': row.get('category', 'image'),
                }
                
                if 'theme' in row:
                    theme = row['theme'].strip()
                    if theme in ALL_IMAGES:
                        ALL_IMAGES[theme].append(image_data)
                        print(f"   ✅ Added {row['name']} to {theme}")
                    else:
                        print(f"   ⚠️ Unknown theme '{theme}' for image {row['name']}")
                else:
                    total_images = sum(len(imgs) for imgs in ALL_IMAGES.values())
                    if total_images < 30:
                        ALL_IMAGES['classic'].append(image_data)
                    elif total_images < 60:
                        ALL_IMAGES['liar'].append(image_data)
                    else:
                        ALL_IMAGES['footBall'].append(image_data)
        
        print(f"\n✅ Loaded {sum(len(imgs) for imgs in ALL_IMAGES.values())} images from CSV")
        print(f"   - Classic: {len(ALL_IMAGES['classic'])} images")
        print(f"   - Liar: {len(ALL_IMAGES['liar'])} images")
        print(f"   - Football: {len(ALL_IMAGES['footBall'])} images\n")
        
    except FileNotFoundError:
        print(f"⚠️ CSV file not found at {CSV_FILE_PATH}")
        print("   Using fallback image data...")
        for theme in ALL_IMAGES.keys():
            for i in range(1, 13):
                ALL_IMAGES[theme].append({
                    'name': f'{theme}_img_{i:03d}',
                    'url': f'https://via.placeholder.com/400x400?text={theme}_{i}',
                    'category': 'image',
                })
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")

load_images_from_csv()


def get_random_theme_image(theme_id, room_code):
    """Get a random image for the theme that hasn't been used in this room yet"""
    if theme_id not in ALL_IMAGES or not ALL_IMAGES[theme_id]:
        print(f"❌ Theme '{theme_id}' not found or has no images")
        return None
    
    if room_code not in used_images:
        used_images[room_code] = {theme_id: []}
    elif theme_id not in used_images[room_code]:
        used_images[room_code][theme_id] = []
    
    used_names = used_images[room_code][theme_id]
    available_images = [
        img for img in ALL_IMAGES[theme_id] 
        if img['name'] not in used_names
    ]
    
    if not available_images:
        print(f"🔄 All {theme_id} images used in room {room_code}, resetting pool...")
        used_images[room_code][theme_id] = []
        available_images = ALL_IMAGES[theme_id]
    
    selected_image = random.choice(available_images)
    used_images[room_code][theme_id].append(selected_image['name'])
    
    print(f"🎲 Selected: {selected_image['name']} (theme: {theme_id}, room: {room_code})")
    
    return selected_image


@csrf_exempt
@require_http_methods(["POST"])
def create_room(request):
    """Create a new room with theme"""
    try:
        data = json.loads(request.body)
        room_code = data.get('key')
        player_name = data.get('name')
        theme_id = data.get('theme_id') or data.get('theme', 'classic')
        
        print(f"\n📝 CREATE ROOM:")
        print(f"   Room: {room_code}")
        print(f"   Player: {player_name}")
        print(f"   Theme: {theme_id}")
        
        if not room_code or not player_name:
            return JsonResponse({
                'success': False,
                'message': 'Missing room code or player name'
            }, status=400)
        
        if room_code in rooms:
            return JsonResponse({
                'success': False,
                'message': 'Room already exists'
            }, status=400)
        
        if theme_id not in ALL_IMAGES:
            return JsonResponse({
                'success': False,
                'message': f'Invalid theme: {theme_id}. Available: {list(ALL_IMAGES.keys())}'
            }, status=400)
        
        # ✅ Get TWO different images - one for each player
        player1_image = get_random_theme_image(theme_id, room_code)
        player2_image = get_random_theme_image(theme_id, room_code)  # ← صورة تانية!
        
        if not player1_image or not player2_image:
            return JsonResponse({
                'success': False,
                'message': f'Not enough images for theme: {theme_id}'
            }, status=500)
        
        # Create room with BOTH images
        rooms[room_code] = {
            'player1': player_name,
            'player2': None,
            'theme_id': theme_id,
            'player1_ready': False,
            'player2_ready': False,
            'player1_image': player1_image,  # ✅ صورة Player 1
            'player2_image': player2_image,  # ✅ صورة Player 2
            'created_at': datetime.now().isoformat(),
        }
        
        print(f"✅ Room {room_code} created:")
        print(f"   Player1 image: {player1_image['name']}")
        print(f"   Player2 image: {player2_image['name']}\n")
        
        return JsonResponse({
            'success': True,
            'message': 'Room created successfully',
            'room_code': room_code,
            'theme_id': theme_id,
            'player1_image': player1_image['name'],
            'player1_image_url': player1_image['url'],
        })
        
    except Exception as e:
        print(f"❌ Error creating room: {e}\n")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def join_room(request):
    """Join an existing room - must match theme"""
    try:
        data = json.loads(request.body)
        room_code = data.get('key')
        player_name = data.get('name')
        theme_id = data.get('theme_id') or data.get('theme', 'classic')
        
        print(f"\n📝 JOIN ROOM:")
        print(f"   Room: {room_code}")
        print(f"   Player: {player_name}")
        print(f"   Theme: {theme_id}")
        
        if not room_code or not player_name:
            return JsonResponse({
                'success': False,
                'message': 'Missing room code or player name'
            }, status=400)
        
        if room_code not in rooms:
            return JsonResponse({
                'success': False,
                'message': 'Room not found'
            }, status=404)
        
        room = rooms[room_code]
        
        if room['theme_id'] != theme_id:
            print(f"❌ Theme mismatch: room={room['theme_id']}, player={theme_id}\n")
            return JsonResponse({
                'success': False,
                'message': f'Theme mismatch! This room uses {room["theme_id"]} theme. Switch to {room["theme_id"]} to join.'
            }, status=403)
        
        if room['player2']:
            return JsonResponse({
                'success': False,
                'message': 'Room is full'
            }, status=400)
        
        room['player2'] = player_name
        room['player2_ready'] = False
        
        print(f"✅ Player joined room {room_code}\n")
        
        return JsonResponse({
            'success': True,
            'message': 'Joined room successfully',
            'player1': room['player1'],
            'player2': player_name,
            'theme_id': room['theme_id'],
            'player2_image': room['player2_image']['name'],   # ✅ صورة Player 2
            'player2_image_url': room['player2_image']['url'], # ✅ URL Player 2
        })
        
    except Exception as e:
        print(f"❌ Error joining room: {e}\n")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def set_ready_status(request):
    """Set player ready status"""
    try:
        data = json.loads(request.body)
        room_code = data.get('room_code') or data.get('key')
        player_name = data.get('player_name') or data.get('name')
        is_ready = data.get('is_ready') or data.get('ready', False)
        
        if room_code not in rooms:
            return JsonResponse({
                'success': False,
                'message': 'Room not found'
            }, status=404)
        
        room = rooms[room_code]
        
        if room['player1'] == player_name:
            room['player1_ready'] = is_ready
        elif room['player2'] == player_name:
            room['player2_ready'] = is_ready
        else:
            return JsonResponse({
                'success': False,
                'message': 'Player not in room'
            }, status=400)
        
        both_ready = room['player1_ready'] and room['player2_ready'] and room['player2'] is not None
        
        return JsonResponse({
            'success': True,
            'player1_ready': room['player1_ready'],
            'player2_ready': room['player2_ready'],
            'both_ready': both_ready,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_room_status(request):
    """Unified room status endpoint"""
    try:
        room_code = request.GET.get('key') or request.GET.get('room_code')
        
        if not room_code or room_code not in rooms:
            return JsonResponse({
                'success': False,
                'message': 'Room not found'
            }, status=404)
        
        room = rooms[room_code]
        both_ready = room['player1_ready'] and room['player2_ready'] and room['player2'] is not None
        
        return JsonResponse({
            'success': True,
            'player1': room['player1'],
            'player2': room['player2'] or '',
            'player1_ready': room['player1_ready'],
            'player2_ready': room['player2_ready'],
            'both_ready': both_ready,
            'ready': both_ready,
            'player1_image': room['player1_image']['name'],       # ✅ صورة Player 1
            'player1_image_url': room['player1_image']['url'],
            'player2_image': room['player2_image']['name'],       # ✅ صورة Player 2
            'player2_image_url': room['player2_image']['url'],
            'theme_id': room['theme_id'],
            'theme': room['theme_id'],
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def start_game(request):
    """Get game image - returns the appropriate image for each player"""
    try:
        room_code = request.GET.get('key')
        
        if not room_code or room_code not in rooms:
            return JsonResponse({
                'success': False,
                'message': 'Room not found'
            }, status=404)
        
        room = rooms[room_code]
        
        if not (room['player1_ready'] and room['player2_ready'] and room['player2']):
            return JsonResponse({
                'success': False,
                'message': 'Both players must be ready'
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'category': 'image',
            'player1_image': room['player1_image']['url'],  # ✅ URL Player 1
            'player2_image': room['player2_image']['url'],  # ✅ URL Player 2
            'image': room['player1_image']['url'],  # backward compatibility
            'theme_id': room['theme_id'],
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reset_ready(request):
    """Reset ready status and get NEW images for next round"""
    try:
        data = json.loads(request.body)
        room_code = data.get('room_code') or data.get('key')
        
        if room_code not in rooms:
            return JsonResponse({
                'success': False,
                'message': 'Room not found'
            }, status=404)
        
        room = rooms[room_code]
        room['player1_ready'] = False
        room['player2_ready'] = False
        
        # ✅ Get TWO NEW different images
        new_player1_image = get_random_theme_image(room['theme_id'], room_code)
        new_player2_image = get_random_theme_image(room['theme_id'], room_code)
        
        if new_player1_image and new_player2_image:
            room['player1_image'] = new_player1_image
            room['player2_image'] = new_player2_image
            
        print(f"🔄 Reset ready for room {room_code}:")
        print(f"   New Player1 image: {new_player1_image['name'] if new_player1_image else 'none'}")
        print(f"   New Player2 image: {new_player2_image['name'] if new_player2_image else 'none'}\n")
        
        return JsonResponse({
            'success': True,
            'message': 'Ready status reset',
            'player1_ready': False,
            'player2_ready': False,
            'both_ready': False,
            'images_cleared': True,
            'new_image': new_player1_image['url'] if new_player1_image else None,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def result(request):
    """Game result endpoint"""
    try:
        room_code = request.GET.get('key')
        
        if not room_code or room_code not in rooms:
            return JsonResponse({
                'success': False,
                'message': 'Room not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'message': 'Game completed'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reset_room_images(request):
    """Reset used images pool"""
    try:
        data = json.loads(request.body)
        room_code = data.get('room_code')
        
        if room_code in used_images:
            used_images[room_code] = {}
            print(f"🔄 Reset image pool for room {room_code}\n")
        
        return JsonResponse({
            'success': True,
            'message': 'Room images reset'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_room(request):
    """Delete a room"""
    try:
        data = json.loads(request.body)
        room_code = data.get('room_code')
        
        if room_code in rooms:
            del rooms[room_code]
            print(f"🗑 Deleted room {room_code}\n")
        
        if room_code in used_images:
            del used_images[room_code]
        
        return JsonResponse({
            'success': True,
            'message': 'Room deleted'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reload_csv(request):
    """Reload images from CSV"""
    try:
        global ALL_IMAGES
        ALL_IMAGES = {
            'classic': [],
            'liar': [],
            'footBall': [],
        }
        load_images_from_csv()
        
        return JsonResponse({
            'success': True,
            'message': 'CSV reloaded successfully',
            'total_images': sum(len(imgs) for imgs in ALL_IMAGES.values()),
            'classic': len(ALL_IMAGES['classic']),
            'liar': len(ALL_IMAGES['liar']),
            'footBall': len(ALL_IMAGES['footBall']),
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)