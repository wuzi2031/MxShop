from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, VerifyCode
from .setting import REGEX_MOBILE, VERIFY_CODE_TIMEOUT
import re, time
from datetime import datetime, timedelta
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserRegSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(read_only=True)
    username = serializers.CharField(max_length=11, min_length=11, allow_null=False, allow_blank=False,
                                     help_text="手机号码", label="用户名",
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已存在")])
    code = serializers.CharField(required=True, max_length=4, min_length=4,
                                 error_messages={
                                     "blank": "验证码不能为空",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="手机验证码",
                                 label="验证码")
    password = serializers.CharField(write_only=True, style={'inpt_type': 'password'},
                                     help_text="用户密码", label="密码")

    def validate_code(self, code):
        verify_code = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by('-add_time')
        if (not verify_code):
            raise serializers.ValidationError('验证码不存在')
        add_time = verify_code[0].add_time.timestamp()
        dis_time = datetime.now().timestamp() - add_time
        if (dis_time > VERIFY_CODE_TIMEOUT):
            raise serializers.ValidationError('验证码已过期')
        if (verify_code[0].code != code):
            raise serializers.ValidationError('验证码不正确')

    def validate(self, attrs):
        attrs["mobile"] = attrs["username"]
        del attrs["code"]
        self.fields.pop('code')
        return attrs

    class Meta:
        model = User
        fields = ["code", "username", "mobile", "password"]


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """

    class Meta:
        model = User
        fields = ("name", "gender", "birthday", "email", "mobile")


class SmsCodeSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=11, min_length=11, allow_null=False, allow_blank=False,
                                     help_text="手机号码", label="用户名")

    def validate_mobile(self, username):
        if not re.match(REGEX_MOBILE, username):
            raise serializers.ValidationError("手机号码非法")
        user = User.objects.filter(username=username)
        if user:
            raise serializers.ValidationError('用户已存在')
        verify_code = VerifyCode.objects.filter(mobile=self.initial_data["username"],
                                                code=code).order_by('-add_time')
        if (verify_code):
            add_time = verify_code[0].add_time.timestamp()
            dis_time = datetime.now().timestamp() - add_time
            if (dis_time < VERIFY_CODE_TIMEOUT):
                raise serializers.ValidationError('不能频繁发送验证码')
        return username
