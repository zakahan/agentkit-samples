# 概述
用于单条删除已写入记忆库的事件记忆。
# 方法定义
`collection.delete_event(event_id, headers=None, timeout=None)`
# **请求参数**
| **参数** | **类型** | **是否必须** | **参数说明** |
| --- | --- | --- | --- |
| event_id | String | 是 | 需要删除的事件记忆id。 |
# 响应消息
| **参数** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码，0表示成功，其他表示错误。 |
| message | String | 返回信息，成功时通常为 "success"。失败则返回原因。 |
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
        memory_info={"summary": "用户提到自己喜欢跑步，并计划下周参加马拉松。"},
    )

    event_id = (created.get("data") or {}).get("event_id")
    if not event_id:
        raise RuntimeError(f"add_event did not return event_id, response={created}")

    deleted = collection.delete_event(event_id=event_id)
    print("delete_event response:")
    print(json.dumps(deleted, indent=2, ensure_ascii=False))
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
    "request_id":"021695029537650fd001de666660000000000000000000230da93"
}
```


