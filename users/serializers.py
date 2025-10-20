from rest_framework import serializers 
from django.contrib.auth.models import User
from .models import UserProfile 

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True , max_length = 8)
    password2 = serializers.CharField(write_only=True , max_length =  8)

    class Meta:
        model = User 
        fields= ['username', 'email', 'password', 'password2', 'first_name', 'last_name']

    def validate(self, data):
        if data['password']!=data['password2']:
            raise serializers.ValidationError("Passwords don't match!")
        
        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already registerd!")  
        
        return data

    def create(self, validated_data):
        validated_data.pop('password2') #don't need it 

        user = User.objects.create_user(**validated_data)

        # Automatically create a profile for the user (could have used signals but keeping it simple )
        UserProfile.objects.create(user=user)
        
        return user 
    
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'address', 'city', 'postal_code', 'country']
    
    def update(self, instance, validated_data):
        # Update user fields if provided
        user_data = validated_data.pop('user', {})
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


# Simple user serializer for displaying user info
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
