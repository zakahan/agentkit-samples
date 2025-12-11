import os
import time
import json
# 通过 pip install 'volcengine-python-sdk[ark]' 安装方舟SDK
from volcenginesdkarkruntime import Ark

# 从环境变量中获取 MODEL_AGENT_API_KEY
api_key = os.getenv("MODEL_AGENT_API_KEY")

# 初始化 Ark 客户端
client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=api_key
)

def generate_video_from_images(image_url: str):
    """
    从图片生成视频的工具函数
    :param image_url: 图片地址
    :return: JSON 格式的视频生成结果
    """
    # 检查图片地址是否存在
    if not image_url:
        return json.dumps({"status": "error", "message": "Missing image_url parameter"}, ensure_ascii=False)

    try:
        # 创建视频生成任务，仅包含 image_url
        create_result = client.content_generation.tasks.create(
            model="doubao-seedance-1-0-lite-i2v-250428",
            content=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        )
        
        # 获取任务 ID
        task_id = create_result.id
        
        # 轮询任务状态
        while True:
            get_result = client.content_generation.tasks.get(task_id=task_id)
            status = get_result.status
            
            if status == "succeeded":
                # 将 Pydantic 模型转换为字典
                result_dict = get_result.model_dump()
                print("Result dictionary:", result_dict)  # 打印完整字典以调试
                
                # 提取视频 URL - 根据API响应，视频URL位于content.video_url
                video_url = None
                # 检查content字段
                if "content" in result_dict and isinstance(result_dict["content"], dict):
                    if "video_url" in result_dict["content"]:
                        video_url = result_dict["content"]["video_url"]
                
                # 检查其他可能的位置作为备选
                if not video_url:
                    if "video_url" in result_dict:
                        video_url = result_dict["video_url"]
                    elif "url" in result_dict:
                        video_url = result_dict["url"]
                    # 检查是否content是列表形式
                    elif "content" in result_dict and isinstance(result_dict["content"], list):
                        for item in result_dict["content"]:
                            if isinstance(item, dict):
                                if "video_url" in item:
                                    video_url = item["video_url"]
                                    break
                                elif "url" in item:
                                    video_url = item["url"]
                                    break
                
                return json.dumps({
                    "status": "ok",
                    "task_status": "succeeded",
                    "video_url": video_url
                }, ensure_ascii=False)
            elif status == "failed":
                return json.dumps({
                    "status": "error",
                    "message": f"Video generation failed: {get_result.error}"
                }, ensure_ascii=False)
            else:
                time.sleep(1)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error: {str(e)}"
        }, ensure_ascii=False)
