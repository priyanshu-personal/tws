from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('api.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# handler404 = 'webapp.views.handle404'

# handler500 = 'webapp.views.handle500'