from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    priority_score = serializers.FloatField(read_only=True)
    priority_explanation = serializers.CharField(read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'due_date', 'estimated_hours', 
                  'importance', 'dependencies', 'priority_score', 
                  'priority_explanation']