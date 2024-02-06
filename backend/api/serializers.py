from .models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','name','password','email','recept_number','phone_number','bank_balance']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    

class CreateStockSerializer(serializers.ModelSerializer):
    class Meta:
        models = Stock
        fields = '__all__'

class ListStockSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        models = Stock
        fields = '__all__'


class CreateLogSerializer(serializers.ModelSerializer):
    class Meta:
        models = Log
        fields = '__all__'

class ListLogSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        models = Log
        fields = '__all__'