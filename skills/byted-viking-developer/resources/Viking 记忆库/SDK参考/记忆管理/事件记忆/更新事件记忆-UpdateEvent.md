# 概述
用于更新已写入记忆库的事件记忆。
# 方法定义
`collection.update_event(event_id, memory_info, user_id=None, assistant_id=None, headers=None, timeout=None)`
# **请求参数**
| **参数** | **类型** | **是否必须** | **参数说明** |
| --- | --- | --- | --- |
| event_id | String | 是 | 需要更新的事件记忆id。 |
| memory_info | Object | 是 | 事件记忆的内容。对于内置事件sys_event_v1，只有summary；对于内置事件sys_profile_collect_v1，只有user_profile；对于自定义事件，按照自定义的属性字段展示。 <br> **需要注意的是，其格式必须遵循在记忆库中已定义的格式。如：** <br>  <br> * 内置事件sys_event_v1： <br>  <br> { <br> "summary": "今天我和好朋友一起过生日。" <br> } <br>  <br> * 自定义事件： <br>  <br> { <br> "knowledge_point_name": "今天我和好朋友一起过生日。", <br> "rating_score": 9 <br> } |
| user_id | Array of String | 否 | 事件关联的user_id。 |
| assistant_id | Array of String | 否 | 事件关联的assitant_id。 |
# 响应消息
| **参数** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码，0表示成功，其他表示错误。 |
| message | String | 返回信息，成功时通常为 "success"。失败则返回原因。 |
| data | Object | 返回的详细数据，成功添加消息时此字段通常为空。 |
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

    created = collection.add_event(
        event_type="event_v1",
        user_id=user_id,
        assistant_id="sdk_example_assistant",
        memory_info={"summary": "用户表示明天要去看一场比赛，并且很期待。"},
    )

    event_id = (created.get("data") or {}).get("event_id")
    if not event_id:
        raise RuntimeError(f"add_event did not return event_id, response={created}")

    time.sleep(5)

    updated = collection.update_event(
        event_id=event_id,
        memory_info={
            "summary": "用户表示明天要去看一场比赛，并且很期待；还提到想带朋友一起去。",
        },
        user_id=[user_id],
        assistant_id=["sdk_example_assistant"],
    )

    print("update_event response:")
    print(json.dumps(updated, indent=2, ensure_ascii=False))
    print("event_id:", event_id)
    print("user_id:", user_id)


if __name__ == "__main__":
    main()
```

## 响应消息
### **执行成功返回**
```Shell
{
    "code":0,
    "message":"success",
    "request_id":"0216950295xxxxxxx"
}
```


