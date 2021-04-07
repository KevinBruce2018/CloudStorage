"""testpro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('login/',views.login),
    path('gettoken/',views.getToken),
    path('captcha/',views.getCaptcha),
    path('reg/',views.registor),
    path('activate/',views.activate),
    path('logout/',views.logout),
    path('upload/',views.upload),
    path('download/',views.download),
    path('getkey/',views.getkey),
    path('getList/',views.fileList),
    path('delete/',views.delete),
    path('share/',views.share),
    path('deluser/',views.delUser),
    path('getauthority/',views.getAuthority),
    path('userlist/',views.userList),
    path('loglist/',views.getLogList),
    path('lockuser/',views.lockUser),
    path('unlockuser/',views.unlockuser),
]
