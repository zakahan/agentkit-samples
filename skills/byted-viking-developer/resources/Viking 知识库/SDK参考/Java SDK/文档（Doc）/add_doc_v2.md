# 概述
add_doc_v2 用于向已创建的知识库添加文档。
# **请求参数**
| **参数** | **类型** | **是否必传** | **默认值** | **参数说明** |
| --- | --- | --- | --- | --- |
| collectionName | String | 否 | -- | 知识库名称 |
| projectName | String | 否 | default | 知识库所属项目，获取方式参考文档 [API 接入与技术支持](https://www.volcengine.com/docs/84313/1606319?lang=zh#1ab381b9) <br> 若需要操作指定项目下的知识库，需正确配置该字段 |
| resourceId | String | 否 | -- | **知识库唯一 id** <br> 可选择直接传 ResourceID，或同时传 CollectionName 和 ProjectName 作为知识库的唯一标识 |
| docId | String | 是 | -- | **知识库下的文档唯一标识** <br>  <br> * 只能使用英文字母、数字、下划线_，并以英文字母或下划线开头，不能为空 <br> * 长度要求：[1, 128] |
| docName | String | 否 | -- | **文档名称** <br>  <br> * 对于 TOS 导入的方式，未传入时直接使用 TOS Path 下的文档名 <br> * 对于 URL 导入的方式，先通过 URL 提取带后缀的文档名，如果没有则返回错误码 400，要求用户再传 DocName <br>  <br> 格式要求： <br>  <br> * 不能包含有特殊用途的字符：`<` `>` `:` `"` `/` `\` `\|` <br> * 长度要求：[1, 255] |
| docType | String | 否 | -- | **上传文档的类型** <br>  <br> * 非结构化文档支持类型：txt, doc, docx, pdf, markdown, pptx, ppt, jpeg, png, webp, bmp, mp4, mp3, wav, aac, flac, ogg <br> * .jpg 和 .jpeg 文件 DocType 均为 jpeg <br> * .markdown 和 .md 文件 DocType 均为 markdown <br> * 结构化文档支持类型：xlsx, csv, jsonl <br>  <br> 优先使用传入的值；若未传入，将尝试自动提取；若自动提取失败，则接口返回错误 |
| description | String | 否 | -- | **文档描述** <br> 描述会参与对图片的检索，如电商场景下，描述可以用于存放图片对应的详细商品说明，售卖亮点，价格等 <br> 注： <br>  <br> * 暂**只在** DocType 为**图片类型文档时支持**，其他类型文档设置无效。 <br> * 长度 [0, 4000] |
| tagList | List | 否 | -- | Tag 为结构体，包含 <br>  <br> * FieldName：标签名，类型为 string <br> * 不能为 "doc_id" <br> * 需对齐创建知识库时的 FieldName <br> * 在创建知识库时先初始化标签索引，再在上传文档时打标，以用于检索时实现标签过滤能力 <br> * 若需新增过滤标签，请先编辑知识库新增标签后，再进行文档打标 <br> * FieldType：标签类型 <br> * 支持 "int64"，"float32"，"string"，"bool"，"list"，"date_time"，"geo_point" 类型 <br> * 需对齐创建知识库时的 FieldType <br> * FieldValue：标签值 <br> * 与 FieldType 指定类型一致 |
| uri | String | 是 | -- | 待上传的文件 uri 链接，示例： <br>  <br> * http://a/b/c.pdf <br> * tos://a/b/c.pdf |
# **响应消息**
| **参数** | **类型** | **参数说明** | **备注** |
| --- | --- | --- | --- |
| code | Integer | 状态码 |  |
| message | String | 返回信息 |  |
| requestId | String | 标识每个请求的唯一标识符 |  |
| data | AddDocResponseData | AddDocResponseData |  |
### **AddDocResponseData**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| collectionName | String | 知识库的名字 |
| resourceId | String | 知识库唯一标识 |
| project | String | 项目名 |
| docId | String | 文档唯一标识 |
| taskId | Long | 任务 id |
| dedupInfo | DedupInfo | DedupInfo |
| moreInfo | String | 更多信息 |
### **DedupInfo**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| skip | Boolean | 是否跳过（去重命中） |
| sameDocIds | List | 重复的文档 id 列表 |
## **状态码说明**
| **状态码** | **http状态码** | **返回信息** | **状态码说明** |
| --- | --- | --- | --- |
| 0 | 200 | success | 成功 |
| 1000001 | 401 | unauthorized | 鉴权失败 |
| 1000002 | 403 | no permission | 权限不足 |
| 1000003 | 400 | invalid request: %s | 非法参数 |
| 1000005 | 400 | collection not exist | collection 不存在 |
| 1001002 | 400 | invalid request: doc_id:xxx is duplicated with doc_ids:xxx | 文档内容与现有文档重复 |
| 1001010 | 400 | doc num is exceed 3000000 | doc 数量已达限额，点击详情查看[知识库配额限制](https://www.volcengine.com/docs/84313/1339026) |
# 请求示例
首次使用知识库 SDK ，可参考 [使用说明](https://www.volcengine.com/docs/84313/2277191?lang=zh)
本示例演示了知识库 Java SDK 中 AddDocV2 的基础使用方法，使用前需配置 API Key 鉴权参数（VIKING_API_KEY）。
```java
package com.volcengine.vikingdb.runtime.knowledge.examples.doc_add_v2;

import com.fasterxml.jackson.databind.ObjectWriter;
import com.volcengine.vikingdb.runtime.core.ApiClient;
import com.volcengine.vikingdb.runtime.core.RequestAddition;
import com.volcengine.vikingdb.runtime.core.auth.Auth;
import com.volcengine.vikingdb.runtime.core.auth.AuthWithApiKey;
import com.volcengine.vikingdb.runtime.enums.Scheme;
import com.volcengine.vikingdb.runtime.knowledge.model.CollectionMeta;
import com.volcengine.vikingdb.runtime.knowledge.model.request.AddDocV2Request;
import com.volcengine.vikingdb.runtime.knowledge.model.response.AddDocResponse;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeCollectionClient;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeService;

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

        AddDocV2Request req = AddDocV2Request.builder()
                .docId(docId)
                .docName("Java SDK Knowledge Doc AddV2 Example")
                .docType("pdf")
                .uri(uri)
                .build();

        AddDocResponse resp = kc.addDocV2(req, new RequestAddition());
        printJson("add_doc_v2", resp);
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


