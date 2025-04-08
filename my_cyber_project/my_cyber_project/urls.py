from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from my_cyber_app.views import (
    user_login,
    upload_file,
    data_analysis,
    user_logout,
    malware_analysis,
    unmalware_analysis,
    check_link,
)

urlpatterns = [
    path('', RedirectView.as_view(url='login/')),  # Redirect root to login
    path('admin/', admin.site.urls),
    path('login/', user_login, name='user_login'),
    path('upload/', upload_file, name='upload_file'),
    path('data_analysis/<str:filename>/', data_analysis, name='data_analysis'),
    path('logout/', user_logout, name='user_logout'),
    path('malware_analysis/', malware_analysis, name='malware_analysis'),
    path('unmalware_analysis/', unmalware_analysis, name='unmalware_analysis'),
    path('check-link/', check_link, name='check_link'),  # For the link checking functionality
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
