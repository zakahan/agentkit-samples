# 概述
list_points 用于查看知识库下的切片列表，默认按照 point_id 从小到大排序
# **请求参数**
| **参数** | **类型** | **是否必选** | **默认值** | **参数说明** |
| --- | --- | --- | --- | --- |
| collectionName | String | 否 | -- | **知识库名称** |
| projectName | String | 否 | default | **知识库所属项目，获取方式参见文档**[API 接入与技术支持](/c8p1dfoq/y97x844a) <br> 若不指定该字段，则在default项目下创建。 <br> 若需要操作指定项目下的知识库，需正确配置该字段。 |
| resourceId | String | 否 | -- | **知识库唯一 id** <br> 可选择直接传 resourceId，或同时传 collectionName 和 projectName 作为知识库的唯一标识 |
| offset | Integer | 否 | 0 | **用于分页** <br> 表示从结果的第几个开始取，需要大于等于 0 |
| limit | Integer | 否 | -1 | **返回切片个数** <br> -1 表示获取所有，最大值不超过 100，每次返回最多不超过 100 |
| docIds | String[] | 否 | -- | **按文档 id 筛选** <br> 指定文档返回对应切片列表，不传或为 null 表示不筛选，传入的 size 为 0 将返回空结果。限制 list 长度，最大长度为 100 |
| pointIds | String[] | 否 | -- | **按照切片 id 筛选** <br> 指定一个或多个切片 id 返回对应切片内容，不传或为 null 表示不筛选，传入的 size 为 0 将返回空结果。限制切片 id 最大长度为 100 |
| getAttachmentLink | Boolean | 否 | false | **是否获取切片中图片的临时下载链接** <br> 10 分钟有效期 |
# **响应消息**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码 |
| message | String | 返回信息 |
| requestId | String | 标识每个请求的唯一标识符 |
| data | ListPointsResult | ListPointsResult |
| count | Integer | 本次返回的结果数量 |
| totalNum | Integer | 总共有多少个结果 |
### **ListPointsResult**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| pointList | List | 切片信息列表 |
### **PointInfo**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| collectionName | String | 知识库名称 |
| pointId | String | 切片 id（知识库下唯一） |
| docInfo | PointDocInfo | PointDocInfo |
| processTime | Long | 切片处理完成的时间 |
| originText | String | 原始文本 |
| mdContent | String | 切片 markdown 解析结果，保留更多的原始表格信息（chunk_type 为 table 时会返回） |
| htmlContent | String | 切片 html 解析结果，保留更多的原始表格信息（chunk_type 为 table 时会返回） |
| chunkTitle | String | 切片标题，是由解析模型识别出来的上一层级的标题。若没有上一层级标题则为空 |
| chunkType | String | 切片所属类型 |
| description | String | 文档描述（当前仅支持图片文档） |
| content | String | 切片内容 |
| chunkId | Long | 切片位次 id，代表在原始文档中的位次顺序 |
| originalQuestion | String | FAQ 数据检索召回答案对应的原始问题 |
| tableChunkFields | List | 结构化数据检索返回单行全量数据 |
| chunkAttachment | List | 附件信息（GetAttachmentLink 为 true 时返回临时链接，10 分钟有效期） |
| rerankScore | Double | 重排得分 |
| score | Double | 检索得分 |
| updateTime | Long | 更新时间 |
| chunkSource | String | 切片来源 |
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
| uuid | String | 附件 uuid |
| caption | String | 附件说明 |
| type | String | 附件类型 |
| link | String | 附件链接 |
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
| 1000001 | 401 | unauthorized | 鉴权失败 |
| 1000002 | 403 | no permission | 权限不足 |
| 1000003 | 400 | invalid request：%s | 非法参数 |
| 1000005 | 400 | collection not exist | collection 不存在 |
# 请求示例
首次使用知识库 SDK，可参考 [使用说明](https://www.volcengine.com/docs/84313/2277191?lang=zh)
本示例演示了知识库 Java SDK 中 ListPoints 的基础使用方法，通过指定知识库信息查询切片列表，使用前需配置 API Key 鉴权参数（VIKING_API_KEY）。
```java
package com.volcengine.vikingdb.runtime.knowledge.examples.point_list;

import com.fasterxml.jackson.databind.ObjectWriter;
import com.volcengine.vikingdb.runtime.core.ApiClient;
import com.volcengine.vikingdb.runtime.core.RequestAddition;
import com.volcengine.vikingdb.runtime.core.auth.Auth;
import com.volcengine.vikingdb.runtime.core.auth.AuthWithApiKey;
import com.volcengine.vikingdb.runtime.enums.Scheme;
import com.volcengine.vikingdb.runtime.knowledge.model.CollectionMeta;
import com.volcengine.vikingdb.runtime.knowledge.model.request.ListPointsRequest;
import com.volcengine.vikingdb.runtime.knowledge.model.response.ListPointsResponse;
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

        ListPointsRequest req = ListPointsRequest.builder()
                .offset(0)
                .limit(10)
                .getAttachmentLink(true)
                .build();
        ListPointsResponse resp = kc.listPoints(req, new RequestAddition());
        printJson("list_points", resp);
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


