"""
URL configuration for google_books project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/books/',include('books.urls')),
    path('api/auth/',include('authentication.urls')),
]



# from django.contrib import admin
# from django.urls import path, include, re_path
# from django.conf import settings
# from django.conf.urls.static import static



# urlpatterns = [
#     re_path(r'^admin/', admin.site.urls),
#     re_path(r'^auth/',include('authentication.urls')),
#     # re_path(r'',include('queue_management.urls')),
#     re_path(r'^api/',include('queue_management.urls')),
#     re_path(r'^api/lab/',include('synclo_labs.urls')),
#     re_path(r'^api/syncloai/',include('qms_ai.urls')),
#     re_path(r'^api/payment/',include('payments.urls')),
#     re_path(r'^api/nms/',include('nurse.urls')),
#     # re_path(r'^DOC/',include('app3.urls'))
# ]