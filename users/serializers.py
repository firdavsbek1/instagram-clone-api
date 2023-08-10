from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from .models import User, VIA_EMAIL, VIA_PHONE, CODE_VERIFIED, DONE, PHOTO_UPLOADED,NEW
from rest_framework import serializers
from shared.utils import validate_phone_or_email, send_mail, send_phone_number_confirm,identify_user_login_type
from .models import FileExtensionValidator
from django.db.models import Q

MESSAGE_TEMPLATE = {
    "success": False,
    "message": ""
}


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status',
        )

        extra_kwargs = {
            'auth_type': {"read_only": True, "required": False},
            'auth_status': {"read_only": True, "required": False}
        }

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        validated_data = self.auth_validate(data)
        print(validated_data)
        return validated_data

    def validate_email_phone_number(self, value):
        data = {
            'success': False,
        }
        if value and User.objects.filter(email=value).exists():
            data.update(message="This email is already registered!")
            raise ValidationError(data)
        elif value and User.objects.filter(phone_number=value).exists():
            data.update(message="This phone is number already registered!")
            raise ValidationError(data)
        return value

    @staticmethod
    def auth_validate(data):
        email_phone_number = data.get("email_phone_number").lower()
        input_type = validate_phone_or_email(email_phone_number)
        if input_type == VIA_EMAIL:
            data = {
                'email': email_phone_number,
                'auth_type': VIA_EMAIL
            }
        elif input_type == VIA_PHONE:
            data = {
                'phone_number': email_phone_number,
                'auth_type': VIA_PHONE
            }
        return data

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        code = user.create_verification()
        print(code)
        if user.auth_type == VIA_EMAIL:
            send_mail(user.email, code)
        else:
            send_phone_number_confirm(user.phone_number, code)
        return user

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(token=instance.generate_token())
        return data


class UserChangeInformationModelSerializer(serializers.ModelSerializer):
    pass


class UserChangeInformationSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get('password')
        password_confirmation = data.get('password_confirmation')
        if password != password_confirmation:
            MESSAGE_TEMPLATE.update(message="The passwords don't match! Please, try again!")
            raise ValidationError(MESSAGE_TEMPLATE)
        if password:
            validate_password(password)
        return data

    def validate_username(self, username):
        if len(username) < 5 or len(username) > 30:
            MESSAGE_TEMPLATE.update(message='The username must be between 5 and 30 characters long!')
            raise ValidationError(MESSAGE_TEMPLATE)
        return username

    def update(self, instance, validated_data):
        instance.first_name=validated_data.get('first_name',instance.first_name)
        instance.last_name=validated_data.get('last_name',instance.last_name)
        instance.username=validated_data.get('username',instance.username)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status==CODE_VERIFIED:
            instance.auth_status=DONE
        instance.save()
        return instance


class UploadUserPhotoSerializer(serializers.Serializer):
    photo=serializers.ImageField(write_only=True,required=True,validators=[
        FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','Webp','heif','avif','jfif'])
    ])

    def update(self, instance, validated_data):
        photo=validated_data.get('photo')
        if photo:
            instance.photo=photo
            instance.auth_status=PHOTO_UPLOADED
        instance.save()
        return instance


class UserLoginSerializer(TokenObtainPairSerializer):

    def __init__(self,*args,**kwargs):
        super(UserLoginSerializer,self).__init__(*args,**kwargs)
        self.fields['user_input']=serializers.CharField(required=True)
        self.fields['username']=serializers.CharField(read_only=True,required=False)

    def auth_validate(self,data):
        user_input=data.get('user_input')
        user_login_type=identify_user_login_type(user_input)
        current_user=self.get_user(user_login_type,user_input).first()
        if not current_user:
            MESSAGE_TEMPLATE.update(message='User with that credential not found!')
            raise ValidationError(MESSAGE_TEMPLATE)
        if current_user.auth_status in [NEW,CODE_VERIFIED]:
            MESSAGE_TEMPLATE.update(message='Registration was not completed!')
            raise ValidationError(MESSAGE_TEMPLATE)
        authenticated_user=authenticate(username=current_user.username,password=data['password'])
        if not authenticated_user:
            MESSAGE_TEMPLATE.update(message="Password and username not match!")
            raise ValidationError(MESSAGE_TEMPLATE)
        return authenticated_user

    def validate(self,data):
        user=self.auth_validate(data)
        # validation logic
        data=user.generate_token()
        data['full_name']=user.full_name
        data['auth_type']=user.auth_type
        data['auth_status']=user.auth_status
        return data

    def get_user(self,user_login_type,user_input):
        if user_login_type=='email':
            user=User.objects.filter(email__iexact=user_input)
        elif user_login_type=='phone_number':
            user=User.objects.filter(phone_number=user_input)
        else:
            user=User.objects.filter(username=user_input)
        return user


class UserTokenRefreshSerializer(TokenRefreshSerializer):

    def validate(self,attrs):
        data=super().validate(attrs)
        # for updating user login
        access_token_instance=AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user=get_object_or_404(User,id=user_id)
        update_last_login(None,user)
        return data


class LogoutSerializer(serializers.Serializer):
    refresh_token=serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    user_input=serializers.CharField()

    def validate(self,data):
        user_input=data['user_input']
        user=User.objects.filter(Q(email=user_input) | Q(phone_number=user_input))
        if not user.exists():
            MESSAGE_TEMPLATE.update(message="User not found!")
            raise NotFound(MESSAGE_TEMPLATE)
        data['user']=user.first()
        return data


class ResetPasswordSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    password=serializers.CharField(required=True,write_only=True)
    password_confirm=serializers.CharField(required=True,write_only=True)

    class Meta:
        model = User
        fields=(
            'id',
            'password',
            'password_confirm'
        )

    def validate(self,data):
        password=data.get('password')
        password_confirm=data.get('password_confirm')
        if password != password_confirm:
            MESSAGE_TEMPLATE.update(message='The passwords not match!')
            raise ValidationError(MESSAGE_TEMPLATE)
        validate_password(password)
        return data

    def update(self, instance, validated_data):
        password=validated_data.pop('password')
        instance.set_password(password)
        instance.save()
        return self.instance
