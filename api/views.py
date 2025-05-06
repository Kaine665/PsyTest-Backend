from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
import tempfile
import zipfile
import os
from .services import UserService as UserController, ChatService as ChatHistoryController, PatientService as PatientController, PromptService as PromptController, ChatRobotService

# Create your views here.
@api_view(['POST'])
def login(request):
    # 登录所需参数
    data = request.data
    account = data["account"]
    password = data["password"]
    # 登录，并返回结果
    result = UserController.login(account, password)
    if result["success"]:
        return Response(
            {"success": True, "msg": result["msg"], "account": account},
            status = status.HTTP_200_OK
        )
    else:
        return Response(
            {"success": False, "msg": result["msg"]},
            status= status.HTTP_401_UNAUTHORIZED
        )
        
@api_view(["GET"])
def get_chat_history(request, chat_history_id):
    result = ChatHistoryController.get_history(chat_history_id)
    if result["success"]:
        return Response(result, status=status.HTTP_200_OK)
    else: 
        return Response(result, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def delete_chat_history(request):
    """
    前端传入：chat_history_id
    后端删除对应的历史聊天记录
    """
    chat_history_id = request.data.get("chat_history_id")
    if not chat_history_id:
        return Response({"success": False, "msg": "未提供chat_history_id"}, status=status.HTTP_400_BAD_REQUEST)
    result = ChatHistoryController.delete_history(chat_history_id)
    if result.get("success"):
        return Response({"success": True, "msg": "删除成功"}, status=status.HTTP_200_OK)
    else:
        return Response({"success": False, "msg": result.get("msg", "删除失败")}, status=status.HTTP_400_BAD_REQUEST)
       
@api_view(["GET"])
def get_chat_histories_by_user(request, user_id):
    result = ChatHistoryController.get_histories_by_user(user_id)
    return Response(result, status=status.HTTP_200_OK)

@api_view(["POST"])
def save_chat_history(request):
    data = request.data
    result = ChatHistoryController.save_history(data)
    if result["success"]:
        return Response(result, status=status.HTTP_200_OK)
    else: 
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def load_chat_page(request):
    """
    前端传入：chat_history_id, patient_id, prompt_id
    后端返回：对应聊天记录
    """
    data = request.data
    chat_history_id = data.get("chat_history_id")
    
    # 通过 ChatHistoryController 获取聊天内容
    result = ChatHistoryController.get_history(chat_history_id)
    if not result["success"]:
        return Response({'messages': [{"role": "user", "content": "对话不存在，返回空消息"}]}, status=status.HTTP_200_OK)
    
    chat_history = result["data"]
    
    return Response({'messages': chat_history["content"]}, status=status.HTTP_200_OK)

@api_view(['POST'])
def process_message(request):
    """
    前端传入：inputValue
    后端返回：AI来访者回复
    """
    data = request.data
    chat_history_id = data.get("chat_history_id")
    input_value = data.get("inputValue")
    result = ChatRobotService.process_message(chat_history_id, input_value)
    if result["success"]:
        return Response({'messages': result["data"]}, status=status.HTTP_200_OK)
    else:
        return Response({'error': result["msg"]}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['POST'])
def get_feedback(request):
    """
    前端传入：inputValue
    后端返回：AI督导反馈
    """
    data = request.data
    chat_history_id = data.get("chat_history_id")
    input_value = data.get("inputValue")
    result = ChatRobotService.get_feedback(chat_history_id, input_value)
    if result["success"]:
        return Response({'messages': result["data"]}, status=status.HTTP_200_OK)
    else:
        return Response({'error': result["msg"]}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(["POST"])
def post_messages(request):
    """
    前端传入：messagesToSend, chat_history_id
    后端追加消息到聊天记录
    """
    data = request.data
    chat_history_id = data.get("chat_history_id")
    messages_to_send = data.get("messagesToSend")
    result = ChatHistoryController.append_messages(chat_history_id, messages_to_send)
    if result["success"]:
        return Response({'messages': 'Yes'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': result["msg"]}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def get_patient(request, patient_id):
    result = PatientController.get_patient(patient_id)
    if result["success"]:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
def get_all_patients(request):
    result = PatientController.get_all_patients()
    return Response(result, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_prompt(request, prompt_id):
    result = PromptController.get_prompt(prompt_id)
    if result["success"]:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)
    
@api_view(["GET"])
def get_all_prompts(request):
    result = PromptController.get_all_prompts()
    return Response(result, status=status.HTTP_200_OK)

@api_view(["GET"])
def export_chat_histories(request): 
    """ 
    将MongoDB中的聊天历史导出为zip文件并提供下载 
    """ 
    from .models import chat_collection
    import tempfile
    import zipfile
    import json
    import os
    
    # 创建临时目录用于存储导出的JSON文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 从MongoDB获取所有聊天历史并保存为JSON文件
        cursor = chat_collection.find({})
        for doc in cursor:
            # 移除MongoDB的_id字段
            if '_id' in doc:
                del doc['_id']
            
            # 写入临时文件
            file_path = os.path.join(temp_dir, f"chat_history_{doc['chat_history_id']}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
        
        # 创建临时文件用于存储zip 
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file: 
            temp_file_path = tmp_file.name 
        
        # 创建zip文件 
        with zipfile.ZipFile(temp_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf: 
            for root, dirs, files in os.walk(temp_dir): 
                for file in files: 
                    file_path = os.path.join(root, file) 
                    # 计算文件在压缩包内的路径 
                    arcname = os.path.relpath(file_path, temp_dir) 
                    zipf.write(file_path, arcname) 
    
    # 返回文件以供下载 
    response = FileResponse(open(temp_file_path, 'rb'), as_attachment=True) 
    response['Content-Disposition'] = 'attachment; filename=chat_histories.zip' 
    
    # 添加一个回调，在响应结束后删除临时文件 
    def close_and_cleanup(): 
        if os.path.exists(temp_file_path): 
            os.unlink(temp_file_path) 
    
    response.close = close_and_cleanup 
    
    return response