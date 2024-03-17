# serializers.py
from rest_framework import serializers
from .models import SubscriptionPlan, UserApp, UserAppSubscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


class UserAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserApp
        fields = '__all__'


class UserAppSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAppSubscription
        fields = '__all__'
