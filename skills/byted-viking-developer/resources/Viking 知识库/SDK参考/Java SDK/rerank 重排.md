本节将说明如何单独调用 rerank 模型，以计算两段文本间的相似度。
## **概述**
rerank 用于批量计算输入文本与检索到的文本之间的 score 值，以对召回结果进行重排序。判断依据为 chunk content 能回答 query 的概率，分数越高即模型认为该文本片段能回答 query 的概率越大。
## **请求参数**
| **参数** | **类型** | **是否必选** | **默认值** | **参数说明** |
| --- | --- | --- | --- | --- |
| datas | List | 是 | -- | **待重排的数据列表** <br> 每个元素为一个 Map，数组长度不超过 200，支持以下参数： <br>  <br> * query（必选）：用于排序的查询内容，Object <br> * string：纯文本查询内容，重排模型通用 <br> * object：文本或图片查询内容，**仅适用于 doubao-seed-rerank 模型** <br> * content（可选）：待排序的文本内容，String <br> * image（可选）：待排序的图片内容，Object（String 单张或 String[] 多张），**仅适用于 doubao-seed-rerank 模型** <br> * 支持传入公开访问的 http/https 链接 <br> * 支持 jpeg、png、webp、bmp 格式的 base64 编码，单张图片小于 3 MB，请求体不能超过 4 MB <br> * title（可选）：文档的标题 |
| endpointId | String | 否 | -- | **推理接入点 ID** |
| rerankModel | String | 否 | "base-multilingual-rerank" | **rerank 模型** <br> 可选模型： <br> *"doubao-seed-rerank"（即 doubao-seed-1.6-rerank）：字节自研多模态重排模型、支持文本 / 图片 / 视频 混合重排、精细语义匹配、可选阈值过滤与指令设置**（推荐）** <br>  <br> * "base-multilingual-rerank"：速度快、长文本、支持 70+ 种语言 <br> * "m3-v2-rerank"：常规文本、支持 100+ 种语言 |
| rerankInstruction | String | 否 | -- | **重排指令** <br> **仅当 rerankModel=="doubao-seed-rerank" 时生效**，用于提供给模型一个明确的排序指令，提升重排效果。字符串长度不超过 1024 <br> *如，Whether the document answers the query or matches the content retrieval intent* |
## **响应消息**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| code | Integer | 状态码 |
| message | String | 错误信息 |
| requestId | String | 请求的唯一标识符 |
| data | RerankResult | 重排结果 |
### **RerankResult**
| **字段** | **类型** | **参数说明** |
| --- | --- | --- |
| scores | List | 与输入 datas 数组一一对应，表示每个文档与 query 的相关性得分 |
| tokenUsage | Integer | 本次 rerank 调用消耗的总 token 数量 |
### **状态码说明**
| **状态码** | **http 状态码** | **返回信息** | **状态码说明** |
| --- | --- | --- | --- |
| 0 | 200 | success | 成功 |
| 1000001 | 403 | VolcanoErrUnauthorized | 鉴权失败 |
| 1000002 | 400 | VolcanoErrInvalidRequest | 请求参数无效（当 query 缺失，或 datas 中所有文档都未提供任一媒体/文本内容时触发） |
| 300004 | 429 | VolcanoErrQuotaLimiter | 账户的 rerank 调用已达到配额限制 |
| 1000028 | 500 | VolcanoErrInternal | 服务内部错误，rerank 模型过载 |
## 请求示例
首次使用知识库 SDK，可参考 [使用说明](https://www.volcengine.com/docs/84313/2277191?lang=zh)。
本示例演示了知识库 Java SDK 中 Rerank 的基础使用方法，通过传入查询语句和待排序内容列表实现结果重排序。使用前需配置 API Key 鉴权参数（VIKING_API_KEY）。
```java
package com.volcengine.vikingdb.runtime.knowledge.examples.rerank;

import com.fasterxml.jackson.databind.ObjectWriter;
import com.volcengine.vikingdb.runtime.core.ApiClient;
import com.volcengine.vikingdb.runtime.core.RequestAddition;
import com.volcengine.vikingdb.runtime.core.auth.Auth;
import com.volcengine.vikingdb.runtime.core.auth.AuthWithApiKey;
import com.volcengine.vikingdb.runtime.enums.Scheme;
import com.volcengine.vikingdb.runtime.knowledge.model.request.RerankDataItem;
import com.volcengine.vikingdb.runtime.knowledge.model.request.RerankRequest;
import com.volcengine.vikingdb.runtime.knowledge.model.response.RerankResponse;
import com.volcengine.vikingdb.runtime.knowledge.service.KnowledgeService;

import java.util.Arrays;

public class Main {
    private static final ObjectWriter PRETTY_JSON = ApiClient.objectMapper.writerWithDefaultPrettyPrinter();
    private static final Scheme SCHEME = Scheme.HTTPS;
    private static final String HOST = "api-knowledgebase.mlp.cn-beijing.volces.com";
    private static final String REGION = "cn-beijing";

    public static void main(String[] args) throws Exception {
        String apiKey = getEnv("VIKING_API_KEY");
        if (apiKey.isEmpty()) {
            System.out.println("missing_auth: set VIKING_API_KEY");
            return;
        }
        Auth auth = new AuthWithApiKey(apiKey);
        KnowledgeService service = newKnowledgeService(auth);

        String query = "Your Query";
        RerankRequest req = RerankRequest.builder()
                .rerankModel("Doubao-pro-4k-rerank")
                .datas(Arrays.asList(
                        RerankDataItem.builder().query(query).title("Revenue").content("Revenue grew 12% YoY to $3.4B.")
                                .build(),
                        RerankDataItem.builder().query(query).title("Margin")
                                .content("Operating margin improved by 1.5pp to 17%.").build()))
                .build();
        RerankResponse resp = service.rerank(req, new RequestAddition());
        printJson("rerank", resp);
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


