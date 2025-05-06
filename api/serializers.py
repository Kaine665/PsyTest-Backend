from rest_framework import serializers
from .models import User, ChatHistory, Patient, Prompt

class UserSerializer(serializers.Serializer):
    account = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=20, write_only=True)
    
    def create(self, validated_data):
        user = User(
            account=validated_data.get('account'),
            password=validated_data.get('password')
        )
        user.save()
        return user
    
    def update(self, instance, validated_data):
        instance.account = validated_data.get('account', instance.account)
        instance.password = validated_data.get('password', instance.password)
        instance.save()
        return instance


class PatientSerializer(serializers.Serializer):
    patient_id = serializers.CharField(max_length=20)
    patient_name = serializers.CharField(max_length=100)
    patient_introduce = serializers.CharField(allow_blank=True)
    prompt = serializers.CharField(allow_blank=True)
    
    def create(self, validated_data):
        patient = Patient(
            patient_id=validated_data.get('patient_id'),
            patient_name=validated_data.get('patient_name'),
            patient_introduce=validated_data.get('patient_introduce', ''),
            prompt=validated_data.get('prompt', '')
        )
        patient.save()
        return patient
    
    def update(self, instance, validated_data):
        instance.patient_id = validated_data.get('patient_id', instance.patient_id)
        instance.patient_name = validated_data.get('patient_name', instance.patient_name)
        instance.patient_introduce = validated_data.get('patient_introduce', instance.patient_introduce)
        instance.prompt = validated_data.get('prompt', instance.prompt)
        instance.save()
        return instance


class PromptSerializer(serializers.Serializer):
    prompt_id = serializers.CharField(max_length=20)
    prompt_type = serializers.CharField(max_length=50)
    prompt = serializers.CharField()
    
    def create(self, validated_data):
        prompt = Prompt(
            prompt_id=validated_data.get('prompt_id'),
            prompt_type=validated_data.get('prompt_type'),
            prompt=validated_data.get('prompt')
        )
        prompt.save()
        return prompt
    
    def update(self, instance, validated_data):
        instance.prompt_id = validated_data.get('prompt_id', instance.prompt_id)
        instance.prompt_type = validated_data.get('prompt_type', instance.prompt_type)
        instance.prompt = validated_data.get('prompt', instance.prompt)
        instance.save()
        return instance


class ChatMessageSerializer(serializers.Serializer):
    role = serializers.CharField(max_length=20)
    content = serializers.CharField()


class ChatHistorySerializer(serializers.Serializer):
    chat_history_id = serializers.CharField(max_length=20)
    user_id = serializers.CharField(max_length=20)
    prompt_id = serializers.CharField(max_length=20)
    patient_id = serializers.CharField(max_length=20)
    update_time = serializers.CharField(max_length=50)
    content = ChatMessageSerializer(many=True)
    
    def create(self, validated_data):
        content_data = validated_data.pop('content')
        chat_history = ChatHistory(
            chat_history_id=validated_data.get('chat_history_id'),
            user_id=validated_data.get('user_id'),
            prompt_id=validated_data.get('prompt_id'),
            patient_id=validated_data.get('patient_id'),
            update_time=validated_data.get('update_time'),
            content=content_data
        )
        chat_history.save()
        return chat_history
    
    def update(self, instance, validated_data):
        instance.chat_history_id = validated_data.get('chat_history_id', instance.chat_history_id)
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.prompt_id = validated_data.get('prompt_id', instance.prompt_id)
        instance.patient_id = validated_data.get('patient_id', instance.patient_id)
        instance.update_time = validated_data.get('update_time', instance.update_time)
        
        content_data = validated_data.get('content')
        if content_data is not None:
            instance.content = content_data
            
        instance.save()
        return instance