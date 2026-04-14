# 概述
SearchByKeywords 用于关键词检索，适用于带有 text 字段向量化配置（vectorize 参数）的索引，支持多个关键词检索。
# 方法定义
```go
resp, err := client.Index(indexLocator).SearchByKeywords(ctx, req)
```

# **请求参数**
请求参数是 `SearchByKeywordsRequest`，其字段如下表所示。
| **参数** | **类型** | **是否必选** | **说明** |
| --- | --- | --- | --- |
| Keywords | []string | 是 | 关键词列表，列表元素 1-10 个，元素不允许为空字符串。 |
| CaseSensitive | bool | 否 | 是否大小写严格。默认 false。 |
| Filter | map[string]interface{} | 否 | 过滤条件，详见**标量过滤** <br>  <br> * 默认为空，不做过滤。 <br> * 过滤条件包含 must、must_not、range、range_out 四类查询算子，包含 and 和 or 两种对查询算子的组合。 |
| OutputFields | []string | 否 | 要返回的标量字段列表。 <br>  <br> 1. 用户不传 output_fields 时, 返回所有标量字段 <br> 2. 用户传一个空列表不返回标量字段 <br> 3. output_fields格式错误或者过滤字段不是 collection 里的字段时, 接口返回错误 |
| Limit | int | 否 | 检索结果数量，最大 5000 个。 |
| Offset | int | 否 | 偏移量。仅分页场景下使用，不建议设置过大值，否则有深分页影响。默认值为 0。设置值至少为 0，语义和 MySQL 的 offset 相同。 |
| Advance | SearchAdvance | 否 | 高级参数，详见[检索公共参数](/docs/84313/1927082) |
# 返回参数

* SearchResult

| **属性** | 类型 | **说明** |
| --- | --- | --- |
| Data | []SearchItemResult | 见下 |
| FilterMatchedCount | int | 满足过滤条件的文档总数。 |
| TotalReturnCount | int | 本次返回的结果数量。 |
| RealTextQuery | string | 模型可能修正后的真实查询串。 |
| TokenUsage | map[string]interface{} | token 计量信息。 |

* SearchItemResult

| **属性** | 类型 | **说明** |
| --- | --- | --- |
| ID | interface{} | 主键 id。 |
| Fields | map[string]interface{} | 请求返回中的 fields 字段 |
| Score | float64 | 相似度得分。 |
| AnnScore | float64 | ANN 得分。 |
# 示例
## 请求参数
```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "github.com/volcengine/vikingdb-go-sdk/vector"
    "github.com/volcengine/vikingdb-go-sdk/vector/model"
    "os"
    "time"
)

func main() {
    var (
       accessKey = os.Getenv("VIKINGDB_AK")
       secretKey = os.Getenv("VIKINGDB_SK")
       endpoint  = "https://api-vikingdb.vikingdb.cn-beijing.volces.com"
       region    = "cn-beijing"
    )

    client, err := vector.New(
       vector.AuthIAM(accessKey, secretKey), // IAM auth
       // vector.AuthAPIKey(apiKey),            // APIKey auth
       vector.WithEndpoint(endpoint),
       vector.WithRegion(region),
       vector.WithTimeout(time.Second*30),
       vector.WithMaxRetries(3),
    )
    if err != nil {
       fmt.Println("New client failed, err: ", err)
       panic(err)
    }
    ctx := context.Background()

    var (
       limit = 10
    )

    resp, err := client.Index(model.IndexLocator{
       CollectionLocator: model.CollectionLocator{
          CollectionName: "Your Collection Name",
       },
       IndexName: "Your Index Name",
    }).SearchByKeywords(ctx, model.SearchByKeywordsRequest{
       SearchBase: model.SearchBase{
          Limit: &limit,
       },
       Keywords:      []string{"viking"},
       CaseSensitive: false,
    })

    if err != nil {
       fmt.Println("SearchByKeywords failed, err: ", err)
       panic(err)
    }

    jsonData, err := json.Marshal(resp.Result)
    if err != nil {
       fmt.Println("Marshal result failed, err: ", err)
       panic(err)
    }
    fmt.Println(string(jsonData))
}
```


