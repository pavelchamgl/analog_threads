from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

from users import views

urlpatterns = [
    # path('sign_in/', include('social_django.urls')),
    path('auth_test/', views.TestView.as_view(), name='test'),
    path('sock_test/', views.SockTestView.as_view(), name='sock_test'),

    path('sign_up/', views.UserCreateApiView.as_view(), name='sign_up'),
    path('sign_in/', views.CustomTokenObtainPairView.as_view(), name='sign_in'),
    path('sign_in/google/', views.GoogleLoginView.as_view(), name='sign_in_google'),
    path('sign_in/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('forgot_password/', views.ForgotPasswordApiView.as_view(), name='forgot_password'),
    path('forgot_password/verify/', views.ForgotPasswordOTPVerifyView.as_view(), name='forgot_password_otp'),
    path('forgot_password/update/', views.ForgotPasswordUpdateApiView.as_view(), name='forgot_password_update'),

    path('confirm_email/', views.ConfirmEmailView.as_view(), name='confirm_email'),
    # path('confirm_email/verify/', views.ConfirmEmailOTPVerifyView.as_view(), name='confirm_email_otp'),
    path('confirm_email/update/', views.ConfirmEmailUpdateApiView.as_view(), name='confirm_email_update'),


    path('user/profile/follow_requests/', views.FollowersListPendingView.as_view(), name='followers_pending_list'),
    path('user/profile/follow_requests/allow/', views.FollowPendingConfirm.as_view(), name='followers_pending_allow'),
    path('user/profile/follow_requests/decline/', views.FollowPendingDecline.as_view(), name='followers_pending_decline'),

    path('user/profile/followers/<int:followee_pk>/', views.FollowersListView.as_view(), name='followers_list'),
    path('user/profile/follows/<int:follower_pk>/', views.FollowingListView.as_view(), name='following_list'),
    path('user/profile/mutual_follow/', views.MutualFollowCheckView.as_view(), name='mutual_follow_check'),
    path('user/profile/follow/', views.FollowActionView.as_view(), name='follow_followee_action'),
    path('user/profile/unfollow/', views.UnfollowActionView.as_view(), name='unfollow_followee_action'),
    path('user/profile/delete/', views.DeleteFollowerView.as_view(), name='delete_follower_action'),

    path('user/profile/update/', views.UserProfileUpdateView.as_view(), name='user_profile_update'),
    path('user/profile/me/', views.SelfUserView.as_view(), name='user_profile_me'),
    path('user/profile/<int:pk>/', views.UserProfileViewByPK.as_view(), name='user_profile_data'),
    path('user/profile/<str:username>/', views.UserProfileViewByUsername.as_view(), name='user-profile-by-username'),
    path('user/profile/me/edit_photo/', views.UserProfilePhotoUpdateAPIView.as_view(), name='user_profile_edit_photo'),
    path('user/profile/me/delete_photo/', views.UserProfilePhotoDestroyAPIView.as_view(), name='user_profile_delete_photo'),

]
