from rest_framework import mixins, viewsets
from .serializers import ShoppingCartSerializer, ShoppingCartListSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from .models import ShoppingCart


class ShoppingCartViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    """
    购物车
    creat:
        加入购物车
    list:
        购物车列表
    update:
        更新购物车
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # serializer_class = ShoppingCartSerializer
    lookup_field = "goods_id"

    def perform_create(self, serializer):
        shop_cart = serializer.save()
        goods = shop_cart.goods
        goods.goods_num -= shop_cart.nums
        goods.save()

    def perform_update(self, serializer):
        existed_record = ShoppingCart.objects.get(id=serializer.instance.id)
        existed_nums = existed_record.nums
        saved_record = serializer.save()
        nums = saved_record.nums - existed_nums
        goods = saved_record.goods
        goods.goods_num -= nums
        goods.save()

    def get_queryset(self):
        user = self.request.user
        return ShoppingCart.objects.filter(user=user)

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            return ShoppingCartListSerializer
        return ShoppingCartSerializer
