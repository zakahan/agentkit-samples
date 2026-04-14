# 概述
list_docs 用于查询知识库上文档的列表，默认按照文档的上传时间倒序。
# **请求参数**
| **参数** | 子参数 | **类型** | **是否必选** | **默认值** | **参数说明** |
| --- | --- | --- | --- | --- | --- |
| collectionName | -- | String | 否 | -- | **知识库名称** |
| projectName | -- | String | 否 | default | **知识库所属项目，获取方式参见文档**[API 接入与技术支持](/c8p1dfoq/y97x844a) <br> 若不指定该字段，则默认在 default 项目下进行查询。 <br> 若需要操作指定项目下的知识库，需正确配置该字段。 |
| resourceId | -- | String | 否 | -- | **知识库唯一 id** <br> 可选择直接传 resourceId，或同时传 collectionName 和 projectName 作为知识库的唯一标识 |
| filter |  | Map<String, Object> | 否 | -- | **过滤条件** <br> 用于对返回结果进行过滤，支持使用 docId 过滤 |
|  | docIdList | String[] | 否 | -- | **指定 docId 过滤条件** <br> 只返回列表中指定的文档信息 |
| offset | -- | Integer | 否 | 0 | **查询起始位置** <br> 表示从结果的第几个文档后开始取，需要大于等于0 <br> 注：如果设置 offset ≥ 100，需同时传入 limit 参数才能生效 |
| limit | -- | Integer | 否 | -1 | **查询文档数** <br> -1 表示获取所有，最大值不超过 100，每次返回最多不超过 100 |
| docType | -- | String | 否 | -- | **文档类型筛选** |
| returnTokenUsage | -- | Boolean | 否 | false | **是否返回文档向量化和文档摘要生成所消耗的 tokens** |
# **响应消息**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码 |
| message | String | 返回信息 |
| requestId | String | 标识每个请求的唯一标识符 |
| data | ListDocsResult | ListDocsResult |
### **ListDocsResult**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| docList | List | 文档信息列表 |
| count | Integer | 本次查询返回的文档总数 |
| totalNum | Integer | 该知识库下的文档总数 |
### **DocInfo**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| collectionName | String | 知识库名称 |
| docName | String | 文档名称 |
| docId | String | 文档 id |
| docHash | String | 文档 hash |
| addType | String | 导入方式 |
| docType | String | 文档类型 |
| description | String | 文档描述（当前仅支持图片文档） |
| createTime | Long | 文档创建时间 |
| addedBy | String | 添加人 |
| updateTime | Long | 文档更新时间 |
| url | String | 原始文档链接 |
| tosPath | String | tos 路径 |
| pointNum | Integer | 切片数量 |
| status | DocStatus | DocStatus |
| title | String | 文档标题 |
| source | String | 知识来源（url，tos 等） |
| totalTokens | Object | tokens 统计 |
| docSummaryTokens | Integer | 摘要 tokens 统计 |
| docPremiumStatus | DocPremiumStatus | DocPremiumStatus |
| docSummary | String | 文档摘要 |
| briefSummary | String | 简要摘要 |
| docSize | Integer | 文档大小 |
| meta | String | meta 信息 |
| labels | Map<String, String> | 标签信息 |
| videoOutline | Map<String, Object> | 视频大纲 |
| audioOutline | Map<String, Object> | 音频大纲 |
| statistics | Map<String, Object> | 统计信息 |
| project | String | 项目名 |
| resourceId | String | 知识库唯一 id |
### **DocStatus**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| processStatus | Integer | 处理状态 |
| failedCode | Integer | 失败错误码 |
| failedMsg | String | 失败错误信息 |
### **DocPremiumStatus**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| docSummaryStatusCode | Integer |  |
## **状态码说明**
| **状态码** | **HTTP 状态码** | **返回信息** | **状态码说明** |
| --- | --- | --- | --- |
| 0 | 200 | success | 成功 |
| 1000001 | 401 | unauthorized | 鉴权失败 |
| 1000002 | 403 | no permission | 权限不足 |
| 1000003 | 400 | invalid request: %s | 非法参数 |
| 1000005 | 400 | collection not exist | collection 不存在 |
# 请求示例
首次使用知识库 SDK，可参考 [使用说明](https://www.volcengine.com/docs/84313/2277191?lang=zh)
本示例演示了知识库 Java SDK 中 ListDocs 的基础使用方法，通过指定知识库信息实现文档列表查询，使用前需配置 API Key 鉴权参数（VIKING_API_KEY）。
```java
package com.volcengine.vikingdb.runtime.knowledge.examples.doc_list;

import com.fasterxml.jackson.databind.ObjectWriter;
import com.volcengine.vikingdb.runtime.core.ApiClient;
import com.volcengine.vikingdb.runtime.core.RequestAddition;
import com.volcengine.vikingdb.runtime.core.auth.Auth;
import com.volcengine.vikingdb.runtime.core.auth.AuthWithApiKey;
import com.volcengine.vikingdb.runtime.enums.Scheme;
import com.volcengine.vikingdb.runtime.knowledge.model.CollectionMeta;
import com.volcengine.vikingdb.runtime.knowledge.model.request.ListDocsRequest;
import com.volcengine.vikingdb.runtime.knowledge.model.response.ListDocsResponse;
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

        ListDocsRequest req = ListDocsRequest.builder()
                .offset(0)
                .limit(10)
                .returnTokenUsage(true)
                .build();

        ListDocsResponse resp = kc.listDocs(req, new RequestAddition());
        printJson("list_docs", resp);
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


