from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
import tempfile
import zipfile
import os
import json
from .services import UserController, ChatHistoryController, PatientController, PromptController, ChatRobotService
from .models import ChatHistory

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

@api_view(['POST'])
def register(request):
    # 注册所需参数
    data = request.data
    account = data.get("account")
    password = data.get("password")
    
    if not account or not password:
        return Response(
            {"success": False, "msg": "账号和密码不能为空"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 注册，并返回结果
    result = UserController.register(account, password)
    if result["success"]:
        return Response(
            {"success": True, "msg": result["msg"]},
            status=status.HTTP_201_CREATED
        )
    else:
        return Response(
            {"success": False, "msg": result["msg"]},
            status=status.HTTP_400_BAD_REQUEST
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
    从MongoDB导出聊天历史为zip文件并提供下载 
    """ 
    # 创建临时文件用于存储zip 
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file: 
        temp_file_path = tmp_file.name 
    
    # 创建zip文件 
    with zipfile.ZipFile(temp_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf: 
        # 从MongoDB获取所有聊天历史
        from .models import mongo_db
        chat_histories = mongo_db.find('chat_histories', {})
        
        # 将每条聊天历史保存为单独的JSON文件
        for history in chat_histories:
            chat_id = history.get('chat_history_id')
            if chat_id:
                # 创建临时JSON文件
                with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as json_file:
                    json_path = json_file.name
                    # 写入JSON数据
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(history, f, ensure_ascii=False, indent=2)
                    
                    # 添加到zip文件
                    zipf.write(json_path, f'chat_history_{chat_id}.json')
                    
                    # 删除临时JSON文件
                    os.unlink(json_path)
    
    # 返回文件以供下载
    response = FileResponse(open(temp_file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = 'attachment; filename=chat_histories.zip'
    
    # 添加一个回调，在响应结束后删除临时文件
    def close_and_cleanup():
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    
    response.close = close_and_cleanup
    
    return response