from .models import ShoppingCart
from goods.serializers import GoodsSerializer
from goods.models import Goods
from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()


class ShoppingCartListSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False, read_only=True)

    class Meta:
        model = ShoppingCart
        fields = "__all__"


class ShoppingCartSerializer(serializers.Serializer):
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault)
    user = serializers.PrimaryKeyRelatedField(required=True, queryset=User.objects.all())
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
