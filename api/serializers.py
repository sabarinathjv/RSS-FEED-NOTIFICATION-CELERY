from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from rest_framework.authtoken.views import Token




class Subscriptionserializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'title']
        model = Link

class Topsubscriptionserializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'title']
        model = Link





class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password','email']

        extra_kwargs = {'password':{
            'write_only':True,
            'required':True
        }}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        print("haii")
        Token.objects.create(user=user)
        return user




