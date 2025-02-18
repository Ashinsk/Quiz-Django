"""quiz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from app import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('auth_app.urls')),
    path('', app_views.Index.as_view()),
    path('quiz/', include('app.urls'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path('admin/doc/', include('django.contrib.admindocs.urls')),
    ] + urlpatterns

handler404 = 'app.views.response_404_handler'

admin.site.site_header = 'Quiz Django'
admin.site.site_title = 'Quiz Django'

# To remove nav side bar in admin panel
# admin.site.enable_nav_sidebar = False