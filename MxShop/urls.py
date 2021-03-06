"""MxShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
# from django.contrib import admin
import xadmin
from MxShop.settings import MEDIA_ROOT,STATIC_ROOT
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token

from goods.views import GoodsListViewSet, Hello
from apps.users.views import VerifyCodeViewSet, UserViewSet
from trade.views import ShoppingCartViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'goods', GoodsListViewSet, base_name='goods')
router.register(r'verify_code', VerifyCodeViewSet, base_name='verify_code')
router.register(r'user', UserViewSet, base_name='user')
router.register(r'shopping_cart', ShoppingCartViewSet, base_name='shopping_cart')
router.register(r'order', OrderViewSet, base_name='order')
urlpatterns = [
    url(r'^$', Hello, name='hello'),
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include_docs_urls(title='wzm生鲜')),
    # 商品列表
    # url(r'^goods/$',GoodsListView.as_view(),name='goods-list')
    url(r'^', include(router.urls)),
    url(r'^login/', obtain_jwt_token),
    url(r'^verify_jwt_token/', verify_jwt_token),
]
