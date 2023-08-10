from django.urls import path
from .views import UserSignupView,UserVerifyView,ResendVerificationView,UserUpdateApiView,UploadUserPhotoApiView,\
    UserLoginView,UserRefreshTokenView,UserLogoutView,ForgotPasswordView,ResetPasswordView
urlpatterns = [
    path("login/",UserLoginView.as_view()),
    path("logout/",UserLogoutView.as_view()),
    path("login/refresh/",UserRefreshTokenView.as_view()),
    path("forgot-password/",ForgotPasswordView.as_view()),
    path("reset-password/",ResetPasswordView.as_view()),
    path("signup/",UserSignupView.as_view()),
    path("verify/",UserVerifyView.as_view()),
    path('resend-verification/',ResendVerificationView.as_view()),
    path('update/',UserUpdateApiView.as_view()),
    path('uplaod-photo/',UploadUserPhotoApiView.as_view()),
]