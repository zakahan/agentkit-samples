# 概述
用于手动触发画像记忆的更新。
# 方法定义
`collection.trigger_update_profile(update_profile_type=None, filters=None, headers=None, timeout=None)`
# **请求参数**
| **参数** | **类型** | **是否必须** | **参数说明** |
| --- | --- | --- | --- |
| update_profile_type | Array of String | 否 | 需要更新的画像记忆类型。不传时默认会更新所有画像类型。 |
| filters | Object | 否 |  |
| * user_id | String or Array of String | 否 | 需要更新画像的用户范围，不传时默认更新全部用户。最多传1000个，超过时建议并行调用。 |
| * end_time | Integer | 否 | 更新画像的记忆截止时间。即此次事件记忆的数据范围为“上次更新的时间戳至end_time”。建议设置比当前时间早，确保更新数据的完整性。 |
# 响应消息
| **参数** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码，0表示成功，其他表示错误。 |
| message | String | 返回信息，成功时通常为 "success"。失败则返回原因。 |
| data | Object | 返回的详细数据。 |
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

    collection.add_profile(
        profile_type="profile_v1",
        user_id=user_id,
        assistant_id="sdk_example_assistant",
        memory_info={"user_profile": "基础信息: 喜好 旅行/摄影"},
    )

    time.sleep(5)

    triggered = collection.trigger_update_profile(
        update_profile_type=["profile_v1"],
        filters={"user_id": [user_id]},
    )

    print("trigger_update_profile response:")
    print(json.dumps(triggered, indent=2, ensure_ascii=False))
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


