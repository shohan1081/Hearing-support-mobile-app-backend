from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/legal/', include('legal_pages.urls')),
    path('api/weekly-tutorials/', include('weekly_tutorials.urls', namespace='weekly_tutorials')),
    path('api/weekly-tips/', include(('weekly_tutorials.urls', 'weekly_tips'), namespace='weekly_tips')),
    path('api/learn/', include(('learn.urls', 'learn'), namespace='learn')),
    path('api/what-normal/', include(('what_normal.urls', 'what_normal'), namespace='what_normal')),
    path('api/skills-strategies/', include(('skills_strategies.urls', 'skills_strategies'), namespace='skills_strategies')),
    path('api/device-care/', include(('device_care.urls', 'device_care'), namespace='device_care')),
    path('api/support-chat/', include(('support_chat.urls', 'support_chat'), namespace='support_chat')),
    path('api/chatbot/', include(('ai_chatbot.urls', 'ai_chatbot'), namespace='ai_chatbot')),
    path('api/ai-chat/', include(('ai_chatbot.urls', 'ai_chat'), namespace='ai_chat')),
]
