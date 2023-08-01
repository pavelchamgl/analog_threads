from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

from users import views

urlpatterns = [
    path('sign_in/', include('social_django.urls')),

    path('sign_up/', views.UserCreateApiView.as_view(), name='sign_up'),
    path('sign_in/', jwt_views.TokenObtainPairView.as_view(), name='sign_in'),
    path('sign_in/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

]
