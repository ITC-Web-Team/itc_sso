from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.
    This serializer converts Profile model instances into JSON and vice versa.
    """
    
    class Meta:
        model = Profile
        # Only include the fields that should be exposed in the API
        fields = ['id', 'user', 'roll', 'name', 'branch', 'passing_year', 'course', 'email_verified']
        read_only_fields = ['email_verified']  # Make email_verified read-only

    def to_representation(self, instance):
        """
        Customize the representation of the data to handle human-readable formats.
        For example, converting the 'email_verified' field into 'Yes'/'No'.
        """
        representation = super().to_representation(instance)
        
        # Customize the representation of 'email_verified'
        representation['email_verified'] = 'Yes' if instance.email_verified else 'No'
        
        return representation
    
    def validate_passing_year(self, value):
        """
        Custom validation for the 'passing_year' field.
        Ensure the passing year is realistic (e.g., no future dates).
        """
        from datetime import datetime
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError("Passing year cannot be in the future.")
        return value
