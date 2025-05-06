from rest_framework import serializers
import json

class TypedBaseSerializer(serializers.Serializer):
    """基础序列化器，确保所有序列化数据都包含Type字段"""
    type = serializers.CharField(required=True)
    
    def validate(self, data):
        """确保type字段存在并有效"""
        if 'type' not in data or not data['type']:
            raise serializers.ValidationError("required field 'Type' not set")
        return data

class UserSerializer(TypedBaseSerializer):
    """用户序列化器"""
    account = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def to_representation(self, instance):
        """从实例转换为序列化表示"""
        data = {
            'type': 'user',
            'account': instance.account if hasattr(instance, 'account') else instance.get('account', '')
        }
        return data
    
    def to_internal_value(self, data):
        """反序列化验证"""
        if not isinstance(data, dict):
            data = json.loads(data) if isinstance(data, str) else {'account': '', 'type': 'user'}
        if 'type' not in data:
            data['type'] = 'user'
        return super().to_internal_value(data)

class MessageSerializer(serializers.Serializer):
    """聊天消息序列化器"""
    role = serializers.CharField(required=True)
    content = serializers.CharField(required=True)

class ChatHistorySerializer(TypedBaseSerializer):
    """聊天历史序列化器"""
    chat_history_id = serializers.CharField(required=True)
    user_id = serializers.CharField(required=True)
    prompt_id = serializers.CharField(required=True)
    patient_id = serializers.CharField(required=True)
    update_time = serializers.CharField(required=True)
    content = serializers.ListField(child=MessageSerializer(), required=True)
    
    def to_representation(self, instance):
        """从实例转换为序列化表示"""
        if hasattr(instance, '__dict__'):
            return {
                'type': 'chat_history',
                'chat_history_id': instance.chat_history_id,
                'user_id': instance.user_id,
                'prompt_id': instance.prompt_id,
                'patient_id': instance.patient_id,
                'update_time': instance.update_time,
                'content': instance.content
            }
        return {
            'type': 'chat_history',
            'chat_history_id': instance.get('chat_history_id', ''),
            'user_id': instance.get('user_id', ''),
            'prompt_id': instance.get('prompt_id', ''),
            'patient_id': instance.get('patient_id', ''),
            'update_time': instance.get('update_time', ''),
            'content': instance.get('content', [])
        }
    
    def to_internal_value(self, data):
        """反序列化验证"""
        if not isinstance(data, dict):
            data = json.loads(data) if isinstance(data, str) else {}
        if 'type' not in data:
            data['type'] = 'chat_history'
        return super().to_internal_value(data)

class PatientSerializer(TypedBaseSerializer):
    """病人信息序列化器"""
    patient_id = serializers.CharField(required=True)
    patient_name = serializers.CharField(required=True)
    patient_introduce = serializers.CharField(required=False, allow_blank=True, default="")
    prompt = serializers.CharField(required=True)
    
    def to_representation(self, instance):
        """从实例转换为序列化表示"""
        if hasattr(instance, '__dict__'):
            return {
                'type': 'patient',
                'patient_id': instance.patient_id,
                'patient_name': instance.patient_name,
                'patient_introduce': instance.patient_introduce,
                'prompt': instance.prompt
            }
        return {
            'type': 'patient',
            'patient_id': instance.get('patient_id', ''),
            'patient_name': instance.get('patient_name', ''),
            'patient_introduce': instance.get('patient_introduce', ''),
            'prompt': instance.get('prompt', '')
        }
    
    def to_internal_value(self, data):
        """反序列化验证"""
        if not isinstance(data, dict):
            data = json.loads(data) if isinstance(data, str) else {}
        if 'type' not in data:
            data['type'] = 'patient'
        return super().to_internal_value(data)

class PromptSerializer(TypedBaseSerializer):
    """提示词序列化器"""
    prompt_id = serializers.CharField(required=True)
    prompt_type = serializers.CharField(required=True)
    prompt = serializers.CharField(required=True)
    
    def to_representation(self, instance):
        """从实例转换为序列化表示"""
        if hasattr(instance, '__dict__'):
            return {
                'type': 'prompt',
                'prompt_id': instance.prompt_id,
                'prompt_type': instance.prompt_type,
                'prompt': instance.prompt
            }
        return {
            'type': 'prompt',
            'prompt_id': instance.get('prompt_id', ''),
            'prompt_type': instance.get('prompt_type', ''),
            'prompt': instance.get('prompt', '')
        }
    
    def to_internal_value(self, data):
        """反序列化验证"""
        if not isinstance(data, dict):
            data = json.loads(data) if isinstance(data, str) else {}
        if 'type' not in data:
            data['type'] = 'prompt'
        return super().to_internal_value(data)

# 工具函数，用于序列化和反序列化
def serialize_to_json(obj, serializer_class):
    """使用指定的序列化器将对象序列化为JSON"""
    serializer = serializer_class(obj)
    return json.dumps(serializer.data, ensure_ascii=False)

def deserialize_from_json(json_str, serializer_class):
    """使用指定的序列化器从JSON反序列化对象"""
    try:
        data = json.loads(json_str) if isinstance(json_str, str) else json_str
        serializer = serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            return serializer.validated_data
    except Exception as e:
        print(f"反序列化错误: {str(e)}")
        return None