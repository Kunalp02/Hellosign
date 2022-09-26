from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
  path('callback/', views.callback, name="callback"),
  path('register/', views.register, name="register"),
  path('login/', views.login, name="login"),
  path('logout/', views.logout, name="logout"),
  path('dashboard/', views.dashboard, name="dashboard"),
  path('send_file/', views.send_file, name="send_file"),
  path('check_status/', views.check_status, name="check_status"),
  path('download_file/<slug:signature_request>/', views.download_file, name="download_file"),
] 

if settings.DEBUG:
 urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
 urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

