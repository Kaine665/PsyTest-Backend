from django.urls import path, include
from . import views

urlpatterns = [
    path('login', views.login),
    path('chat_history/save', views.save_chat_history),
    path('chat_history/delete', views.delete_chat_history),
    path('chat_history/user/<str:user_id>', views.get_chat_histories_by_user),
    path('chat_history/<str:chat_history_id>', views.get_chat_history),
    path('patient/all', views.get_all_patients),
    path('prompt/all', views.get_all_prompts),
    path('patient/<str:patient_id>', views.get_patient),
    path('prompt/<str:prompt_id>', views.get_prompt),    
    path('load_chat_page', views.load_chat_page),
    path('process_message', views.process_message),
    path('get_feedback', views.get_feedback),
    path('post_messages', views.post_messages),
]
