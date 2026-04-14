# 接口概述
用于更新已有记忆库的配置信息，包括记忆库的描述、自定义事件类型、自定义画像类型等内容。请注意，该接口采用全量替换策略，请求中提供的字段将覆盖原有配置，而非在原配置基础上增量修改。未包含在请求体中的配置项将被清空或重置。更新仅针对记忆库结构，之前已经添加的数据不受影响，依然可以正常检索。
# **请求接口**
| **URL** | /api/memory/collection/update | 统一资源标识符 |
| --- | --- | --- |
| **请求方法** | POST | 客户端对记忆库服务器请求的操作类型 |
| **请求头** | Content-Type: application/json | 请求消息类型 |
|  | Authorization: HMAC-SHA256 *** | 基于AK/SK生成的签名信息 |
# 请求参数
更新记忆库时，必须带上全部配置，否则会被覆盖。

* CollectionName 与 ResourceId 至少传一个，用于定位要更新的记忆库
* CollectionType、CollectionModalType、EventType、ProfileType、EnableAssistantIsolation 不可编辑

| **参数名** | **类型** | **是否必须** | **描述** |
| --- | --- | --- | --- |
| CollectionName | String | 否 | 要更新的记忆库的唯一名称。 |
| ProjectName | String | 否 | 项目名称。默认为 default。 |
| ResourceId | String | 否 | 资源 ID。唯一标识符。 |
| Description | String | 否 | 记忆库的描述信息，最多 10000 个字符。 |
| TtlRelative | Integer | 否 | 事件记忆的过期时间，单位为秒。不传则默认永不过期。为保证记忆的完整性，建议不要设置过低的值。范围: (0, 315576000] |
| BuiltinEventTypes | Array of String | 否 | 新的内置事件类型名称列表。提供此字段会覆盖现有的内置事件类型。 |
| BuiltinProfileTypes | Array of String | 否 | 新的内置画像类型名称列表。提供此字段会覆盖现有的内置画像类型。 |
| CustomEventTypeSchemas | Array of EventTypeSchema | 否 | 新的自定义事件类型模式列表。提供此字段会覆盖现有的自定义事件类型。 |
| CustomProfileTypeSchemas | Array of ProfileTypeSchema | 否 | 新的自定义画像类型模式列表。提供此字段会覆盖现有的自定义画像类型。 |
| CpuQuota | Integer | 否 | 创建时默认为1核，可支撑100qps。范围[1, 100]。 |
| Tags | Array of Tag | 否 | 标签，可用于资源管理和分账。 |
| * Key | String | 是 | 标签的键。 |
| * Value | String | 是 | 标签的值。 |
# 响应消息
操作成功时，HTTP状态码为200。
| **字段** | **类型** | **描述** |
| --- | --- | --- |
| ResponseMetadata | Object | 响应元数据信息。 |
| * Region | String | 服务区域，例如"cn-beijing"。 |
| * RequestId | String | 请求唯一标识符。 |
| * Service | String | 服务名称，如"knowledge_base_server"。 |
| * Version | String | API版本号。 |
# 示例代码
## **Python请求**
```Python
import os
import volcenginesdkcore
import volcenginesdkvikingdb
from volcenginesdkcore.rest import ApiException

configuration = volcenginesdkcore.Configuration()
configuration.ak = os.environ.get("VIKINGDB_AK")
configuration.sk = os.environ.get("VIKINGDB_SK")
configuration.region = "cn-beijing"
volcenginesdkcore.Configuration.set_default(configuration)

api_instance = volcenginesdkvikingdb.VIKINGDBApi()

memory_collection_update_request = volcenginesdkvikingdb.MemoryCollectionUpdateRequest(
    collection_name="your_collection_name",
    project_name="default",
    builtin_event_types=["sys_event_v1"],
    builtin_profile_types=["sys_profile_v1"],
    custom_event_type_schemas=[
        volcenginesdkvikingdb.CustomEventTypeSchemaForMemoryCollectionUpdateInput(
            event_type="english_study",
            properties=[
                volcenginesdkvikingdb.PropertyForMemoryCollectionUpdateInput(
                    property_name="question",
                    property_value_type="string",
                    description="助教提出的问题"),
                volcenginesdkvikingdb.PropertyForMemoryCollectionUpdateInput(
                    property_name="answer",
                    property_value_type="string",
                    description="学生的回答"),
                volcenginesdkvikingdb.PropertyForMemoryCollectionUpdateInput(
                    property_name="rating_score",
                    property_value_type="int64",
                    description="学生的评分分数"),
            ]
        )
    ]
)

try:
    api_instance.memory_collection_update(memory_collection_update_request)
except ApiException as e:
    print("Exception when calling api: %s\n" % e)
```


