# 概述
service_chat 支持基于一个已创建的知识服务进行检索/问答。
# 请求参数
| **参数** | **类型** | **是否必选** | **默认值** | **参数说明** |
| --- | --- | --- | --- | --- |
| serviceResourceId | String | 是 | -- | **知识服务唯一 id** |
| messages | List | 是 | -- | **检索/问答多轮对话消息** <br> 格式为一问一答形式，发出消息的对话参与者角色可选值包括： <br>  <br> * user：User Message 用户消息 <br> * assistant：Assistant Message 对话助手消息 <br>  <br> 其中 **最后一个元素 role == user，content 为当前最新的提问 query** <br> **纯文本对话：** <br> 例如： <br> ```json <br> [ <br>      { <br>          "role": "system", <br>          "content": "你是一位在线客服，你的首要任务是通过巧妙的话术回复用户的问题，你需要根据「参考资料」来回答接下来的「用户问题」，这些信息在 <context></context> XML tags 之内，你需要根据参考资料给出准确，简洁的回答。参考资料中可能会包含图片信息，图片的引用说明在<img></img>XML tags 之内，参考资料内的图片顺序与用户上传的图片顺序一致。" <br>      }, <br>      {"role": "user", "content": "你好"}, <br>      {"role": "assistant", "content": "你好！有什么我可以帮助你的？"}, <br>      {"role": "user", "content": "当前轮次用户问题"} <br>  ] <br> ``` <br>  <br> **图文对话**： <br> 例如： <br> ```json <br> [ <br>      { <br>          "role": "system", <br>          "content": "你是一位在线客服，你的首要任务是通过巧妙的话术回复用户的问题，你需要根据「参考资料」来回答接下来的「用户问题」，这些信息在 <context></context> XML tags 之内，你需要根据参考资料给出准确，简洁的回答。参考资料中可能会包含图片信息，图片的引用说明在<img></img>XML tags 之内，参考资料内的图片顺序与用户上传的图片顺序一致。" <br>      }, <br>      { <br>          "role": "user", <br>          "content": [ <br>              { <br>                  "type": "text", <br>                  "text": "推荐一个类似的适合 3 岁小孩的玩具" <br>              }, <br>              { <br>                  "type": "image_url", <br>                  "image_url": { <br>                      "url": "https://ark-project.tos-cn-beijing.volces.XXX.jpeg" #客户上传的图片，支持 URL/base64 编码，协议详见：https://www.volcengine.com/docs/82379/1362931?lang=zh#477e51ce 和 https://www.volcengine.com/docs/82379/1362931?lang=zh#d86010f4 <br>                  } <br>              } <br>          ] <br>      } <br>  ] <br> ``` <br>  |
| queryParam | Map<String, Object> | 否 | null | **检索过滤条件** <br> 在创建知识服务时如果您已配置了过滤条件，那么和该附加过滤条件一起生效，逻辑为 and <br>  <br> * 支持对 doc 的 meta 信息过滤 <br> * 详细使用方式和支持字段见[filter表达式](https://www.volcengine.com/docs/84313/1419289#filter-%E8%A1%A8%E8%BE%BE%E5%BC%8F)，可支持对 doc_id 做筛选 <br> * 此处用于过滤的字段，需要在 collection/create 时添加到 index_config 的 fields 上 <br>  <br> 例如： <br> 单层 filter： <br> ```json <br> doc_filter = { <br>     "op": "must", // 查询算子 must/must_not/range/range_out <br>     "field": "doc_id", <br>     "conds": ["tos_doc_id_123", "tos_doc_id_456"] <br>  } <br>  query_param = { <br>      "doc_filter": doc_filter <br>  } <br> ``` <br>  <br> 多层 filter： <br> ```json <br> doc_filter = { <br>    "op": "and",   // 逻辑算子 and/or <br>    "conds": [     // 条件列表，支持嵌套逻辑算子和查询算子 <br>      { <br>        "op": "must", <br>        "field": "type", <br>        "conds": [1] <br>      }, <br>      { <br>          ...         // 支持>=1的任意数量的条件进行组合 <br>      } <br>    ] <br>  } <br>  <br>  query_param = { <br>      "doc_filter": doc_filter <br>  } <br> ``` <br>  |
| stream | Boolean | 否 | true | **是否采用流式返回** <br> 当创建的知识服务为问答类型服务时生效 |
# **响应消息**
目前知识服务主要分为两类，检索类型和问答类型。针对不同类型的知识服务，返回的消息格式也有所不同
检索/问答/流式的差异体现在 Data 内字段是否出现及返回时机：
Count、RewriteQuery、ResultList 通常在首流返回；TokenUsage 通常在尾流返回；GeneratedAnswer、ReasoningContent 在中间流分段返回（SSE）。
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码 |
| message | String | 返回信息 |
| requestId | String | 标识每个请求的唯一标识符 |
| data | ServiceChatData | ServiceChatData |
### **ServiceChatData**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| count | Integer | 检索结果返回的条数 |
| rewriteQuery | String | query 改写的结果 |
| tokenUsage | Object | Token 使用信息 |
| resultList | List | 检索返回的信息 |
| generatedAnswer | String | LLM 模型生成的回答 |
| reasoningContent | String | 推理模型生成的内容 |
| prompt | String | prompt 内容 |
| end | Boolean | 是否结束（流式场景用于标识最后一段） |
### **ServiceChatRetrieveItem**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| id | String | 索引的主键 |
| content | String | 切片内容 <br> 1、非结构化文件：Content 返回切片内容 <br> 2、faq 文件：Content 返回答案 <br> 3、结构化文件：Content 返回参与索引的字段和取值，以 K:V 对拼接，使用 \n 区隔 |
| mdContent | String | markdown 格式的解析结果（表格切片可通过 ChunkType == table 判断） |
| score | Double | 向量化语义检索得分 |
| pointId | String | 切片 id |
| originText | String | 原始文本 |
| originalQuestion | String | faq 数据检索召回的答案对应的原始问题 |
| chunkTitle | String | 切片标题 |
| chunkId | Long | 切片位次 id（代表在原始文档中的位次顺序） |
| processTime | Long | 检索耗时（秒） |
| rerankScore | Double | 重排得分 |
| docInfo | ServiceChatRetrieveItemDocInfo | ServiceChatRetrieveItemDocInfo |
| recallPosition | Integer | 向量化语义检索召回位次 |
| rerankPosition | Integer | 重排位次 |
| chunkType | String | 切片所属类型（如 doc-image、image、video、table、mixed-table、text、structured、faq 等） |
| chunkSource | String | 切片来源 |
| updateTime | Long | 更新时间 |
| chunkAttachment | List | 检索召回附件的临时下载链接，有效期 10 分钟 |
| tableChunkFields | List | 结构化数据检索返回单行全量数据 |
| originalCoordinate | Map<String, Object> | 切片在所属文档的原始位置坐标 |
### **ServiceChatRetrieveItemDocInfo**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| docId | String | 文档 id |
| docName | String | 文档名字 |
| createTime | Long | 文档的创建时间 |
| docType | String | 知识所属原始文档的类型 |
| docMeta | String | 文档相关元信息 |
| source | String | 知识来源类型 |
| title | String | 知识所属文档的标题 |
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
# 请求示例
首次使用知识库 SDK，可参考 [使用说明](https://www.volcengine.com/docs/84313/2277191?lang=zh)
本示例演示了知识库 Java SDK 中 ServiceChat 的基础使用方法，包含普通调用和流式调用两种方式；该功能使用 API Key 鉴权（VIKING_API_KEY），且需配置知识服务 ID。
```java
package com.volcengine.vikingdb.runtime.knowledge.examples.service_chat;

import com.fasterxml.jackson.databind.ObjectWriter;
import com.volcengine.vikingdb.runtime.core.ApiClient;
import com.volcengine.vikingdb.runtime.core.RequestAddition;
import com.volcengine.vikingdb.runtime.core.auth.Auth;
import com.volcengine.vikingdb.runtime.core.auth.AuthWithApiKey;
import com.volcengine.vikingdb.runtime.enums.Scheme;
import com.volcengine.vikingdb.runtime.knowledge.model.request.ChatMessage;
import com.volcengine.vikingdb.runtime.knowledge.model.request.ServiceChatRequest;
import com.volcengine.vikingdb.runtime.knowledge.model.response.ServiceChatResponse;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeService;

import java.util.Collections;

public class Main {
    private static final ObjectWriter PRETTY_JSON = ApiClient.objectMapper.writerWithDefaultPrettyPrinter();
    private static final Scheme SCHEME = Scheme.HTTPS;
    private static final String HOST = "api-knowledgebase.mlp.cn-beijing.volces.com";
    private static final String REGION = "cn-beijing";
    private static final String SERVICE_RESOURCE_ID = "your_service_resource_id";

    public static void main(String[] args) throws Exception {
        String apiKey = getEnv("VIKING_API_KEY");
        if (apiKey.isEmpty()) {
            System.out.println("missing_auth: set VIKING_API_KEY");
            return;
        }
        Auth auth = new AuthWithApiKey(apiKey);

        KnowledgeService service = newKnowledgeService(auth);
        ServiceChatRequest req = ServiceChatRequest.builder()
                .serviceResourceId(SERVICE_RESOURCE_ID)
                .messages(Collections.singletonList(ChatMessage.builder()
                        .role("user")
                        .content("Your Query")
                        .build()))
                .stream(false)
                .build();

        ServiceChatResponse resp = service.serviceChat(req, new RequestAddition());
        printJson("service_chat", resp);
    }

    private static KnowledgeService newKnowledgeService(Auth auth) {
        return new KnowledgeService(SCHEME, HOST, REGION, auth);
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

```java
package com.volcengine.vikingdb.runtime.knowledge.examples.service_chat_stream;

import com.volcengine.vikingdb.runtime.core.RequestAddition;
import com.volcengine.vikingdb.runtime.core.auth.Auth;
import com.volcengine.vikingdb.runtime.core.auth.AuthWithApiKey;
import com.volcengine.vikingdb.runtime.enums.Scheme;
import com.volcengine.vikingdb.runtime.knowledge.model.request.ChatMessage;
import com.volcengine.vikingdb.runtime.knowledge.model.request.ServiceChatRequest;
import com.volcengine.vikingdb.runtime.knowledge.model.response.ServiceChatResponse;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeService;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeStream;

import java.util.Collections;

public class Main {
    private static final Scheme SCHEME = Scheme.HTTPS;
    private static final String HOST = "api-knowledgebase.mlp.cn-beijing.volces.com";
    private static final String REGION = "cn-beijing";
    private static final String SERVICE_RESOURCE_ID = "your_service_resource_id";

    public static void main(String[] args) throws Exception {
        String apiKey = getEnv("VIKING_API_KEY");
        if (apiKey.isEmpty()) {
            System.out.println("missing_auth: set VIKING_API_KEY");
            return;
        }
        Auth auth = new AuthWithApiKey(apiKey);

        KnowledgeService service = newKnowledgeService(auth);
        ServiceChatRequest req = ServiceChatRequest.builder()
                .serviceResourceId(SERVICE_RESOURCE_ID)
                .messages(Collections.singletonList(ChatMessage.builder()
                        .role("user")
                        .content("Your Query")
                        .build()))
                .stream(true)
                .build();

        try (KnowledgeStream<ServiceChatResponse> stream = service.serviceChatStream(req,
                new RequestAddition())) {
            System.out.println("service_chat_stream:");
            for (ServiceChatResponse item : stream) {
                if (item != null && item.getData() != null && item.getData().getGeneratedAnswer() != null) {
                    System.out.print(item.getData().getGeneratedAnswer());
                }
                if (item != null && item.getData() != null && Boolean.TRUE.equals(item.getData().getEnd())) {
                    break;
                }
            }
            System.out.print("\n");
        }
    }

    private static KnowledgeService newKnowledgeService(Auth auth) {
        return new KnowledgeService(SCHEME, HOST, REGION, auth);
    }

    private static String getEnv(String name) {
        String v = System.getenv(name);
        if (v == null) {
            return "";
        }
        v = v.trim();
        return v.isEmpty() ? "" : v;
    }
}
```


