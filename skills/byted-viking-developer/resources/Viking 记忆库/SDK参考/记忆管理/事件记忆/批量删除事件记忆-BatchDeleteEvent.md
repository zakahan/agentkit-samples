# 概述
用于批量删除已写入记忆库的事件记忆。
# 方法定义
`collection.batch_delete_event(filter=None, delete_type=None, headers=None, timeout=None)`
# **请求参数**
| **参数** | **类型** | **是否必须** | **参数说明** |
| --- | --- | --- | --- |
| filter | Object | 否 | 删除记忆的过滤条件。 |
| * user_id | String or Array of String | 否 | 用户 ID，支持单个 ID 或 ID 列表。和 assistant_id 至少填写一个，也可以同时填写。 |
| * assistant_id | String or Array of String | 否 | 助手 ID，支持单个 ID 或 ID 列表。和 user_id 至少填写一个，也可以同时填写。 |
| * group_id | String or Array of String | 否 | 群组 ID，支持单个 ID 或 ID 列表。 |
| * event_type | String or Array of String | 否 | 事件类型。 |
| delete_type | String | 是 | 记忆的删除方式。默认是full模式。 <br>  <br> * full：全局删除整条记忆 |
**说明：**

* user_id 和 assistant_id 至少填写一个，也可以同时填写。

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
    user_id = f"sdk_example_user_{now_ms}"

    for i in range(2):
        collection.add_event(
            event_type="event_v1",
            user_id=user_id,
            assistant_id="sdk_example_assistant",
            memory_info={"summary": f"用户事件样例 {i + 1}: 计划周末去咖啡店。"},
        )

    deleted = collection.batch_delete_event(
        filter={"user_id": user_id, "event_type": "event_v1"},
        delete_type="full",
    )

    print("batch_delete_event response:")
    print(json.dumps(deleted, indent=2, ensure_ascii=False))
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


