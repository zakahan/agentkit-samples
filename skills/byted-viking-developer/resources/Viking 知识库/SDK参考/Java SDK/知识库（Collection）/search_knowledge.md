# 概述
search_knowledge 用于对知识库进行检索和前后处理，当前会默认对原始文本加工后的知识内容进行检索。
# **请求参数**
| **参数** | **子参数** | **类型** | **是否必选** | **默认值** | **参数说明** |
| --- | --- | --- | --- | --- | --- |
| collectionName | -- | String | 否 | -- | **知识库名称** |
| projectName | -- | String | 否 | default | **知识库所属项目，获取方式参见文档**[API 接入与技术支持](/c8p1dfoq/y97x844a) <br> 若不指定该字段，则默认在 default 项目下检索。 <br> 若需要操作指定项目下的知识库，需正确配置该字段。 |
| resourceId | -- | String | 否 | -- | **知识库唯一 id** <br> 可选择直接传 ResourceID，或同时传 CollectionName 和 ProjectName 作为知识库的唯一标识 |
| query | -- | String | 是 | -- | **检索文本** <br>  <br> * 最大可输入长度为 8000，query 长度 > 8000 时，接口报错 <br> * 所选 embedding 模型输入最大长度 < query 长度 < 8000 时，query 按所选模型自动截断 <br> * query 长度 < 所选 embedding 模型输入最大长度时，正常检索返回目标切片 |
| imageQuery | -- | String | 否 | -- | **检索图片** <br> 支持图片 URL 或 Base64 编码，详细要求见[图片像素说明](https://www.volcengine.com/docs/82379/1409291?lang=zh#7a10f532)和[图片文件格式](https://www.volcengine.com/docs/82379/1409291?lang=zh#5c068efa) <br>  <br> * 图片 URL 传入：适用于图片文件已存在公网可访问 URL 的场景，单张图片小于 10 MB <br> * Base64 编码传入：适用于图片文件较小的场景，支持 **JPEG、PNG、WebP、BMP** 四种格式的 Base64 编码，单张图片小于 3 MB，请求体不能超过 4 MB |
| limit | -- | Integer | 否 | 10 | **检索结果数量** <br>  <br> * 数量要求：[1, 1000] |
| queryParam |  | Map<String, Object> | 否 |  | **检索的过滤和返回设置** |
|  | doc_filter | map | 否 | -- | **检索过滤条件** <br>  <br> * 支持对 doc 的 meta 信息过滤 <br> * 详细使用方式和支持字段见[filter 表达式](https://www.volcengine.com/docs/84313/1419289#filter-%E8%A1%A8%E8%BE%BE%E5%BC%8F)，可支持对 doc_id 做筛选 <br> * 此处用于过滤的字段，需要在 collection/create 时添加到 index_config 的 fields 上 <br>  <br> 例如： <br> 单层 filter： <br> ```json <br> doc_filter = { <br>      "op": "must", // 查询算子 must/must_not/range/range_out <br>      "field": "doc_id", <br>      "conds": ["tos_doc_id_123", "tos_doc_id_456"] <br>  } <br>  query_param = { <br>      "doc_filter": doc_filter <br>  } <br> ``` <br>  <br> 多层 filter： <br> ```json <br> doc_filter = { <br>    "op": "and",   // 逻辑算子 and/or <br>    "conds": [     // 条件列表，支持嵌套逻辑算子和查询算子 <br>      { <br>        "op": "must", <br>        "field": "type", <br>        "conds": [1] <br>      }, <br>      { <br>          ...         // 支持 >= 1 个条件进行组合 <br>      } <br>    ] <br>  } <br>  <br>  query_param = { <br>      "doc_filter": doc_filter <br>  } <br> ``` <br>  |
| denseWeight | -- | Double | 否 | 0.5 | **混合检索中稠密向量的权重** <br>  <br> * 1 表示纯稠密检索，0 表示纯字面检索，范围 [0.2, 1] <br> * 只有在请求的知识库使用的是混合检索时有效，即索引算法为 hnsw_hybrid |
| preProcessing |  | Map<String, Object> |  |  | **检索预处理** |
|  | need_instruction | bool | 否 | False | **是否拼接 instruction 进行检索** |
|  | return_token_usage | bool | 否 | False | **是否返回 search 流程中各阶段的 token 使用量** |
|  | rewrite | bool | 否 | False | **是否对 query 进行改写** <br> 根据 messages 字段传入的历史对话信息进行改写，最多 3 轮 <br> **注：​**只有在 messages 字段长度大于 2 且不为空时，设置参数值为 True，才能返回有效的 rewrite_query； <br> ```json <br> "messages": [ <br>      {"role": "user", "content": "prompt 1"}, <br>      {"role": "assistant", "content": "prompt2"}, <br>      {"role": "user", "content": "prompt 3"}, <br>  ] <br> ``` <br>  |
|  | messages | json | 否 | -- | **多轮对话信息** <br> 仅**开启改写**时需要上传，可根据历史对话内容进行问题改写，注意上传对话轮数需 >= 1 <br> 发出消息的对话参与者角色，可选值包括： <br>  <br> * user：User Message 用户消息 <br> * assistant：Assistant Message 对话助手消息 <br>  <br> ```json <br> [ <br>      {"role": "user", "content": "知识库支持哪些文档格式？"}, <br>      {"role": "assistant", "content": "知识库支持结构化和非结构化文档，其中结构化文档支持 excel、csv、jsonl 等常见格式，非结构化文档支持 pdf、docx、ppt 等常见格式。"}, <br>      {"role": "user", "content": "那大小呢？"}, <br>  ] <br> ``` <br>  |
| postProcessing |  | Map<String, Object> |  |  | **检索后处理** |
|  | rerank_switch | bool | 否 | False | **自动对结果做 rerank** <br> 打开后，会自动请求 rerank 模型排序 |
|  | retrieve_count | int | 否 | 25 | **进入重排的切片数量，默认为 25** <br> 只有在 rerank_switch 为 True 时生效。retrieve_count 需要大于等于 limit，否则会抛出错误 |
|  | chunk_diffusion_count | int | 否 | 0 | **检索阶段返回命中切片的上下几片邻近切片** <br> 默认为 0，表示不进行 chunk diffusion。范围 [0, 5] |
|  | chunk_group | bool | 否 | False | **文本聚合** <br> 默认不聚合，对于非结构化文件，考虑到原始文档内容语序对大模型的理解，可开启文本聚合。开启后，会根据文档及其顺序，对切片进行重新聚合排序返回 |
|  | rerank_model | string | 否 | "base-multilingual-rerank" | **rerank 模型选择** <br> 仅在 "rerank_switch" == True 的时候生效 <br> 可选模型： <br>  <br> * "doubao-seed-rerank"（即 doubao-seed-1.6-rerank）：字节自研多模态重排模型、支持文本 / 图片 / 视频混合重排、精细语义匹配、可选阈值过滤与指令设置 <br> * "base-multilingual-rerank"：速度快、长文本、支持 70+ 种语言 <br> * "m3-v2-rerank"：常规文本、支持 100+ 种语言 |
|  | rerank_threshold | float | 否 | -- | **阈值过滤** <br> **仅当 rerank_model=="doubao-seed-rerank" 时生效**，用于设置重排分数的过滤阈值，低于阈值的结果将不会被返回，取值范围为 0 到 1 |
|  | rerank_instruction | string | 否 | -- | **rerank 指令** <br> **仅在 "rerank_switch" == True 且 "rerank_model" == "doubao-seed-rerank" 时生效**，用于提供给模型一个明确的排序指令，提升重排效果。字符串长度不超过 1024 <br> *如：Whether the document answers the query or matches the content retrieval intent* |
|  | rerank_only_chunk | bool | 否 | False | **是否仅根据 chunk 内容计算重排分数** <br> 可选值： <br>  <br> * True：只根据 chunk 内容计算分数 <br> * False：根据 chunk title + 内容一起计算排序分数 |
|  | get_attachment_link | bool | 否 | False | **是否获取切片中图片的临时下载链接** |
# **响应消息**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码 |
| message | String | 返回信息 |
| requestId | String | 标识每个请求的唯一标识符 |
| data | SearchKnowledgeResult | SearchKnowledgeResult |
### **SearchKnowledgeResult**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| count | Integer | 检索结果返回的条数 |
| rewriteQuery | String | query 改写的结果 |
| tokenUsage | Map<String, Object> | Token 使用信息 |
| resultList | List | 检索召回切片信息列表 |
### **PointInfo**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| collectionName | String | 知识库名称 |
| pointId | String | 切片 id（知识库下唯一） |
| processTime | Long | 切片处理完成的时间 |
| originText | String | 原始文本 |
| mdContent | String | 切片 markdown 解析结果，保留更多的原始表格信息（chunk_type 为 table 时会返回） |
| htmlContent | String | 切片 html 解析结果，保留更多的原始表格信息（chunk_type 为 table 时会返回） |
| chunkTitle | String | 切片标题，是由解析模型识别出来的上一层级的标题。若没有上一层级标题则为空 |
| chunkType | String | 切片所属类型 |
| description | String | 文档描述（当前仅支持图片文档） |
| content | String | 切片内容 <br> 1、非结构化文件：content 返回切片内容 <br> 2、faq 文件：content 返回答案 <br> 3、结构化文件：content 返回参与索引的字段和取值，以 K:V 对拼接，使用 \n 区隔 |
| chunkId | Long | 切片位次 id，代表在原始文档中的位次顺序 |
| originalQuestion | String | faq 数据检索召回答案对应的原始问题 |
| docInfo | PointDocInfo | PointDocInfo |
| rerankScore | Double | 重排得分 |
| score | Double | 检索得分 |
| chunkSource | String | 切片来源 |
| chunkAttachment | List | 临时下载链接，有效期 10 分钟 |
| tableChunkFields | List | 结构化数据检索返回单行全量数据 |
| updateTime | Long | 更新时间 |
| chunkStatus | String | 切片状态 |
| videoFrame | String | 视频帧 |
| videoUrl | String | 视频链接 |
| videoStartTime | Long | 视频切片的起始时间（ms） |
| videoEndTime | Long | 视频切片的结束时间（ms） |
| videoOutline | Map<String, Object> | 视频大纲 |
| audioStartTime | Long | 音频切片的起始时间（ms） |
| audioEndTime | Long | 音频切片的结束时间（ms） |
| audioOutline | Map<String, Object> | 音频大纲 |
| sheetName | String | sheet 名称 |
| project | String | 项目名 |
| resourceId | String | 知识库唯一 id |
### **PointDocInfo**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| docId | String | 所属文档 id |
| docName | String | 所属文档名字 |
| createTime | Long | 文档创建时间 |
| docType | String | 所属原始文档类型 |
| docMeta | String | 所属文档的 meta 信息 |
| source | String | 所属文档知识来源（url，tos 等） |
| title | String | 所属文档标题 |
| status | DocStatus | DocStatus |
### **DocStatus**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| processStatus | Integer | 处理状态 |
| failedCode | Integer | 失败错误码 |
| failedMsg | String | 失败错误信息 |
### **ChunkAttachment**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| uuid | String | 附件的唯一标识 |
| caption | String | 图片所属标题，若未识别到标题则值为 "\n" |
| type | String | image 等 |
| link | String | 临时下载链接，有效期 10 分钟 |
| infoLink | String | 附件 info_link |
| columnName | String | 附件列名 |
### **PointTableChunkField**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| fieldName | String | 字段名 |
| fieldValue | Object | 字段值 |
## **状态码说明**
| **状态码** | **http状态码** | **返回信息** | **状态码说明** |
| --- | --- | --- | --- |
| 0 | 200 | success | 成功 |
| 1000001 | 401 | unauthorized | 缺乏鉴权信息 |
| 1000002 | 403 | no permission | 权限不足 |
| 1000003 | 400 | invalid request：%s | 非法参数 |
| 1000005 | 400 | collection not exist | collection 不存在 |
# 请求示例
首次使用知识库 SDK，可参考 [使用说明](https://www.volcengine.com/docs/84313/2277191?lang=zh)
本示例演示了知识库 Java SDK 中 SearchKnowledge 的基础使用方法，通过指定知识库名称和查询语句实现知识库检索，使用前需配置 API Key 鉴权参数（VIKING_API_KEY）。
```java
package com.volcengine.vikingdb.runtime.knowledge.examples.collection_search_knowledge;

import com.fasterxml.jackson.databind.ObjectWriter;
import com.volcengine.vikingdb.runtime.core.ApiClient;
import com.volcengine.vikingdb.runtime.core.RequestAddition;
import com.volcengine.vikingdb.runtime.core.auth.Auth;
import com.volcengine.vikingdb.runtime.core.auth.AuthWithApiKey;
import com.volcengine.vikingdb.runtime.enums.Scheme;
import com.volcengine.vikingdb.runtime.knowledge.model.CollectionMeta;
import com.volcengine.vikingdb.runtime.knowledge.model.request.SearchKnowledgeRequest;
import com.volcengine.vikingdb.runtime.knowledge.model.response.SearchKnowledgeResponse;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeCollectionClient;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeService;

public class Main {
    private static final ObjectWriter PRETTY_JSON = ApiClient.objectMapper.writerWithDefaultPrettyPrinter();
    private static final Scheme SCHEME = Scheme.HTTPS;
    private static final String HOST = "api-knowledgebase.mlp.cn-beijing.volces.com";
    private static final String REGION = "cn-beijing";
    private static final String PROJECT = "default";
    private static final String COLLECTION_NAME = "your_collection_name";
    private static final String COLLECTION_RESOURCE_ID = "";

    public static void main(String[] args) throws Exception {
        String apiKey = getEnv("VIKING_API_KEY");
        if (apiKey.isEmpty()) {
            System.out.println("missing_auth: set VIKING_API_KEY");
            return;
        }
        Auth auth = new AuthWithApiKey(apiKey);
        KnowledgeService service = newKnowledgeService(auth);
        KnowledgeCollectionClient kc = service.collection(defaultCollectionMeta());

        String query = "Your Query";
        SearchKnowledgeRequest req = SearchKnowledgeRequest.builder()
                .query(query)
                .limit(10)
                .denseWeight(0.5)
                .build();
        SearchKnowledgeResponse resp = kc.searchKnowledge(req, new RequestAddition());
        printJson("search_knowledge", resp);
    }

    private static KnowledgeService newKnowledgeService(Auth auth) {
        return new KnowledgeService(SCHEME, HOST, REGION, auth);
    }

    private static CollectionMeta defaultCollectionMeta() {
        return CollectionMeta.builder()
                .collectionName(COLLECTION_NAME)
                .projectName(PROJECT)
                .resourceId(COLLECTION_RESOURCE_ID)
                .build();
    }

    private static String getEnv(String name) {
        String v = System.getenv(name);
        if (v == null) {
            return "";
        }
        v = v.trim();
        return v.isEmpty() ? "" : v;
    }

    private static void printJson(String name, Object obj) throws Exception {
        if (obj == null) {
            System.out.println(name + ": null");
            return;
        }
        System.out.println(name + ": " + PRETTY_JSON.writeValueAsString(obj));
    }
}
```


