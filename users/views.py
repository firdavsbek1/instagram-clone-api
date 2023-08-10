from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.exceptions import ValidationError
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignUpSerializer, UserChangeInformationSerializer, UploadUserPhotoSerializer, \
    UserLoginSerializer, UserTokenRefreshSerializer, LogoutSerializer, ForgotPasswordSerializer,ResetPasswordSerializer
from .models import User
from datetime import datetime
from .models import CODE_VERIFIED, NEW, DONE, PHOTO_UPLOADED, VIA_PHONE, VIA_EMAIL
from .serializers import send_mail, send_phone_number_confirm, validate_phone_or_email


class UserSignupView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = SignUpSerializer


class UserVerifyView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        code = request.data.get('code')
        user = request.user
        self.verify_code(user, code)
        token = user.generate_token()
        return Response(
            {
                "success": True,
                'auth_status': user.auth_status,
                'auth_type': user.auth_type,
                'access_token': token['access_token'],
                'refresh_token': token['refresh_token'],
            }
        )

    @staticmethod
    def verify_code(user, code):
        confirmations = user.confirmations.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        if not confirmations.exists():
            raise ValidationError({"success": False, "message": "The code that was sent was incorrect or expired!"})
        confirmations.update(is_confirmed=True)
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()


class ResendVerificationView(APIView):

    def get(self, request):
        user = request.user
        self.verify_code_expiration(user)
        code = user.create_verification()
        print(code)
        if user.auth_type == VIA_EMAIL:
            send_mail(user.email, code)
        else:
            send_phone_number_confirm(user.phone_number, code)
        return Response({
            "success": True,
            "message": "Your confirmation code has been resent.Please use it to verify you account!"
        })

    @staticmethod
    def verify_code_expiration(user):
        confirmations = user.confirmations.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
        if confirmations.exists():
            raise ValidationError(
                {
                    'success': False,
                    'message': "Your confirmation code was sent and it is not expired yet!"
                }
            )


class UserUpdateApiView(UpdateAPIView):
    serializer_class = UserChangeInformationSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(
            {
                'success': True,
                'message': "Your account has been set successfully!",
                'auth_status': DONE
            }
        )

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response(
            {
                'success': True,
                'message': "Your account has been set successfully!",
                'auth_status': DONE,
                'view': 'partial_update'
            }
        )


class UploadUserPhotoApiView(APIView):

    def put(self, request, *args, **kwargs):
        data = request.data
        serialized_data = UploadUserPhotoSerializer(request.user, data=data)
        if serialized_data.is_valid():
            serialized_data.save()
            return Response({
                'success': True,
                'message': "Your photo has been set successfully!"
            })
        return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer


class UserRefreshTokenView(TokenRefreshView):
    serializer_class = UserTokenRefreshSerializer


class UserLogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serialized_data = self.serializer_class(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        try:
            refresh_token = serialized_data.data['refresh_token']
            refresh_token_instance = RefreshToken(refresh_token)
            refresh_token_instance.blacklist()
            return Response({
                "success": True,
                "message": "You are successfully logged out!"
            })
        except TokenError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        user_input=serializer.validated_data['user_input']
        input_type=validate_phone_or_email(user_input)
        code=user.create_verification()
        print(code)
        if input_type == VIA_EMAIL:
            send_mail(user_input,code)
        else:
            send_phone_number_confirm(user_input,code)
        token=user.generate_token()
        return Response({
            'success': True,
            "message": f"The confirmation code was sent to your {input_type[4:]}!",
            'auth_type':user.auth_type,
            "access_token": token['access_token'],
            "refresh_token":token['refresh_token'],

        })


class ResetPasswordView(UpdateAPIView):
    serializer_class= ResetPasswordSerializer
    http_method_names = ["put"]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        data=super().put(request,*args,**kwargs).data
        data['success']=True
        data['message']="Your password changed successfully! Go back and login now."
        return Response(data)
