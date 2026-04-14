# 概述
用于批量删除已写入记忆库的画像记忆。
# 方法定义
`collection.batch_delete_profile(filter=None, headers=None, timeout=None)`
# **请求参数**
| **参数** | **类型** | **是否必须** | **参数说明** |
| --- | --- | --- | --- |
| filter | Object | 否 | 删除记忆的过滤条件。 |
| * user_id | String or Array of String | 是 | 用于过滤的用户ID。可以是单个ID或ID列表。 |
| * assistant_id | String or Array of String | 否 | 用于过滤的助手ID。可以是单个ID或ID列表。 |
| * profile_type | String or Array of String | 否 | 用于过滤的画像类型。 |
# 响应消息
| **参数** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码，0表示成功，其他表示错误。 |
| message | String | 返回信息，成功时通常为 "success"。 |
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
    user_ids = [f"sdk_example_user_{now_ms}_a", f"sdk_example_user_{now_ms}_b"]

    for user_id in user_ids:
        collection.add_profile(
            profile_type="profile_v1",
            user_id=user_id,
            assistant_id="sdk_example_assistant",
            memory_info={"user_profile": f"基础信息: user_id={user_id}"},
        )

    deleted = collection.batch_delete_profile(
        filter={
            "user_id": user_ids,
            "profile_type": ["profile_v1"],
        }
    )

    print("batch_delete_profile response:")
    print(json.dumps(deleted, indent=2, ensure_ascii=False))
    print("user_ids:", user_ids)


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


