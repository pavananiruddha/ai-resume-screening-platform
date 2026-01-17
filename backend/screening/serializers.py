from rest_framework import serializers
from .models import Resume

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ('id', 'job', 'candidate_name', 'candidate_email', 'resume_file', 'uploaded_at', 'status', 'score', 'extracted_text')
        read_only_fields = ('id', 'uploaded_at', 'status', 'score', 'extracted_text')

class ScreeningRequestSerializer(serializers.Serializer):
    resume_id = serializers.IntegerField()

class ScreeningResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    score = serializers.FloatField()
    status = serializers.CharField()
    matched_keywords = serializers.ListField(child=serializers.CharField())
