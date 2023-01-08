from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('save-video', views.tiktok_downloader),
    path('show_video', views.show_video),
    path('download_video', views.download_video)
]


handler404="helpers.views.handle_not_found"
