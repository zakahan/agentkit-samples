# 概述
用于添加画像记忆。
# 方法定义
`collection.add_profile(profile_type, memory_info, user_id=None, assistant_id=None, group_id=None, is_upsert=False, headers=None, timeout=None)`
# **请求参数**
| **参数** | **类型** | **是否必须** | **参数说明** |
| --- | --- | --- | --- |
| profile_type | String | 是 | 画像类型。 |
| memory_info | Object | 是 | 画像记忆的内容。对于内置画像sys_profile_v1只有user_profile；对于自定义画像，按照自定义的属性字段写入。**需要注意的是，其格式必须遵循在记忆库中已定义的格式。** |
| user_id | String | 是 | 画像关联的用户ID。 |
| assistant_id | String | 否 | 画像关联的助手ID。 <br>  <br> * 对于按 assistant 隔离的画像，必填，可填写""或有效值 <br> * 对于不按 assistant 隔离的画像，若填写 assistant_id 会报错 |
| group_id | String | 否 | 群组ID。用于隔离不同的会话或场景。 |
| is_upsert | Boolean | 否 | 已存在记忆是否使用本次写入进行更新，默认为false，即不更新。 <br>  <br> * false：查找是否存在记录，存在则报错，不存在则新增。 <br> * true：先查找是否存在记录，存在则更新，不存在则新增。 |
# 响应消息
| **参数** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码，0表示成功，其他表示错误。 |
| message | String | 返回信息，成功时通常为 "success"。 |
| data | Object | 返回的详细数据。 |
| * profile_id | String | 画像的唯一ID。 |
| * memory_info | Object | 画像记忆的内容。 |
| * primary_key | String | 画像主键。 |
| * profile_type | String | 画像类型。 |
| usage | Object | 画像记忆写入消耗的token。 |
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

    result = collection.add_profile(
        profile_type="profile_v1",
        user_id=user_id,
        assistant_id="sdk_example_assistant",
        memory_info={"user_profile": "基础信息: 性别 女/年龄 28/偏好 手冲咖啡/城市 上海"},
    )

    print("add_profile response:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("user_id:", user_id)
    if isinstance(result, dict):
        print("profile_id:", (result.get("data") or {}).get("profile_id"))


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
        "profile_id": "68a6a078f2b275b6a41fec42",
        "primary_key":"",
        "profile_type": "sys_profile_v1",
        "memory_info":{
            "user_profile": "基础信息:性别 女/年龄 28/家乡 广州/职业 产品经理"  
        },
        "usage": {
            "embedding_tokens":68
        }
    }
    "request_id":"021695029537650fd001de666660000000000000000000230da93"
}
```


