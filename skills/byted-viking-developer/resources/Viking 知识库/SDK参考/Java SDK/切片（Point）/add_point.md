# 概述
add_point 用于新增一个知识库下文档的一个切片
# **请求参数**
| **参数** | **类型** | **必选** | **默认值** | **备注** |
| --- | --- | --- | --- | --- |
| collectionName | String | 否 | -- | **知识库名称** |
| projectName | String | 否 | default | **知识库所属项目，获取方式参见文档**[API 接入与技术支持](/c8p1dfoq/y97x844a) <br> 若不指定该字段，则在default项目下创建。 <br> 若需要操作指定项目下的知识库，需正确配置该字段。 |
| resourceId | String | 否 | -- | **知识库唯一 id** <br>  <br> * 可选择直接传 ResourceID，或同时传 CollectionName 和 ProjectName 作为知识库的唯一标识 |
| docId | String | 是 | -- | **表示新增切片所属的文档** <br>  <br> * 不存在时会报错。 |
| chunkType | String | 是 | -- | **要添加的切片类型** <br>  <br> * 和知识库支持的类型不匹配时会报错 <br> * 结构化知识库：“structured”， <br> * 非结构化知识库： <br> * “text”： 纯文本切片 <br> * “faq”： faq 类型切片 |
| content | String | 否 | -- | **新增切片文本内容** <br> 当 `chunkType` 为 text、faq 时必传 <br> 1、text：Content 对应切片原文内容 <br> 2、faq：Content 对应**答案字段**内容 |
| chunkTitle | String | 否 | -- | **切片标题** <br> 只有非结构化文档支持修改切片的标题。 |
| question | String | 否 | -- | **新增 faq 切片中的问题字段** <br> 当 `chunkType` 为 faq 时必传 <br>  <br> * 字段长度范围为 [1，{Embedding模型支持的最大长度}] |
| fields | List<Map<String, Object>> | 否 | -- | **表示传入的结构化数据** <br> 当 `chunkType` 为 structured 时必传。 <br> [ <br> { "field_name": "xxx" // 字段名称 <br> "field_value": xxxx // 字段值 <br> }, <br> ] <br>  <br> * field_name 必须已在所属知识库的表字段里配置，否则会报错 <br> * 和文档导入时的向量字段长度校验保持一致，拼接后的做 embedding 的文本长度不超过 65535 |
# **响应消息**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码 |
| message | String | 返回信息 |
| requestId | String | 标识每个请求的唯一标识符 |
| data | PointAddResult | PointAddResult |
### **PointAddResult**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| collectionName | String | 知识库的名字 |
| project | String | 项目名 |
| resourceId | String | 知识库唯一标识 |
| docId | String | 文档 id |
| chunkId | Long | 切片在文档下的 id，文档下唯一 |
| pointId | String | 切片 id，知识库下唯一 |
# 请求示例
首次使用知识库 SDK ，可参考 [使用说明](https://www.volcengine.com/docs/84313/2277191?lang=zh)
本示例演示了知识库 Java SDK 中 AddPoint 的基础使用方法，使用前需配置 API Key 鉴权参数（VIKING_API_KEY）。
```java
package com.volcengine.vikingdb.runtime.knowledge.examples.point_add;

import com.fasterxml.jackson.databind.ObjectWriter;
import com.volcengine.vikingdb.runtime.core.ApiClient;
import com.volcengine.vikingdb.runtime.core.RequestAddition;
import com.volcengine.vikingdb.runtime.core.auth.Auth;
import com.volcengine.vikingdb.runtime.core.auth.AuthWithApiKey;
import com.volcengine.vikingdb.runtime.enums.Scheme;
import com.volcengine.vikingdb.runtime.knowledge.model.CollectionMeta;
import com.volcengine.vikingdb.runtime.knowledge.model.request.AddDocV2Request;
import com.volcengine.vikingdb.runtime.knowledge.model.request.AddPointRequest;
import com.volcengine.vikingdb.runtime.knowledge.model.response.AddDocResponse;
import com.volcengine.vikingdb.runtime.knowledge.model.response.PointAddResponse;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeCollectionClient;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeService;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

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

        String docId = "java-example-doc-" + UUID.randomUUID();
        String uri = "https://pdf.dfcfw.com/pdf/H3_AP202504281663850212_1.pdf";
        AddDocV2Request addDocReq = AddDocV2Request.builder()
                .docId(docId)
                .docName("Java SDK Knowledge Point Add Example")
                .docType("pdf")
                .uri(uri)
                .build();
        AddDocResponse addDocResp = kc.addDocV2(addDocReq, new RequestAddition());
        printJson("add_doc_v2", addDocResp);

        Map<String, Object> field1 = new HashMap<>();
        field1.put("field_name", "topic");
        field1.put("field_type", "string");
        field1.put("field_value", "your_topic");

        Map<String, Object> field2 = new HashMap<>();
        field2.put("field_name", "year");
        field2.put("field_type", "int64");
        field2.put("field_value", 2025);

        AddPointRequest req = AddPointRequest.builder()
                .docId(docId)
                .chunkType("text")
                .chunkTitle("your_chunk_title")
                .content("your_chunk_content")
                .fields(Arrays.asList(field1, field2))
                .build();

        PointAddResponse resp = kc.addPoint(req, new RequestAddition());
        printJson("add_point", resp);
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


