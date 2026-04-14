# 概述
delete_point 用于删除一个知识库下的某个切片。
# **请求参数**
| **参数** | **类型** | **必选** | **默认值** | **备注** |
| --- | --- | --- | --- | --- |
| collectionName | String | 否 | -- | **知识库名称** <br>  <br> * 只能使用英文字母、数字、下划线_，并以英文字母开头，不能为空 <br> * 长度要求：[1, 64] |
| projectName | String | 否 | default | **知识库所属项目，获取方式参见文档**[API 接入与技术支持](/c8p1dfoq/y97x844a) <br> 若不指定该字段，则在 default 项目下进行操作。 <br> 若需要操作指定项目下的知识库，需正确配置该字段。 |
| resourceId | String | 否 | -- | **知识库唯一 id** <br>  <br> * 可选择直接传 resourceId，或同时传 collectionName 和 projectName 作为知识库的唯一标识 |
| pointId | String | 是 | -- | **要删除的切片 id** |
# **响应消息**
| 字段 | 类型 | 备注 |
| --- | --- | --- |
| code | Integer | 状态码 |
| message | String | 返回信息 |
| requestId | String | 标识每个请求的唯一标识符 |
# 请求示例
首次使用知识库 SDK，可参考 [使用说明](https://www.volcengine.com/docs/84313/2277191?lang=zh)
本示例演示了知识库 Java SDK 中 DeletePoint 的基础使用方法，通过指定切片 ID 实现切片删除，使用前需配置 API Key 鉴权参数（VIKING_API_KEY）。
```java
package com.volcengine.vikingdb.runtime.knowledge.examples.point_delete;

import com.fasterxml.jackson.databind.ObjectWriter;
import com.volcengine.vikingdb.runtime.core.ApiClient;
import com.volcengine.vikingdb.runtime.core.RequestAddition;
import com.volcengine.vikingdb.runtime.core.auth.Auth;
import com.volcengine.vikingdb.runtime.core.auth.AuthWithApiKey;
import com.volcengine.vikingdb.runtime.enums.Scheme;
import com.volcengine.vikingdb.runtime.knowledge.model.CollectionMeta;
import com.volcengine.vikingdb.runtime.knowledge.model.request.AddDocV2Request;
import com.volcengine.vikingdb.runtime.knowledge.model.request.AddPointRequest;
import com.volcengine.vikingdb.runtime.knowledge.model.request.DeletePointRequest;
import com.volcengine.vikingdb.runtime.knowledge.model.response.AddDocResponse;
import com.volcengine.vikingdb.runtime.knowledge.model.response.BaseResponse;
import com.volcengine.vikingdb.runtime.knowledge.model.response.PointAddResponse;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeCollectionClient;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeService;

import java.util.Collections;
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
                .docName("Java SDK Knowledge Point Delete Example")
                .docType("pdf")
                .uri(uri)
                .build();
        AddDocResponse addDocResp = kc.addDocV2(addDocReq, new RequestAddition());
        printJson("add_doc_v2", addDocResp);

        Map<String, Object> field = new HashMap<>();
        field.put("field_name", "topic");
        field.put("field_type", "string");
        field.put("field_value", "your_topic");

        AddPointRequest addPointReq = AddPointRequest.builder()
                .docId(docId)
                .chunkType("text")
                .chunkTitle("your_chunk_title")
                .content("your_chunk_content")
                .fields(Collections.singletonList(field))
                .build();
        PointAddResponse addPointResp = kc.addPoint(addPointReq, new RequestAddition());
        printJson("add_point", addPointResp);

        String pointId = addPointResp != null && addPointResp.getData() != null ? addPointResp.getData().getPointId()
                : null;
        if (pointId == null || pointId.trim().isEmpty()) {
            System.out.println("point_id_empty");
            return;
        }

        BaseResponse resp = kc.deletePoint(DeletePointRequest.builder().pointId(pointId).build(),
                new RequestAddition());
        printJson("delete_point", resp);
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


