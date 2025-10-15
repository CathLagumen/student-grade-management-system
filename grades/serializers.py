from rest_framework import serializers
from .models import User, Subject, Grade

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_admin', 'is_student']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description']

class GradeSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = Grade
        fields = ['id', 'student', 'subject', 'grade', 'semester', 'school_year', 'remarks']
