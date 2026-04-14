# 概述
update_point 用于更新知识库下的切片内容
# **请求参数**
| 参数 | 类型 | 必选 | 默认值 | 备注 |
| --- | --- | --- | --- | --- |
| collectionName | String | 否 | -- | **知识库名称** |
| projectName | String | 否 | default | **知识库所属项目，获取方式参见文档**[API 接入与技术支持](/c8p1dfoq/y97x844a) <br> 若不指定该字段，则在default项目下创建。 <br> 若需要操作指定项目下的知识库，需正确配置该字段。 |
| resourceId | String | 否 | -- | **知识库唯一 id** <br> 可选择直接传 ResourceID，或同时传 CollectionName 和 ProjectName 作为知识库的唯一标识 |
| pointId | String | 是 | -- | **要更新的切片 id** |
| chunkTitle | String | 否 | -- | **切片标题** <br> 只有非结构化文档支持修改切片的标题。 |
| content | String | 二者只传一个 | -- | **要更新的非结构化文档的切片内容** <br>  <br> * 1、非结构化文件：Content 对应切片原文内容 <br> * 2、faq 文件：Content 对应答案字段内容 <br> * 3、结构化文件：Content 对应参与索引的字段和取值，以 K:V 对拼接，使用 \n 区隔 |
| fields | List<Map<String, Object>> | 否 | -- | **要更新的结构化文档的切片内容** <br> 一行数据全量更新 <br> [ <br> { "field_name": "xxx" // 字段名称 <br> "field_value": xxxx // 字段值 <br> }, <br> ] <br> field_name 必须已在所属知识库的表字段里配置，否则会报错 |
| question | String | 否 | -- | **要更新的非结构化 faq 文档切片的问题字段** |
# **响应消息**
| 字段 | 类型 | 备注 |
| --- | --- | --- |
| code | Integer | 状态码 |
| message | String | 返回信息 |
| requestId | String | 标识每个请求的唯一标识符 |
## **状态码说明**
| code | message | 备注 | http status_code |
| --- | --- | --- | --- |
| 0 | success | 成功 | 200 |
| 1000001 | unauthorized | 缺乏鉴权信息 | 401 |
| 1000002 | no permission | 权限不足 | 403 |
| 1000003 | invalid request：%s | 非法参数 | 400 |
| 1000005 | collection not exist | collection不存在 | 400 |
# 请求示例
首次使用知识库 SDK ，可参考 [使用说明](https://www.volcengine.com/docs/84313/2277191?lang=zh)
本示例演示了知识库 Java SDK 中 UpdatePoint 的基础使用方法，通过指定切片 ID 修改切片内容，使用前需配置 API Key 鉴权参数（VIKING_API_KEY）。
```java
package com.volcengine.vikingdb.runtime.knowledge.examples.point_update;

import com.fasterxml.jackson.databind.ObjectWriter;
import com.volcengine.vikingdb.runtime.core.ApiClient;
import com.volcengine.vikingdb.runtime.core.RequestAddition;
import com.volcengine.vikingdb.runtime.core.auth.Auth;
import com.volcengine.vikingdb.runtime.core.auth.AuthWithApiKey;
import com.volcengine.vikingdb.runtime.enums.Scheme;
import com.volcengine.vikingdb.runtime.knowledge.model.CollectionMeta;
import com.volcengine.vikingdb.runtime.knowledge.model.request.AddDocV2Request;
import com.volcengine.vikingdb.runtime.knowledge.model.request.AddPointRequest;
import com.volcengine.vikingdb.runtime.knowledge.model.request.UpdatePointRequest;
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
                .docName("Java SDK Knowledge Point Update Example")
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

        UpdatePointRequest update = UpdatePointRequest.builder()
                .chunkTitle("your_chunk_title_updated")
                .content("your_chunk_content_updated")
                .build();
        BaseResponse resp = kc.updatePoint(pointId, update, new RequestAddition());
        printJson("update_point", resp);
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


