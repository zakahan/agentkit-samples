# 概述
get_doc 用于查看知识库下的文档信息。
# **请求参数**
| **参数** | **类型** | **是否必选** | **默认值** | **参数说明** |
| --- | --- | --- | --- | --- |
| collectionName | String | 否 | -- | **知识库名称** |
| projectName | String | 否 | default | **知识库所属项目，获取方式参见文档**[API 接入与技术支持](/c8p1dfoq/y97x844a) <br> 若不指定该字段，则在 default 项目下查询。 <br> 若需要操作指定项目下的知识库，需正确配置该字段。 |
| resourceId | String | 否 | -- | **知识库唯一 id** <br> 可选择直接传 resourceId，或同时传 collectionName 和 projectName 作为知识库的唯一标识 |
| docId | String | 是 | -- | **要查询的文档 id** |
| returnTokenUsage | Boolean | 否 | false | **是否返回文档向量化和文档生成摘要所消耗的 tokens** |
# **响应消息**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| collectionName | String | 知识库名称 |
| docName | String | 文档名称 |
| docHash | String | 文档 hash |
| docId | String | 文档 id |
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
| totalTokens | Object | token 统计 |
| docSummaryTokens | Integer | 摘要 token 统计 |
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
| docSummaryStatusCode | Integer | 摘要状态码 |
## failed_code 报错码：
| **failed_code** | **错误描述** | **处理建议** |
| --- | --- | --- |
| 10001 | 文档下载超时 | 请上传重试。如果问题仍然存在，请联系我们 |
| 10003 | url 校验失败，请确认 url 链接 | 请确认 url 链接正确后重试。如果问题仍然存在，请联系我们 |
| 10005 | 飞书文档获取异常，请确认有效且授权 | 请确认飞书文档权限问题，通过飞书开放平台 OpenAPI [飞书开放平台](https://open.larkoffice.com/document/server-docs/docs/docs-overview)确认权限 |
| 30001 | 超过知识库文件限制大小 | 超过知识库配额限制。[配额说明参考](https://www.volcengine.com/docs/84313/1339026) |
| 35001 | 超过知识库切片数量限制 | 超过知识库配额限制。[配额说明参考](https://www.volcengine.com/docs/84313/1339026) |
| 35002 | FAQ 文档解析为空 | FAQ 文档解析结果为空，切片数为 0。请确保文档中包含有效数据 |
| 35004 | 超过知识库 FAQ 文档 sheet 数量限制 | 超过知识库配额限制。[配额说明参考](https://www.volcengine.com/docs/84313/1339026) |
| 36003 | 结构化文档表头不匹配 | 结构化文档表头不匹配，请确保上传文档中每个 sheet 的表头与预定义的知识库表结构完全一致 |
| 36004 | 结构化文档数据类型转换失败 | 结构化文档数据类型转换失败，请确保上传文档中每个 sheet 的单元格的内容格式与预定义的知识库表结构数据类型完全一致 |
| 36005 | 超过知识库结构化文档 sheet 数量限制 | 超过知识库配额限制。[配额说明参考](https://www.volcengine.com/docs/84313/1339026) |
| 36006 | 超过知识库结构化文档有效行数限制 | 超过知识库配额限制。[配额说明参考](https://www.volcengine.com/docs/84313/1339026) |
| 36007 | 结构化文档解析为空 | 结构化文档解析结果为空，切片数为 0。请确保文档中包含有效数据 |
| 36008 | embedding 的列组合长度超出限制 | 缩短待 embedding 原始文本长度 |
| 其他错误码 | 未知错误，请联系我们 | 未知错误，请联系我们 |
## **状态码说明**
| **状态码** | **http状态码** | **返回信息** | **状态码说明** |
| --- | --- | --- | --- |
| 0 | 200 | success | 成功 |
| 1000001 | 401 | unauthorized | 鉴权失败 |
| 1000002 | 403 | no permission | 权限不足 |
| 1000003 | 400 | invalid request：%s | 非法参数 |
| 1000005 | 400 | collection not exist | collection 不存在 |
| 1001001 | 400 | doc not exist | doc 不存在 |
# 请求示例
首次使用知识库 SDK，可参考 [使用说明](https://www.volcengine.com/docs/84313/2277191?lang=zh)
本示例演示了知识库 Java SDK 中 GetDoc 的基础使用方法，通过指定文档 ID 实现单篇文档查询，使用前需配置 API Key 鉴权参数（VIKING_API_KEY）。
```java
package com.volcengine.vikingdb.runtime.knowledge.examples.doc_get;

import com.fasterxml.jackson.databind.ObjectWriter;
import com.volcengine.vikingdb.runtime.core.ApiClient;
import com.volcengine.vikingdb.runtime.core.RequestAddition;
import com.volcengine.vikingdb.runtime.core.auth.Auth;
import com.volcengine.vikingdb.runtime.core.auth.AuthWithApiKey;
import com.volcengine.vikingdb.runtime.enums.Scheme;
import com.volcengine.vikingdb.runtime.knowledge.model.CollectionMeta;
import com.volcengine.vikingdb.runtime.knowledge.model.response.DocInfo;
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

        DocInfo resp = kc.getDoc(DOC_ID, true, new RequestAddition());
        printJson("get_doc", resp);
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


