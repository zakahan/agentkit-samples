# 接口概述
从指定记忆库中检索相关的画像记忆信息，可依据用户提问进行语义相似度检索，并根据查询条件划定查询范围。
# 方法定义
`collection.search_profile_memory(query=None, filter=None, limit=None, headers=None, timeout=None)`
# 请求参数
| **参数** | **类型** | **是否必须** | **描述** |
| --- | --- | --- | --- |
| query | String | 否 | 用户的检索查询语句（最大长度 4000 字符） <br>  <br> * 当传输 query 时，会针对 query 内容对记忆进行语义化匹配召回，召回记忆数量与 limit 值有关； <br> * 当不传 query 时，会返回符合 filter 条件的记忆列表，按照时间顺序返回（优先取最近的），召回记忆数量与 limit 值有关。 |
| filter | Object | 否 | 检索过滤条件和返回设置。 |
| * user_id | String or Array of String | 否 | 用户 ID，支持单个 ID 或 ID 列表。 |
| * assistant_id | String or Array of String | 否 | 助手 ID，支持单个 ID 或 ID 列表。 |
| * primary_key | String or Array of String | 否 | 用于过滤的画像主键表达式。可以是单个或列表，比如画像主键名为kb_id，想查询kb_id为1的数据，则 <br> 检索条件为 primary_key="kb_id=1" |
| * profile_date | String | 否 | 画像对应的记忆检索时间范围。日报用单日日期（如 "2025/12/01"），周报用起止区间（如 "2025/12/01~2025/12/07"），用于过滤并检索该周期内自动更新的画像。 |
| * start_time | Integer | 否 | 检索记忆的起始时间，毫秒级时间戳。 |
| * end_time | Integer | 否 | 检索记忆的终止时间，毫秒级时间戳。 |
| * memory_type | String or Array of String | 是 | 要检索的画像类型名称或它们的列表。 |
| * group_id | String or Array of String | 否 | 用于过滤的群组ID。可以是单个ID或ID列表。 |
| limit | Integer | 否 | 返回的检索结果条数，默认为10，取值范围[1, 5000]。 |
**说明：**

* **检索画像**：user_id 和 assistant_id 至少填写一个，也可同时填写。

# 响应消息
| **字段** | **类型** | **描述** |
| --- | --- | --- |
| code | Integer | 状态码，0 表示成功，其他表示错误。 |
| message | String | 返回信息。 |
| data | Object | 返回的详细检索结果。 |
| * collection_name | String | 被检索的记忆库名称。 |
| * count | Integer | 返回的检索结果数量。 |
| * result_list | Array of Object | 检索结果列表。 |
| * -id | String | 记忆条目（画像实例）的唯一ID。 |
| * -score | Float | 与查询的相关性得分。 |
| * -memory_type | String | 记忆条目的类型（EventType 或 ProfileType）名称。 |
| * -user_id | Array of String | 关联的用户ID列表。 |
| * -assistant_id | Array of String | 关联的助手ID列表。 |
| * -group_id | String | 关联的群组ID。 |
| * -time | Integer | 记忆发生或最后更新的时间戳（毫秒）。 |
| * -status | String | 记忆条目的状态（预留字段）。 |
| * -labels | String | 记忆条目的标签（预留字段）。 |
| * -memory_info | Object | 额外的详细信息。其结构取决于memory_type。 <br> 对于画像，则只包含画像的属性。 例如： <br> ```JSON <br> { <br>     "answer_bad_count": 0, <br>     "answer_good_count": 3, <br>     "count": 3, <br>     "has_been_taught": 0, <br>     "issues": [], <br>     "rating_score_max": 1, <br>     "rating_score_sum": 3 <br> } <br> ``` <br>  |
| * token_usage | Integer | 本次检索消耗的token数量。 |
| request_id | String | 标识每个请求的唯一ID。 |
# 示例代码
## **Python请求**
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
    assistant_id = "sdk_example_assistant"

    profile_id = None
    try:
        created = collection.add_profile(
            profile_type="profile_v1",
            user_id=user_id,
            assistant_id=assistant_id,
            memory_info={"user_profile": "用户名字: 小明; 城市: 上海; 偏好: 手冲咖啡"},
        )
        profile_id = (created.get("data") or {}).get("profile_id")

        time.sleep(5)

        result = collection.search_profile_memory(
            query="小明",
            filter={"user_id": user_id, "assistant_id": assistant_id, "memory_type": ["profile_v1"]},
            limit=10,
        )

        print("search_profile_memory response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("user_id:", user_id)
        print("assistant_id:", assistant_id)
    finally:
        if profile_id:
            collection.delete_profile(profile_id=profile_id)


if __name__ == "__main__":
    main()
```


