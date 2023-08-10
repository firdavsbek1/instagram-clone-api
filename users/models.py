import uuid
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
import random
from datetime import datetime,timedelta
from django.contrib.auth.models import AbstractUser,UserManager
from shared.models import BaseModel
from django.core.validators import FileExtensionValidator
from django.utils import timezone

ORDINARY_USER,MANAGER,ADMIN=['ordinary_user','manager','admin']
VIA_EMAIL,VIA_PHONE = ['via_email','via_phone']
NEW,CODE_VERIFIED,DONE,PHOTO_UPLOADED=('new','code_verified','done','photo_uploaded')
EMAIL_EXPIRATION=5
PHONE_EXPIRATION=2


class User(BaseModel,AbstractUser):
    USER_ROLES=(
        (ORDINARY_USER,ORDINARY_USER),
        (MANAGER,MANAGER),
        (ADMIN,ADMIN),
    )
    AUTH_TYPES=(
        (VIA_PHONE,VIA_PHONE),
        (VIA_EMAIL,VIA_EMAIL),
    )
    STATUS_STAGES=(
        (NEW,NEW),
        (CODE_VERIFIED,CODE_VERIFIED),
        (DONE,DONE),
        (PHOTO_UPLOADED,PHOTO_UPLOADED),
    )
    user_role=models.CharField(max_length=30,choices=USER_ROLES,default=ORDINARY_USER)
    auth_type=models.CharField(max_length=30,choices=AUTH_TYPES)
    auth_status=models.CharField(max_length=30,choices=STATUS_STAGES,default=NEW)
    phone_number=models.CharField(max_length=20,blank=True,null=True)
    photo=models.ImageField(upload_to="users/images/",blank=True,null=True,
                            validators=[
                                FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','Webp','heif','avif','jfif'])
                            ])

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def create_verification(self):
        code = "".join([str(random.randint(0, 100) % 10) for _ in range(4)])
        UserConfirmation.objects.create(
            owner_id=self.id,
            code=code
        )
        return code

    def normalize_email(self):
        if self.email:
            self.email=self.email.lower()

    def check_username(self):
        if not self.username:
            temp_username=f"user-{uuid.uuid4().__str__().split('-')[-1]}"
            while User.objects.filter(username=temp_username):
                temp_username = f"user-{uuid.uuid4().__str__().split('-')[-1]}"
            self.username=temp_username

    def check_pass(self):
        if not self.password:
            self.password=f"password-{uuid.uuid4().__str__().split('-')[-1]}"

    def hash_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def generate_token(self):
        refresh=RefreshToken.for_user(self)
        return {
            'access_token':str(refresh.access_token),
            'refresh_token':str(refresh),
        }

    def clean(self):
        self.normalize_email()
        self.check_username()
        self.check_pass()
        self.hash_password()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.clean()
        super(User,self).save(*args,**kwargs)


class UserConfirmation(BaseModel):
    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name='confirmations')
    code=models.CharField(max_length=4)
    expiration_time=models.DateTimeField(null=True)
    is_confirmed=models.BooleanField(default=False)

    def __str__(self):
        return self.owner.username

    def save(self,*args,**kwargs):
        if not self.pk:
            if self.owner.auth_type==VIA_EMAIL:
                self.expiration_time=datetime.now()+timedelta(minutes=EMAIL_EXPIRATION)
            else:
                self.expiration_time=datetime.now()+timedelta(minutes=PHONE_EXPIRATION)
        super(UserConfirmation,self).save(*args,**kwargs)

