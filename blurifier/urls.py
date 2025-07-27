from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from ninja import NinjaAPI
from core.api import router as core_router

api = NinjaAPI()
api.add_router('/', core_router)


def ping(request):
    return JsonResponse({'ping': 'pong'})


urlpatterns = [
    path('ping/', ping),
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
