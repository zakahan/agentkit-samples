# 接口概述
向指定的记忆库中添加一批消息（通常是多轮对话），系统将根据记忆库的记忆抽取配置对这些消息进行处理和存储，形成结构化的记忆事件，并可能更新关联的画像。
# 方法定义
`collection.add_session(session_id, messages, metadata=None, profiles=None, headers=None, timeout=None, store_file=None)`
# 请求参数
| **参数** | **类型** | **是否必须** | **描述** |
| --- | --- | --- | --- |
| session_id | String | 是 | 当前对话或消息批次的会话 ID。长度要求：[1, 128]，只能使用英文字母、数字、下划线，并以英文字母开头。未填写则由服务端自动生成。 |
| messages | Array of Object | 是 | 要添加的多轮对话消息列表。 |
| * role | String | 是 | 发言人角色，可选值为 "user", "assistant", "system"。 |
| * content | String | List[Object] | 是 <br>  <br> * type：可为 "text", "image_url", "input_image" <br> * image_url：String <br> * text：String <br>  <br> 例如： <br> ```JSON <br> "content": [ <br>  { "type": "image_url", "image_url": { "url": "https://memory-demo.tos-cn-beijing.volces.com/sandwich.jpeg" } }, <br>  { "type": "text", "text": "刚刚吃了一个三明治" } <br> ] <br> ``` <br>  <br> 图片上传限制： <br>  <br> * Session 中图片数量不能超过 20 张 <br> * url 必须是可下载的链接 <br> * 单张图片不能超过 10M <br> * 支持图片格式：jpeg、png、webp、bmp、tiff、ico <br> * 宽高比：限制在范围[1/100, 100]内 <br> * 边长限制在 [10, 6000] 像素范围内 |
| * role_id | String | 否 | 群聊场景下的发言人 ID。若该发言人与 default_user_id 或 default_assistant_id 相同，则无需传入。 |
| * role_name | String | 否 | 群聊场景下的发言人名称。若该发言人与 default_user_name 或 default_assistant_name 相同，则无需传入。 |
| * time | Integer | 否 | 发言时间，毫秒级时间戳。 |
| store_file | Bool | 否 | 是否存储原始文件。默认值 False，即不存储，则原始文件仅用于抽取记忆。填写True时，则原始文件会进行存储并在检索时返回。 |
| metadata | Object | 否 | 用于设定这批消息的元数据信息。 |
| * default_user_id | String | 是 | 消息列表中 'user' 角色的默认ID。如果消息中未指定role_id，则使用此值。 |
| * default_user_name | String | 否 | 消息列表中 'user' 角色的默认名称。 |
| * default_assistant_id | String | 是 | 消息列表中 'assistant' 角色的默认ID。如果消息中未指定role_id，则使用此值。 |
| * default_assistant_name | String | 否 | 消息列表中 'assistant' 角色的默认名称。 |
| * time | Integer | 是 | 这批消息的统一发生时间，毫秒级时间戳。（如果单条消息中也包含time，则单条消息的 time 优先。） |
| * group_id | String | 否 | 群组ID，用于标记消息所属的业务群组。 |
| extract_memory_type | Array of String | 否 | 此次数据写入需要抽取的记忆类型。填写事件或画像类型的名称，可以是多个值。不传时默认会抽取所有类型的记忆。 |
| profiles | Array of Object | 否 | 需要特别关注或更新的画像信息列表。系统会尝试将处理后的事件与这些画像关联。 |
| * profile_type | String | 是 | 画像类型名称，必须是记忆库中已定义的画像类型。 |
| * profile_scope | Array of Object | 是 | 具体的画像实例列表。每个对象包含用于唯一标识和定义该画像实例的属性，例如: {"id": 1, "knowledge_point_name": "taco"} |
| ttl_absolute | Integer | 否 | 事件记忆的过期时间，绝对时间，填写时间戳，精确到毫秒级。 <br> 相对时间和绝对时间填写即可。 <br>  <br> * 都填写时，取绝对时间 <br> * 都不填写时，取记忆库的过期配置 <br> * 限制: ttl_absolute - metadata.time ∈ (0, 315576000 * 1000] <br> * 限制：如果messages 中的time 不为空，ttl_absolute - message.time ∈ (0, 315576000 * 1000] |
| ttl_relative | Integer | 否 | 事件记忆的过期时间，相对时间，单位为秒。限制: (0, 315576000] |
**注意**：

* 调用 add_session 接口时，若使用相同的 session_id，会覆盖该对话之前生成的事件版本，并从画像中撤回之前生成的事件。建议使用 **UUID** 动态生成 session_id，确保每次会话独立；只有在确实需要覆盖时才重复使用。
* 当需要传入结构化的字段时（如用户行为数据、日志数据），可以以 schema说明+字段数据 的形式写入，如：

```JSON
"messages": [
        {"role": "user", "content": "[schema说明。bhv_time：行为时间/bhv_type：行为类型，包括open打开AI助手、chat和AI助手对话/stay_time：当前行为的停留时长]bhv_time:2025-09-21 10:00:00/bhv_type:open/user_id:xxx/stay_time：100s"}
    ]
```


* profile_type需要为extract_memory_type里画像类型的子集。
* 只有在 messages 中同时传入 user 和 assistant 的消息时，画像和事件才会正确归属用户和助手。接口不会仅依赖 metadata 中的 ID 进行关联；如果只传 user 消息，事件不会关联到 metadata 中的 assistant。
* 记忆的隔离机制：
   * 事件：不同assistant、group相关的 message 生成的事件，会带上对应的标识，检索时可使用对应的参数进行过滤。
   * 画像：画像的隔离分为两层：
      * group：不同group生成的画像是完全隔离的（注意，group不代表群聊，只有在需要做画像隔离时，才建议使用group）
      * assistant：如果画像选择了按照 assistant 隔离，那么在同一group下，不同 assistant 和用户的消息生成的画像是完全隔离的；如果原始消息中没有传入 assistant，那么就会生成不关联 assistant 的画像（assistant_id=""）。

# 响应消息
| **字段** | **类型** | **描述** |
| --- | --- | --- |
| code | Integer | 状态码，0表示成功，其他表示错误。 |
| message | String | 返回信息，成功时通常为 "success"。 |
| data | Object | 返回的详细数据。 |
| * session_id | string | 记忆库服务自动生成session ID |
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
    session_id = f"sdk_example_session_{now_ms}"
    user_id = f"sdk_example_user_{now_ms}"
    assistant_id = "sdk_example_assistant"

    result = collection.add_session(
        session_id=session_id,
        messages=[
            {"role": "user", "content": "我喜欢喝手冲咖啡，你能记住吗？"},
            {"role": "assistant", "content": "当然可以，我会记住你喜欢手冲咖啡。"},
        ],
        metadata={
            "default_user_id": user_id,
            "default_assistant_id": assistant_id,
            "time": now_ms,
        },
    )

    print("add_session response:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("session_id:", session_id)
    print("user_id:", user_id)
    print("assistant_id:", assistant_id)


if __name__ == "__main__":
    main()
```


