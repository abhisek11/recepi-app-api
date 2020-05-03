from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.db import transaction
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
'''from knox.auth import TokenAuthentication'''
from custom_decorator import response_modify_decorator_post
from user.knox_views.views import LoginView as KnoxLoginView
from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    render_classes = api_settings.DEFAULT_RENDERER_CLASSES


class LoginView(KnoxLoginView):
    permission_classes = [AllowAny]
    queryset = get_user_model().objects.all()
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @response_modify_decorator_post
    def post(self, request, format=None):
        try:
            data = {}
            with transaction.atomic():
                serializer = AuthTokenSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = serializer.validated_data['user']
                response = super(LoginView, self).post(request, format=None)
                if not user.is_superuser:
                    user_detials = self.queryset.get(email=user)
                    data['token'] = response.data['token']
                    data['token_expiry'] = response.data['expiry']
                    data['user_details'] = {
                                "user_id": user_detials.id,
                                "name": user_detials.name,
                                "email": user_detials.email,
                    }

                return Response(data)
        except Exception as e:
            raise e


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        """Retrive and return authentication user"""
        return self.request.user
