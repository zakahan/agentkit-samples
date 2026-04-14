# 概述
用于添加事件记忆。
# 方法定义
`collection.add_event(event_type, memory_info, user_id=None, assistant_id=None, group_id=None, headers=None, timeout=None, update_profiles=None)`
# **请求参数**
| **参数** | **类型** | **是否必须** | **参数说明** |
| --- | --- | --- | --- |
| event_type | String | 是 | 事件类型。 |
| memory_info | Object | 是 | 事件记忆的内容。对于内置事件sys_event_v1，只有summary；对于自定义事件，按照自定义的属性字段展示。 <br> **需要注意的是，其格式必须遵循在记忆库中已定义的格式。** |
| update_profiles | Array of Object | 否 | 需要更新的画像信息列表。 |
| * profile_type | String | 是 | 画像类型名称，必须是当前事件类型关联的画像类型。 |
| * primary_key | String | 否 | 画像主键。对于没有另外设置主键的画像（默认的user_id主键），primary_key 不需要填写。 <br>  <br> * 单一主键：“primary_key1=1” <br> * 联合主键：“primary_key1=1&primary_key2=1” |
| user_id | String | 否 | 事件关联的用户ID。和assistant_id至少填写一个。 |
| assistant_id | String | 否 | 事件关联的助手ID。和user_id至少填写一个。 |
| group_id | String | 否 | 群组ID。用于隔离不同的会话或场景。 |
# 响应消息
| **参数** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码，0表示成功，其他表示错误。 |
| message | String | 返回信息，成功时通常为 "success"。 |
| data | Object | 返回的详细数据。 |
| * event_id | String | 事件的唯一ID。 |
| * memory_info | Object | 事件记忆的内容。 |
| * event_type | String | 事件类型。 |
| usage | Object | 事件记忆写入消耗的token。 |
| * embedding_tokens | Integer | Embedding token消耗。 |
| request_id | String | 标识每个请求的唯一ID。 |
# 完整示例
## 请求消息
### **Python请求**
```Python
import json
import os
import time

from vikingdb import APIKey
from vikingdb.memory import VikingMem


def build_client() -> VikingMem:
    api_key = os.getenv("MEMORY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing credentials: set MEMORY_API_KEY")
    auth = APIKey(api_key=api_key)

    return VikingMem(
        host="api-knowledgebase.mlp.cn-beijing.volces.com",
        region="cn-beijing",
        auth=auth,
        scheme="http",
    )


def main() -> None:
    client = build_client()

    collection = client.get_collection(collection_name="your_collection", project_name="default")

    now_ms = int(time.time() * 1000)
    user_id = f"sdk_example_user_{now_ms}"

    result = collection.add_event(
        event_type="event_v1",
        user_id=user_id,
        assistant_id="sdk_example_assistant",
        memory_info={"summary": "用户提到自己喜欢手冲咖啡，并计划周末去尝试一家新的咖啡店。"},
    )

    print("add_event response:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("user_id:", user_id)
    if isinstance(result, dict):
        print("event_id:", (result.get("data") or {}).get("event_id"))


if __name__ == "__main__":
    main()
```

## 响应消息
### **执行成功返回**
```Shell
{
     'code': 0, 
     'data': {
         'event_id': 'xxxxxxxxxfc4461e36a16_0', 
         'event_type': 'sys_event_v1', 
         'memory_info': {'summary': '小明向助手分享了今年校庆打算和朋友回校重走校园路线、重温美食的计划，还提及朋友曾送的小夜灯，两人回忆起大学室友情。助手提议帮小明整理回忆成一篇名为《403的黄光》的小文送给阿强，小明表示同意并打算拍摄龟背竹新叶续写。最后，两人约定等小明整理好照片后一起把“403时间线”做成一张长图。'}, 
         'usage': {
         'embedding_tokens': 226
         }
     }, 
     'message': 'success', 
     'request_id': 'xxxxxxxxxxf73ed50'
 }
```


