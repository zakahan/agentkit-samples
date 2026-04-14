# 概述
用于单条删除已写入记忆库的画像记忆。
# 方法定义
`collection.delete_profile(profile_id, headers=None, timeout=None)`
# **请求参数**
| **参数** | **类型** | **是否必须** | **参数说明** |
| --- | --- | --- | --- |
| profile_id | String | 是 | 需要删除的画像记忆id。 |
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

    created = collection.add_profile(
        profile_type="profile_v1",
        user_id=user_id,
        assistant_id="sdk_example_assistant",
        memory_info={"user_profile": "基础信息: 城市 北京/偏好 篮球"},
    )

    profile_id = (created.get("data") or {}).get("profile_id")
    if not profile_id:
        raise RuntimeError(f"add_profile did not return profile_id, response={created}")

    deleted = collection.delete_profile(profile_id=profile_id)
    print("delete_profile response:")
    print(json.dumps(deleted, indent=2, ensure_ascii=False))
    print("profile_id:", profile_id)
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
    "data": {
        "resource_id": "kb-8349ef57441ab57"
    },
    "request_id":"021695029537650fd001de666660000000000000000000230da93"
}
```


