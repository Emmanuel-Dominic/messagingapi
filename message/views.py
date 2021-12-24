from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import UserProfile, Club, ClubUser, UserMessage
from .serializers import (
    RegistrationSerializer, 
    LoginSerializer, 
    UserSerializer,
    UserProfileSerializer,
    ClubSerializer,
    ClubUserSerializer, 
    MessageSerializer
    )


# Create your views here.
class RegistrationAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    http_method_names = ['post']

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    http_method_names = ['post']


class UserListAPIView(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ['get']


class UserRetrieveUpdateAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch', 'delete']
    lookup_field = 'user_id'

    def get_object(self, *args, **kwargs):
        id = self.kwargs.get("user_id")
        return get_object_or_404(User, id=id)


class ClubCreateListAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ClubSerializer
    http_method_names = ['get', 'post']

    def get(self, request):
        queryset = Club.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        club = request.data
        serializer = self.serializer_class(data=club, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ClubRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ClubSerializer
    http_method_names = ['get', 'patch', 'delete']
    queryset = Club.objects.all()
    lookup_field = 'club_id'

    def get_object(self, *args, **kwargs):
        id = self.kwargs.get("club_id")
        return get_object_or_404(Club, id=id)


class ClubUserListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ClubUserSerializer
    http_method_names = ['get']

    def get(self, request):
        queryset = ClubUser.objects.all().distinct('club')
        serializer = self.serializer_class(data=queryset, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class ClubUserCreateAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ClubUserSerializer
    http_method_names = ['post']
    lookup_field = ['club_id', 'user_id',]

    def post(self, request, *args, **kwargs):
        club_user = request.data
        club = Club.objects.filter(id=self.kwargs.get("club_id")).first()
        user = UserProfile.objects.filter(id=self.kwargs.get("user_id")).first()
        serializer_context = {'user': user, 'club': club}
        if request.user==club.owner:
            serializer = self.serializer_class(
                data=club_user, context=serializer_context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        resp = {'error': 'Only group owners are alowed to add participates'}
        return Response(resp, status=status.HTTP_201_CREATED)


class ClubUserRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ClubUserSerializer
    http_method_names = ['get', 'patch', 'delete']
    lookup_field = 'club_id'

    def get_object(self, *args, **kwargs):
        id = self.kwargs.get("club_id")
        return get_object_or_404(ClubUser, club__id=id)


class ClubMessageCreateListAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer
    http_method_names = ['get', 'post']
    lookup_field = 'club_id'

    def get(self, request, *args, **kwargs):
        user = request.user
        club = Club.objects.filter(id=self.kwargs.get('club_id'))
        messages = get_object_or_404(UserMessage, (Q(sender=user.id) | Q(club=club)))
        serializer = self.serializer_class(data=messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        message = request.data
        club = Club.objects.get(id=self.kwargs.get('club_id'))
        ct = ContentType.objects.get_for_model(club)
        serializer = self.serializer_class(data=message)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user, content_type=ct, object_id=club.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserMessageCreateListAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer
    http_method_names = ['get', 'post']
    lookup_field = 'user_id'

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = UserProfile.objects.filter(id=self.kwargs.get('user_id'))
        messages = get_object_or_404(UserMessage, (Q(sender=user.id) | Q(userprofile=profile)))
        serializer = self.serializer_class(data=messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        message = request.data
        profile = UserProfile.objects.get(id=self.kwargs.get('user_id'))
        ct = ContentType.objects.get_for_model(profile)
        serializer = self.serializer_class(data=message)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user, content_type=ct, object_id=profile.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer
    http_method_names = ['get', 'patch', 'delete']
    queryset = UserMessage.objects.all()
    lookup_field = 'message_id'

    def get_object(self, *args, **kwargs):
        id = self.kwargs.get("message_id")
        user = self.request.user
        return get_object_or_404(UserMessage, Q(id=id) & (Q(sender=user.id) | Q(userprofile=user.userprofile)))
