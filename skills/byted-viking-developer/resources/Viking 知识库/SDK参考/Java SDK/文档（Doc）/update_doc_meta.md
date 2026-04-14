# 概述
update_doc_meta 用于更新知识库中文档信息，文档 meta 信息更新会自动触发索引数据更新。
# **请求参数**
| **参数** | **子参数** | **类型** | **是否必选** | **默认值** | **参数说明** |
| --- | --- | --- | --- | --- | --- |
| collectionName | -- | String | 否 | -- | **知识库名称** |
| projectName | -- | String | 否 | default | **知识库所属项目，获取方式参见文档**[API 接入与技术支持](/c8p1dfoq/y97x844a) <br> 若需要操作指定项目下的知识库，需正确配置该字段。 |
| resourceId | -- | String | 否 | -- | **知识库唯一 id** <br> 可选择直接传 resourceId，或同时传 collectionName 和 projectName 作为知识库的唯一标识 |
| docId | -- | String | 是 | -- | **待更新文档的 id** |
| meta |  | List | 否 | -- | **meta 信息** |
|  | fieldName | String | 否 | -- | **要更新的字段名** |
|  | fieldType | String | 否 | -- | **要更新的字段类型** <br>  <br> * 仅当新增知识库未配置过的标签字段时生效，且新增字段不能用于标量过滤，仅可作为当前文档的描述信息存储 <br> * 支持 "int64"，"float32"，"string"，"bool"，"list" 类型，限制参考[VikingDB的field_type规则和说明](https://www.volcengine.com/docs/84313/1254542#field-type-%E5%8F%AF%E9%80%89%E5%80%BC) |
|  | fieldValue | Object | 否 | -- | **要更新的字段值** <br> 字段值需保证类型符合字段定义，如 "int64"，"float32"，"string" 等。 |
# **响应消息**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码 |
| message | String | 返回信息 |
| requestId | String | 每个请求的唯一标识符 |
## **状态码说明**
| **状态码** | **http状态码** | **返回信息** | **状态码说明** |
| --- | --- | --- | --- |
| 0 | 200 | success | 成功 |
| 1000001 | 401 | unauthorized | 鉴权失败 |
| 1000002 | 403 | no permission | 权限不足 |
| 1000003 | 400 | invalid request: %s | 非法参数 |
| 1000005 | 400 | collection not exist | collection 不存在 |
| 1001001 | 400 | doc not exist | doc 不存在 |
# 请求示例
首次使用知识库 SDK，可参考 [使用说明](https://www.volcengine.com/docs/84313/2277191?lang=zh)
本示例演示了知识库 Java SDK 中 UpdateDocMeta 的基础使用方法，通过指定文档 ID 和元数据信息（字段名、类型、值）修改文档元数据，使用前需配置 API Key 鉴权参数（VIKING_API_KEY）。
```java
package com.volcengine.vikingdb.runtime.knowledge.examples.doc_update_meta;

import com.fasterxml.jackson.databind.ObjectWriter;
import com.volcengine.vikingdb.runtime.core.ApiClient;
import com.volcengine.vikingdb.runtime.core.RequestAddition;
import com.volcengine.vikingdb.runtime.core.auth.Auth;
import com.volcengine.vikingdb.runtime.core.auth.AuthWithApiKey;
import com.volcengine.vikingdb.runtime.enums.Scheme;
import com.volcengine.vikingdb.runtime.knowledge.model.CollectionMeta;
import com.volcengine.vikingdb.runtime.knowledge.model.request.MetaItem;
import com.volcengine.vikingdb.runtime.knowledge.model.response.BaseResponse;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeCollectionClient;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeService;

import java.util.ArrayList;
import java.util.List;

public class Main {
    private static final ObjectWriter PRETTY_JSON = ApiClient.objectMapper.writerWithDefaultPrettyPrinter();
    private static final Scheme SCHEME = Scheme.HTTPS;
    private static final String HOST = "api-knowledgebase.mlp.cn-beijing.volces.com";
    private static final String REGION = "cn-beijing";
    private static final String PROJECT = "default";
    private static final String COLLECTION_NAME = "your_collection_name";
    private static final String COLLECTION_RESOURCE_ID = "";
    private static final String DOC_ID = "your_doc_id";

    public static void main(String[] args) throws Exception {
        String apiKey = getEnv("VIKING_API_KEY");
        if (apiKey.isEmpty()) {
            System.out.println("missing_auth: set VIKING_API_KEY");
            return;
        }
        Auth auth = new AuthWithApiKey(apiKey);

        KnowledgeService service = newKnowledgeService(auth);
        KnowledgeCollectionClient kc = service.collection(defaultCollectionMeta());

        List<MetaItem> meta = new ArrayList<>();
        meta.add(MetaItem.builder().fieldName("category").fieldType("string")
                .fieldValue("your_category").build());
        meta.add(MetaItem.builder().fieldName("updated_at").fieldType("int64")
                .fieldValue(System.currentTimeMillis() / 1000).build());

        BaseResponse resp = kc.updateDocMeta(DOC_ID, meta, new RequestAddition());
        printJson("update_doc_meta", resp);
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


