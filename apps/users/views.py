from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, mixins
from .utils import send_verify_code
from rest_framework import status
from rest_framework.response import Response
from .serializers import SmsCodeSerializer, UserRegSerializer, UserDetailSerializer
from .models import VerifyCode
from random import sample
from random import choice
from rest_framework import permissions
from rest_framework import authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.contrib.auth import get_user_model
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    用户
    create:
    用户注册
    retrieve:
    获取用户资料
    update:
    用户资料修改
    """
    serializer_class = UserRegSerializer
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegSerializer

        return UserDetailSerializer

    # permission_classes = (permissions.IsAuthenticated, )
    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return []

        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()


class VerifyCodeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    用户验证码
    create:
    发送短信验证码
    """
    serializer_class = SmsCodeSerializer

    def creat_verify_code(self):
        codelist = [x for x in range(10)]
        code = "".join(str(s) for s in sample(codelist, 4))
        return code

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)
        data = serializer.validated_data
        mobile = data['username']
        code = self.creat_verify_code()
        result = send_verify_code(mobile, code)
        if (result == status.HTTP_200_OK):
            verify_Code = VerifyCode(mobile=mobile, code=code)
            verify_Code.save()
            return Response({"username": mobile}, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"username": ["短信发送失败"]}, status=status.HTTP_400_BAD_REQUEST, headers=headers)
