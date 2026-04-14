# 接口概述
查询指定session的详细信息，包括生成的事件记忆列表，原始消息，token消耗。
# 方法定义
`collection.get_session_info(session_id, headers=None, timeout=None)`
# 请求参数
| **参数** | **类型** | **是否必须** | **参数说明** |
| --- | --- | --- | --- |
| session_id | String | 是 | 当前对话或消息批次的会话 ID，长度要求：[1, 128]。 |
# 响应消息
| **参数** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码，0表示成功，其他表示错误。SDK 直接透传服务端响应。 |
| message | String | 返回信息，成功时通常为 "success"。 |
| data | Object | 返回的详细数据。 |
| * usage | Object | 此session输入的token消耗 |
| * -embedding_tokens | Integer | embedding模型的token总消耗。 |
| * -llm_input_tokens | Integer | LLM输入的token总消耗。 |
| * -llm_output_tokens | Integer | LLM输出的token总消耗。 |
| * -llm_input_tokens_details | Object | LLM输入的token消耗明细。 |
| * -cached_tokens | Integer | LLM输入的cached token消耗。 |
| * event_memory | Array of Object | 生成的事件记忆列表。 |
| * -event_id | String | 事件记忆的id。 |
| * -event_type | String | 事件类型的名称。 |
| * -memory_info | Object | 事件记忆的内容。包含： <br>  <br> * 原始的多轮对话信息。 <br> * 事件的属性：对于内置事件sys_event_v1，只有summary；对于内置事件sys_profile_collect_v1，只有user_profile；对于自定义事件，按照自定义的属性字段展示。 |
| * -user_id | Array of String | 事件归属的user_id。 |
| * -assistant_id | Array of String | 事件归属的 assistant_id。 |
| * -time | Integer | 记忆的创建时间，毫秒级时间戳。 |
| * messages | Array of Object | 对话消息列表. |
| * -content | String | 发言内容。 |
| * -message_id | String | 对话id。 |
| * -role | String | 发言人角色。 |
| * -role_id | String | 发言人ID |
| * -role_name | String | 发言人名称。 |
| * -time | Integer | 发言时间，毫秒级时间戳。 |
| * session_id | String | 当前对话或消息批次的会话 ID。 |
| * status | String | 当前session的处理进度，枚举值：processing, success, failed。 |
| * time | Integer | 当前session的统一发生时间，毫秒级时间戳。 |
| * user_ids | Array of String | 当前session关联的user列表。 |
| * assistant_ids | Array of String | 当前session关联的 assistant 列表。 |
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


def poll_session_info(collection, session_id: str, timeout_s: int = 60, interval_s: float = 2.0):
    deadline = time.time() + timeout_s
    last = None
    while time.time() < deadline:
        info = collection.get_session_info(session_id=session_id)
        last = info
        status = None
        if isinstance(info, dict):
            status = (info.get("data") or {}).get("status")
        if status in ("success", "failed"):
            return info
        time.sleep(interval_s)
    return last


def main() -> None:
    client = build_client()

    collection = client.get_collection(collection_name="your_collection", project_name="default")

    now_ms = int(time.time() * 1000)
    session_id = f"sdk_example_session_{now_ms}"

    collection.add_session(
        session_id=session_id,
        messages=[
            {"role": "user", "content": "请记住我住在上海。"},
            {"role": "assistant", "content": "好的，我记住你住在上海。"},
        ],
        metadata={
            "default_user_id": f"sdk_example_user_{now_ms}",
            "default_assistant_id": "sdk_example_assistant",
            "time": now_ms,
        },
    )

    info = poll_session_info(collection, session_id=session_id)
    print("get_session_info response:")
    print(json.dumps(info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```


