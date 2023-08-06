from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

from users import views

urlpatterns = [
    # path('sign_in/', include('social_django.urls')),

    path('sign_up/', views.UserCreateApiView.as_view(), name='sign_up'),
    path('sign_in/', jwt_views.TokenObtainPairView.as_view(), name='sign_in'),
    path('sign_in/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('forgot_password/', views.ForgotPasswordApiView.as_view(), name='forgot_password'),
    path('forgot_password/verify/', views.ForgotPasswordOTPVerifyView.as_view(), name='forgot_password_otp'),
    path('forgot_password/update/', views.ForgotPasswordUpdateApiView.as_view(), name='forgot_password_update'),

    path('confirm_email/', views.ConfirmEmailView.as_view(), name='confirm_email'),
    # path('confirm_email/verify/', views.ConfirmEmailOTPVerifyView.as_view(), name='confirm_email_otp'),
    path('confirm_email/update/', views.ConfirmEmailUpdateApiView.as_view(), name='confirm_email_update'),
]
