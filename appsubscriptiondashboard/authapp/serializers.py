from rest_framework import serializers

#For Checking Unique Values
from rest_framework.validators import UniqueValidator

#For User Login Authentication
from django.contrib.auth import authenticate

#For Getting Random String
from django.utils.crypto import get_random_string

# Use for checking existing Password
from django.contrib.auth.hashers import check_password

# Getting Current User Model
from django.contrib.auth import get_user_model

# Use for Validation Errors
from django.core.exceptions import ValidationError

#For Using App Models
from .models import (AppUser, LoginAnalytics, AppActionAnalytics)

# Using Common Variables
from utils import constants

from utils.common_utils import (CommonUtils)



#User List
class UserListSerializer(serializers.ModelSerializer):
    datejoined=serializers.DateTimeField(read_only=True, source='date_joined',format=constants.datetime_format)

    class Meta:
        model = AppUser
        fields = ('id',
                  'name',
                  'email', 
                  'username', 
                  'contact_no',
                  'is_auth',
                  'datejoined'
                  )


#Normal Signup
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=AppUser.objects.all())]
            )
    name=serializers.CharField(required=False,default='N/A')
    password = serializers.CharField(min_length=8,required=False)
    contact_no= serializers.CharField(max_length=150,
                                        required=False,
                                        validators=[UniqueValidator(queryset=AppUser.objects.all())])
    
    def create(self, validated_data):
            
        user = AppUser.objects.create_user(
                name=validated_data['name'],
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                contact_no=validated_data['contact_no']
                )
        return user

    datejoined=serializers.DateTimeField(read_only=True, source='date_joined',format=constants.datetime_format)
    class Meta:
        model = AppUser
        fields = ('__all__')

# Use for Normal Login
class LoginSerializer(serializers.ModelSerializer):

    email=serializers.EmailField(required=True)
    username = serializers.CharField(required=False)
    password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        # user = authenticate(username=attrs['email'], password=attrs['password'])
        User = get_user_model()
        
        try:
            user = AppUser.objects.get(email=attrs['email'])
            if user.check_password(attrs['password']):
                if user.is_active==True:
                    return {'user': user}
                else:
                    raise serializers.ValidationError('User is disabled.')
            else:
                raise serializers.ValidationError('Incorrect email or password.')
        except AppUser.DoesNotExist:
            raise serializers.ValidationError('Incorrect email or password.')
    
    class Meta:
        model = AppUser
        fields = ('__all__')
    
    
# User  for Changing Password    
class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    def validate_old_password(self, value):
            """
            Validate that the old password is correct.
            """
            user = self.context['request'].user
            if not check_password(value, user.password):
                raise serializers.ValidationError("Incorrect old password")
            return value

    def save(self, **kwargs):
        """
        Save the new password for the user.
        """
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user

# Use for Resetting Password
class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for password reset endpoint.
    """
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(min_length=8, required=True)

    def validate_email(self, value):
        """
        Validate that the email address exists in the database.
        """
        User = get_user_model()
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise ValidationError("Email address not found")
        return value

    def save(self, **kwargs):
        """
        Save the new password for the user.
        """
        User = get_user_model()
        user = User.objects.get(email=self.validated_data['email'])
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user
