# ===== shoes/urls.py =====
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views  # 修正：使用 . 而不是 ..

router = DefaultRouter()
router.register(r'brands', views.BrandViewSet)
router.register(r'shoes', views.ShoeViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]