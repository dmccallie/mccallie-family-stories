from django.urls import path
from .views import chat_list, chat_detail, add_chat # chat_update, chat_delete

urlpatterns = [
    path('chat_list/', chat_list, name='chat_list'),
    path('chat_detail/<int:chat_id>/', chat_detail, name='chat_detail'),
    path('add_chat/', add_chat, name='add_chat'),
    # path('chat_update/<int:chat_id>/', chat_update, name='chat_update'),
    # path('chat_delete/<int:chat_id>/', chat_delete, name='chat_delete'),
]