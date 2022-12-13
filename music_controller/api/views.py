from django.shortcuts import render
from rest_framework import generics, status
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse

# Create your views here.
class RoomView(generics.ListAPIView):
    # what we wanna return
    queryset = Room.objects.all()
    # converting into format in which it can be returned
    serializer_class = RoomSerializer

class GetRoomView(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg = 'code'

    def get(self, request, format=None):
        # get the code from the url
        code = request.GET.get(self.lookup_url_kwarg)
        if code != None:
            room = Room.objects.filter(code=code)
            if len(room) > 0:
                data = RoomSerializer(room[0]).data
                # storing(T/F) whether the current user is the host of the room or not
                data["is_host"] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({"Room not found": "Invalid room code."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"Bad request": "Code parameter not found in the url"}, status=status.HTTP_400_BAD_REQUEST)

class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format=None):
        # IF THE USER IS NOT CREATED THEN CREATE THE SESSION
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        # converts incoming data in python form using serializer_class
        serializer = self.serializer_class(data=request.data)
        # if incoming data in python is valid then, we will use that data
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            # retrieving a row from room table filtered on the basis of the current host, if it exists then we don't create a new room, we just update the current room
            queryset = Room.objects.filter(host=host)
            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                self.request.session['room_code'] = room.code
                # updating the guest_can_pause and votes_to_skip values
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
            # if the room doesn't exists
            else:
                room = Room(host=host, guest_can_pause=guest_can_pause,
                            votes_to_skip=votes_to_skip)
                self.request.session['room_code'] = room.code
                room.save()
            # returning the response in json form using .data
            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

class JoinRoomView(APIView):
    lookup_url_kwarg = 'code'

    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        code = request.data.get(self.lookup_url_kwarg)
        if code != None:
            filtered_room = Room.objects.filter(code=code)
            if len(filtered_room) > 0:
                self.request.session['room_code'] = code
                return Response({"message": "Room Joined!"}, status=status.HTTP_200_OK)
            return Response({"message": "Invalid room code."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "Invalid post data, didn't find a code key"}, status=status.HTTP_400_BAD_REQUEST)

# view to handle whether a user is already in a room or not using room_code key
class UserInRoomView(APIView):
    def get(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        data = {
            "code": self.request.session.get("room_code"),
        }
        # similar to RoomSerializer, converts a python dictionary to json form as RoomSerializer does to python objects or database models.
        return JsonResponse(data, status=status.HTTP_200_OK)

class LeaveRoomView(APIView):
    def post(self, request, format=None):
        # removes room_code from the session
        if "room_code" in self.request.session:
            self.request.session.pop("room_code")
            # to delete the room if the person who left the room is also the room host
            host_id = self.request.session.session_key
            filtered_room = Room.objects.filter(host=host_id)
            if len(filtered_room) > 0:
                room_deleted = filtered_room[0]
                room_deleted.delete()
        return Response({"message": "Room deleted"}, status=status.HTTP_200_OK)

class UpdateRoomView(APIView):
    serializer_class = UpdateRoomSerializer

    def patch(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        print(request)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')
            filtered_room = Room.objects.filter(code=code)
            if len(filtered_room) > 0:
                room = filtered_room[0]
                user_id = self.request.session.session_key
                # checking whether the room is updated by the owner of the room or not
                if user_id == room.host:
                    room.guest_can_pause = guest_can_pause
                    room.votes_to_skip = votes_to_skip
                    room.save(
                        update_fields=['guest_can_pause', 'votes_to_skip'])
                    return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
                return Response({"message": "Forbidden!"}, status=status.HTTP_403_FORBIDDEN)
            return Response({"message": "Room not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "Invalid Data..."}, status=status.HTTP_400_BAD_REQUEST)