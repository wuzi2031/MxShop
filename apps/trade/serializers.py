from .models import ShoppingCart, Order, OrderGoods
from goods.serializers import GoodsSerializer
from goods.models import Goods
from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import datetime
import random

User = get_user_model()


class ShoppingCartListSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False, read_only=True)

    class Meta:
        model = ShoppingCart
        fields = "__all__"


class ShoppingCartSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # user = serializers.PrimaryKeyRelatedField(required=True, queryset=User.objects.all())
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())
    nums = serializers.IntegerField(required=True)

    # add_time = serializers.HiddenField(default=datetime.now)

    def create(self, validated_data):
        user = self.context["request"].user
        goods = validated_data['goods']
        nums = validated_data['nums']
        if (nums == 0):
            raise serializers.ValidationError("至少添加一个商品")
        shopping_cart = ShoppingCart.objects.filter(goods=goods, user=user)
        if shopping_cart:
            shopping_cart = shopping_cart[0]
            shopping_cart.nums += nums
            shopping_cart.save()
        else:
            shopping_cart = ShoppingCart.objects.create(**validated_data)
        return shopping_cart

    def update(self, instance, validated_data):
        instance.nums = validated_data['nums']
        re = instance.save()
        return instance

        # class Meta:
        #     model = ShoppingCart
        #     fields = ["user", "goods", "nums"]


class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = "__all__"


class OrderInfoSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    order_sn = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    pay_status = serializers.CharField(read_only=True, default="paying")
    order_mount = serializers.FloatField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)
    post_script = serializers.CharField(required=False, allow_blank=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    goods_id = serializers.ListField(required=True, write_only=True)

    def validate(self, attrs):
        attrs['order_sn'] = self.generate_order_sn()
        self.goods_ides = attrs['goods_id']
        del attrs['goods_id']
        self.fields.pop('goods_id')
        attrs['order_mount'] = self.generate_order_mount(self.goods_ides)
        return attrs

    def create(self, validated_data):
        instance = Order.objects.create(**validated_data)
        shopping_cartes = ShoppingCart.objects.filter(goods_id__in=self.goods_ides, user=self.context['request'].user)
        batch_goods = list()

        for shopping_cart in shopping_cartes:
            order_goods = OrderGoods()
            order_goods.goods = shopping_cart.goods
            order_goods.order = instance
            order_goods.goods_num = shopping_cart.nums
            batch_goods.append(order_goods)
        OrderGoods.objects.bulk_create(batch_goods)
        shopping_cartes.delete()

        return instance

    def generate_order_mount(self, goods_ides):
        shopping_carts = ShoppingCart.objects.filter(goods_id__in=goods_ides, user=self.context['request'].user)
        if not shopping_carts:
            raise serializers.ValidationError('购物车商品不存在')
        mount = 0.0
        for shopping_cart in shopping_carts:
            nums = shopping_cart.nums
            price = shopping_cart.goods.market_price
            mount += price * nums
        return mount

    def generate_order_sn(self):
        sn = "{date_str}{user_id}{random_num}".format(date_str=datetime.now().strftime('%y%m%d%H%M%S'),
                                                      user_id=self.context['request'].user.id,
                                                      random_num=random.randint(10, 100))
        return sn

    class Meta:
        model = Order
        fields = "__all__"
