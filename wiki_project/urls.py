"""
URL configuration for wiki_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path,include,reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from encyclopedia.views import KnowledgeHubPasswordResetConfirmView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("",include('encyclopedia.urls')),
    path("accounts/",include('accounts.urls')),
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="registration/password_reset.html",
        success_url=reverse_lazy("password_reset_done"),
        from_email=settings.DEFAULT_FROM_EMAIL,
        ), 
        name="password_reset"
        ),
        
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name = "registration/password_reset_done.html"
        ),
        name="password_reset_done"
        ),

    path("reset/<uidb64>/<token>/", KnowledgeHubPasswordResetConfirmView.as_view(
        template_name = "registration/password_reset_confirm.html",
        success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
        ),

    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name = "registration/password_reset_complete.html"
        ),
        name="password_reset_complete"
        ),
    
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

    