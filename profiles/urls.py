from django.urls import path
from .views import profile, delete_profile_image, \
    profile_detail, update_profile

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('update_profile/', update_profile, name='update_profile'),
    path('profile/<int:user_id>/', profile_detail, name='profile_detail'),
    path('delete_profile_image/', delete_profile_image, name='delete_profile_image'),
]