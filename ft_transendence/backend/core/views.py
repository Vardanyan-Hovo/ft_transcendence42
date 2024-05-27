from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Confirm, Person, GameRoom, History
from game.views import PlayTournament, LiveGames
from .serializers import (
    UserSerializer,
    SettingsSerializer,
    HomeSerializer,
    LeaderboardSerializer,
    ProfileSerializer,
    WaitingRoomSerializer,
    HistorySerializer,
    OpponentHistorySerializer,
    FullHistorySerializer,
    GameRoomSerializer,
    MatchSerializer
)
from .validations import (
    email_validation,
    register_validation,
    send_confirmation_email,
    password_validation
)

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.utils import timezone

from collections import defaultdict
from asgiref.sync import async_to_sync, sync_to_async

import json
import time
import base64
import os

class UserAPIView(APIView):
    def get(self, request):
        queryset = Person.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

class PersonsAPIView(APIView):
    def get(self, request, pk):
        user = Person.objects.get(id=pk)
        if user:
            try:
                serializer = UserSerializer(user)
                return JsonResponse(serializer.data)
            except Person.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        else:
            return JsonResponse({'error': 'User ID not provided'}, status=400)

class EmailValidation(APIView):
    def post(self, request):
        email = request.data['email'].strip()
        try:
            email_validation(email)
            code = send_confirmation_email(email)
        except ValidationError as e:
            return JsonResponse({"success": "false","error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        try:
            existing_confirmation_data = Confirm.objects.get(email=email)
            existing_confirmation_data.delete()
        except ObjectDoesNotExist:
            pass
        confirmation_data = Confirm.objects.create(email=email, code=code)
        return JsonResponse({"success": "true", "email": "model_to_dict(data)"})

class Confirmation(APIView):
    def post(self, request):
        confirm_front = request.data['code']
        if not confirm_front:
            return JsonResponse({"success": "false", "error": "Confirmation code not found"}, status=status.HTTP_400_BAD_REQUEST)
        email = request.data['email']
        try:
            confirmation_data = Confirm.objects.filter(email=email).latest('timestamp')
            if not confirmation_data:
                return JsonResponse({"success": "false", "error": "Confirmation data not found"}, status=status.HTTP_400_BAD_REQUEST)
            expiration_time = confirmation_data.timestamp + timezone.timedelta(seconds=35)
            if timezone.now() > expiration_time:
                confirmation_data.delete()
                return JsonResponse({"success": "false","error": "Confirmation code expired"}, status=status.HTTP_408_REQUEST_TIMEOUT)
            if confirm_front != confirmation_data.code:
                return JsonResponse({"success": "false","error": "Invalid confirmation code"}, status=status.HTTP_404_NOT_FOUND)
        except Confirm.DoesNotExist:
            return JsonResponse({"success": "false","error": "Confirmation data not found"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            person = Person.objects.get(email=email)
            if person.twofactor is True:
                token_serializer = TokenObtainPairSerializer()
                token = token_serializer.get_token(user)
                refresh = RefreshToken.for_user(user)

                response_data = {
                    "success": "true",
                    "access": str(token.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": person.id,
                        "name": person.name,
                        "nickname": person.nickname,
                        "email": person.email,
                        "image": person.image,
                    }
                }
                return JsonResponse({"success": "true", "twoFA": "true", "data": response_data})
        except User.DoesNotExist:
            pass
        except Person.DoesNotExist:
            pass
        return JsonResponse({"success": "true", "message": "Email is validated"})

class Register(APIView):
    def post(self, request):
        email = request.data['email']
        nickname = request.data['nickname']
        try:
            confirmation_data = Confirm.objects.get(email=email)
            register_validation(request.data)
            password = request.data['password'][10:-10]
            hashed_password = make_password(password)
            user = get_user_model().objects.create(
                email=email,
                first_name=request.data['name'],
                username=nickname,
                password=hashed_password,
            )
            data = Person.objects.create(
                user=user,
                email=email,
                name=request.data['name'],
                nickname=nickname,
                password=hashed_password,
            )
            data.save_base64_image(image_path=os.path.join(os.path.dirname(__file__), 'default.jpg'))
            data.save_base64_background(background_path=os.path.join(os.path.dirname(__file__), 'background.jpg'))
            data_to_send = {'email': email, 'nickname': request.data['nickname'], 'name': request.data['name']}
            confirmation_data.delete()
            return JsonResponse({"success": "true", "reg": data_to_send})
        except Confirm.DoesNotExist:
            return JsonResponse({"success": "false","error": "Email is not validated"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            if e.code == 'nickname_exists':
                return Response({"error": "Nickname already exists"}, status=status.HTTP_409_CONFLICT)
            else:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PasswordReset(APIView):
    def post(self, request):
        email = request.data['email'].strip()
        try:
            if not email:
                raise ValidationError('Waiting for an email address') 
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError('Invalid email format')
            code = send_confirmation_email(email)
        except ValidationError as e:
            return JsonResponse({"success": "false","error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        confirm_data = {
            'email': email,
            'code': code,
            'timestamp': timezone.now().isoformat(),
        }
        confirmation_data = Confirm.objects.create(email=email, code=code)
        return JsonResponse({"success": "true", "email": "model_to_dict(data)"})

class ForgetConfirmation(APIView):
    def post(self, request):
        confirm_front = request.data['code']
        if not confirm_front:
            return JsonResponse({"success": "false", "error": "Confirmation code not found"}, status=status.HTTP_400_BAD_REQUEST)
        email = request.data['email']
        try:
            confirmation_data = Confirm.objects.filter(email=email).latest('timestamp')       
            if not confirmation_data:
                return JsonResponse({"success": "false", "error": "Confirmation data not found"}, status=status.HTTP_400_BAD_REQUEST)
            expiration_time = confirmation_data.timestamp + timezone.timedelta(seconds=35)
            if timezone.now() > expiration_time:
                confirmation_data.delete()
                return JsonResponse({"success": "false", "error": "Confirmation code expired"}, status=status.HTTP_408_REQUEST_TIMEOUT)
            if confirm_front != confirmation_data.code:
                return JsonResponse({"success": "false", "error": "Invalid confirmation code"}, status=status.HTTP_404_NOT_FOUND)
        except Confirm.DoesNotExist:
            return JsonResponse({"success": "false","error": "Confirmation data not found"}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({"success": "true", "message": "Email is validated"})

class Password(APIView):
    def post(self, request):
        email = request.data['email']
        confirmation_data = Confirm.objects.get(email=email)
        if not confirmation_data:
            return JsonResponse({"success": "false", "error": "Confirmation data not found"}, status=status.HTTP_400_BAD_REQUEST)
        data_email = confirmation_data.email
        confirmation_data.delete()
        if email != data_email:
            return JsonResponse({"success": "false", "error": "Email is not validated"}, status=status.HTTP_400_BAD_REQUEST)
        password = request.data['password'][10:-10]
        try:
            password = password_validation(password)
            try:
                person = Person.objects.get(email=email)
            except Person.DoesNotExist:
                return JsonResponse({"success": "false", "error": "Person not found"}, status=status.HTTP_404_NOT_FOUND)
            try:
                validate_password(password)
            except ValidationError as e:
                return JsonResponse({"success": "false", "error": e.message}, status=status.HTTP_400_BAD_REQUEST)
            hashed_password = make_password(password)
            person.password = hashed_password
            person.save()
            return JsonResponse({"success": "true", "message": "Password successfully updated"})
        except ValidationError as e:
            return JsonResponse({"success": "false", "error": e.message}, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password'][10:-10]
        try:
            user = User.objects.get(email=email)
            person = Person.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"success": "false", "error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        if check_password(password, person.password):
            gameroom = person.game_room
            if gameroom and gameroom.creator_id == person.id:
                for player in gameroom.players.all():
                    player.ongoing = False
                    player.game_room_id = None
                    player.save()
                gameroom.players.clear()
                gameroom.delete()
            elif gameroom and gameroom.creator_id != person.id:
                gameroom.players.remove(person)
                person.ongoing = False
                person.game_room_id = None
            person.game_room = None
            person.is_online = True
            person.save()
            token_serializer = TokenObtainPairSerializer()
            token = token_serializer.get_token(user)
            refresh = RefreshToken.for_user(user)

            response_data = {
                "success": "true",
                "access": str(token.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": person.id,
                    "name": person.name,
                    "nickname": person.nickname,
                    "email": person.email,
                    "image": person.image,
                    "wins": person.wins,
                    "loses": person.loses,
                }
            }
            if person.twofactor is True:
                code = send_confirmation_email(email)
                confirm_data = {
                    'email': email,
                    'code': code,
                    'timestamp': timezone.now().isoformat(),
                }
                try:
                    existing_confirmation_data = Confirm.objects.get(email=email)
                    existing_confirmation_data.delete()
                except ObjectDoesNotExist:
                    pass
                confirmation_data = Confirm.objects.create(email=email, code=code)
                return JsonResponse({"twoFA": "true"})
            return JsonResponse({"success": "true", "data": response_data})
        else:
            return JsonResponse({"success": "false", "error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class Logout(APIView):
    def post(self, request, pk):
        try:
            person = Person.objects.get(id=pk)
        except Person.DoesNotExist:
            return JsonResponse({"success": "false", "error": "Person not found"}, status=status.HTTP_404_NOT_FOUND)
        gameroom = person.game_room
        if gameroom and gameroom.creator_id == person.id:
            for player in gameroom.players.all():
                player.ongoing = False
                player.game_room_id = None
                player.save()
            gameroom.players.clear()
            gameroom.delete()
        elif gameroom and gameroom.creator_id != person.id:
            gameroom.players.remove(person)
            person.ongoing = False
            person.game_room_id = None
        person.is_online = False
        person.game_room = None
        person.save()
        token = request.data['refresh']
        try:
            refresh = RefreshToken(token)
            refresh.blacklist()
        except TokenError:
            return JsonResponse({"success": "false", "error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": "true", "message": "Logged out successfully"}, status=status.HTTP_200_OK)

class Profile(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            user = Person.objects.get(id=pk)
            serializer = ProfileSerializer(user)
        except Person.DoesNotExist:
            return JsonResponse({"success": "false", "error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse({"success": "true", "profile": serializer.data}, safe=False)

class SettingsById(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            user = Person.objects.get(id=pk)
            serializer = SettingsSerializer(user)
            return JsonResponse({"success": "true", "profile": serializer.data}, safe=False)
        except Person.DoesNotExist:
            return JsonResponse({"success": "false", "error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            person = Person.objects.get(pk=pk)
            user = User.objects.get(pk=pk)
        except Person.DoesNotExist:
            return JsonResponse({"success": "false", "error": "Peron not found"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return JsonResponse({"success": "false", "error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        data = json.loads(request.body)
        if 'name' in data and data['name']:
            person.name = data['name']
            user.first_name = data['name']
        else:
            data['name'] = person.name
        if 'nickname' in data and data['nickname']:
            person.nickname = data['nickname']
            user.username = data['nickname']
        else:
            data['nickname'] = person.nickname
        if 'email' in data and data['email']:
            try:
                email_validation(data['email'])
            except ValidationError as e:
                return JsonResponse({"success": "false","error": e.message}, status=status.HTTP_400_BAD_REQUEST)
            person.email = data['email']
            user.email = data['email']
        else:
            data['email'] = person.email
        if 'image' in data and data['image']:
            person.image = data['image']
        else:
            data['image'] = person.image
        new_password = data.get('password')
        if new_password:
            try:
                new_password = password_validation(data.get('password'))
            except ValidationError as e:
                error_message = e.messages[0] if hasattr(e, 'messages') else str(e)
                return JsonResponse({"success": "false", "error": error_message}, status=status.HTTP_400_BAD_REQUEST)
            hashed_password = make_password(new_password)
            person.password = hashed_password
            user.password = hashed_password
        else:
            new_password = person.password
        if 'gamemode' in data and data['gamemode']:
            person.gamemode = data['gamemode']
        else:
            data['gamemode'] = person.gamemode
        if 'twofactor' in data and data['twofactor']:
            person.twofactor = bool(data['twofactor'])
        else:
            data['twofactor'] = person.twofactor
        person.save()
        user.save()
        return JsonResponse({"success": "true", "profile": data})

    def delete(self, request, pk):
        try:
            person = Person.objects.get(pk=pk)
            user = User.objects.get(pk=pk)
        except Person.DoesNotExist:
            return JsonResponse({"success": "false", "error": "person not found"}, status=status.HTTP_404_NOT_FOUND)
        person.delete()
        user.delete()
        return JsonResponse({"success": "true", "message": "User deleted successfully"})

class Leaderboard(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            user = Person.objects.get(id=pk)
            serializer = LeaderboardSerializer(user)
            leaderboard_data = {
                "id": user.id,
                "nickname": user.nickname,
                "image": user.image,
                "wins": user.wins,
                "loses": user.loses,
                "matches": user.matches,
                "points": user.points,
            }
        except Person.DoesNotExist:
            return JsonResponse({"success": "false", "error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse({"success": "true", "leaderboard": [leaderboard_data]}, safe=False)

class Home(APIView):
    def get(self, request, pk):
        try:
            user = Person.objects.get(id=pk)
            serializer = HomeSerializer(user)
        except Person.DoesNotExist:
            return JsonResponse({"success": "false", "error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        # return JsonResponse({"success": "true", "profile": serializer.data}, safe=False)
        return Response(serializer.data)

class WaitingRoom(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            active_users = User.objects.filter(is_active=True).exclude(id=pk)
            active_persons = [user.person for user in active_users]
            serializer = WaitingRoomSerializer(active_persons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse({"success": "false", "error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

def save_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

class JoinList(APIView):
    permission_classes = [IsAuthenticated]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_layer = None
        self.group_name = None

    def get(self, request, pk):
        try:
            persons = Person.objects.exclude(game_room=None).select_related('game_room').order_by('game_room_id')
            game_room_data = defaultdict(list)
            for person in persons:
                game_room_data[person.game_room_id].append(person)
            result = {"success": True, "method": "join_list_room", "game_rooms": []}
            for game_room_id, persons_in_room in game_room_data.items():
                if len(persons_in_room) >= 1:
                    game_room = persons_in_room[0].game_room
                    if len(persons_in_room) <= 2 and game_room.max_players <= 2:
                        room_data = {
                            "id": game_room_id,
                            "creator_id": game_room.creator_id,
                            "src": [],
                            "GameLevele": game_room.gamemode,
                            "current_players": len(persons_in_room),
                            "max_players": game_room.max_players,
                            "isJoin": game_room.ongoing,
                        }
                        if len(persons_in_room) == 2:
                            room_data["src"].append({
                                "url": persons_in_room[0].image,
                                "urlClient": persons_in_room[1].image
                            })
                        else:
                            default = os.path.join(os.path.dirname(__file__), 'default.jpg')
                            default_img = save_base64_image(default)
                            room_data["src"].append({
                                "url": persons_in_room[0].image,
                                "urlClient": default_img
                            })
                        room_data["type"] = "User"
                        method = "join_list_room"
                    else:
                        cup = os.path.join(os.path.dirname(__file__), 'cup.jpg')
                        cup_img = save_base64_image(cup)
                        room_data = {
                            "id": game_room_id,
                            "creator_id": game_room.creator_id,
                            "src": cup_img,
                            "GameLevele": "Tournament",
                            "current_players": len(persons_in_room),
                            "max_players": game_room.max_players,
                            "isJoin": game_room.ongoing,
                            "type": "Tournament"
                        }
                        method = "join_list_room"
                    result["game_rooms"].append(room_data)
                    result["method"] = method
            return JsonResponse(result)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "No game rooms found"})

    def post(self, request, pk):
        try:
            user = Person.objects.get(id=pk)
            creator_id = request.get('creator_id')
            game_room_id = request.get('game_room_id')
            try:
                creator = Person.objects.get(id=creator_id)
                game_room = creator.game_room
            except Person.DoesNotExist:
                return JsonResponse({"success": "false", "error": "Creator not found"}, status=status.HTTP_404_NOT_FOUND)
            if creator.ongoing:
                return JsonResponse({"success": "false", "error": "User is already in a game room"}, status=status.HTTP_400_BAD_REQUEST)
            if game_room.is_full():
                if user in game_room.players.all():
                    return JsonResponse({"success": "false", "error": "You already have a game room"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    PlayTournament().post(request, game_room_id=game_room_id, creator_id=creator_id)
                    return JsonResponse({"success": "true", "error": "Game room is full"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                game_room.players.add(user)
                game_room.save()
                user.game_room = game_room
                user.save()
                creator.save()
                if game_room.is_full():
                    PlayTournament().post(request, game_room_id=game_room_id, creator_id=creator_id)
                    return JsonResponse({"success": "true", "method": "start_game", "message": "Successfully joined the game room. Game will start soon."}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"success": "true", "method": "join_list_room", "message": "Successfully joined the game room"}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"success": "false", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def do_broadcast(self):
        if not (self.channel_layer is None) and not (self.group_name is None):
            response = await sync_to_async(self.get)(None, None)
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "stream", "response": response,},
            )

    def set_channel_layer(self, channel_layer):
        self.channel_layer = channel_layer
    
    def set_group_name(self, group_name):
        self.group_name = group_name

class CreateRoom(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        try:
            creator = Person.objects.get(id=pk)
            if creator.game_room:
                return JsonResponse({"success": "false", "error": "User already has a game room"}, status=status.HTTP_400_BAD_REQUEST)
            max_players = request.get('max_players', 2)
            if max_players == '':
                max_players = 2
            else:
                max_players = int(max_players)
            live = request.get('live', "false")
            if live == '':
                live = "false"
            theme = request.get('theme', "dark").lower()
            if theme == '':
                theme = "dark"
            gamemode = request.get('gamemode', "classic").lower()
            if gamemode == '':
                gamemode = "classic"
            game_room_data = {
                'max_players': max_players,
                'live': live,
                'theme': theme,
                'gamemode': gamemode,
                'creator': creator.id,
                'players': [creator.id],
                'is_tournament': max_players > 2,
            }
            game_room_serializer = GameRoomSerializer(data=game_room_data)
            if game_room_serializer.is_valid():
                game_room = game_room_serializer.save()
                creator.game_room = game_room
                creator.save()
                return JsonResponse({"success": "true", "message": "Game room created successfully", "game_room":  creator.game_room.id}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({"success": "false", "error": game_room_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"success": "false", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, opponent_id=None):
        try:
            user = Person.objects.get(id=pk)
            if opponent_id:
                opponent = Person.objects.get(id=opponent_id)
                history_data = History.objects.filter(player=user, opponent=opponent)
                if history_data.exists():
                    full_history_serializer = FullHistorySerializer(history_data, many=True)
                    grouped_full_history = {
                        "opponent_id": opponent.id,
                        "nickname": opponent.nickname,
                        "gamemode": opponent.gamemode,
                        "points": opponent.points,
                        "matches": opponent.matches,
                        "full_history": full_history_serializer.data
                    }
                    response_data = {
                        "success": True,
                        "history": [grouped_full_history]
                    }
                else:
                    response_data = {
                        "success": True,
                        "history": []
                    }
            else:
                history_data = History.objects.filter(player=user)
                opponents_with_history = {history.opponent for history in history_data}
                opponents_history_serializer = OpponentHistorySerializer(opponents_with_history, many=True)
                response_data = {
                    "success": True,
                    "history": opponents_history_serializer.data
                }
            return Response(response_data, status=status.HTTP_200_OK)
        except Person.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data.get('refresh')
            refresh = RefreshToken(refresh_token)
            access = str(refresh.access_token)
            new_refresh = str(refresh)
            response_data = {
                "success": True,
                "access": access,
                "refresh": new_refresh,
            }
            return JsonResponse({"success": "true", "data": response_data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
