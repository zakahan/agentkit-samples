# 概述
按特定条件批量删除 Collection 中的数据。
# 方法定义
Go SDK 通过 `vikingdb.New(sess)` 创建的客户端实例调用 `CreateVikingdbTask(input)` 方法发起任务创建请求，input 参数类型为 `vikingdb.CreateVikingdbTaskInput`，包含任务创建所需的完整配置信息。
# 请求参数
若要将数据备份至 TOS，请先授权 VikingDB 跨服务访问 TOS：[去授权](https://console.volcengine.com/iam/service/attach_role/?ServiceName=vikingdb)

| 参数 | 子参数 | 类型 | 是否必填 | 描述 |
| --- | --- | --- | --- | --- |
| ProjectName |  | string | 否 | 项目名称 |
| CollectionName |  | string | 2选1 | 数据集名称 |
| ResourceId |  | string |  | 数据集资源 ID。请求必须指定 ResourceId 和 CollectionName 其中之一。 |
| **TaskType** |  | string | 是 | filter_delete |
| TaskConfig |  | TaskConfigForCreateVikingdbTaskInput | 是 | 任务具体配置 |
|  | FileType | string | 是 | 备份文件类型，json 或 parquet。必填。 |
|  | NeedConfirm | bool | 否 | 是否需要人工确认环节，默认为 true。 |
|  | FilterConds | []interface{} | 是 | 过滤条件。使用参考：https://www.volcengine.com/docs/84313/1791133 |
|  | TosPath | string | 是 | TOS 路径，格式：{桶名}/{路径}，注意不是域名。必填。 |
# 返回参数
| 参数 | 类型 | 描述 |
| --- | --- | --- |
| TaskId | string | 任务ID |
| Message | string | 操作结果信息 |
# 示例
## 请求参数
```Go
package main

import (
    "fmt"
    "os"

    "github.com/volcengine/volcengine-go-sdk/service/vikingdb"
    "github.com/volcengine/volcengine-go-sdk/volcengine"
    "github.com/volcengine/volcengine-go-sdk/volcengine/credentials"
    "github.com/volcengine/volcengine-go-sdk/volcengine/session"
)

func main() {
    var (
       accessKey = os.Getenv("VIKINGDB_AK")
       secretKey = os.Getenv("VIKINGDB_SK")
       region    = "cn-beijing"
    )

    config := volcengine.NewConfig().
       WithRegion(region).
       WithCredentials(credentials.NewStaticCredentials(accessKey, secretKey, ""))

    sess, err := session.NewSession(config)
    if err != nil {
       panic(err)
    }
    svc := vikingdb.New(sess)

    // 创建过滤删除任务
    input := &vikingdb.CreateVikingdbTaskInput{
       TaskType: volcengine.String(vikingdb.EnumOfTaskTypeForCreateVikingdbTaskInputFilterDelete),
       TaskConfig: &vikingdb.TaskConfigForCreateVikingdbTaskInput{
          FilterConds: []interface{}{
             map[string]interface{}{
                "op":    "must",
                "field": "name",
                "conds": []string{"old value1", "old value2"},
             },
          },
          NeedConfirm: volcengine.Bool(true),
          TosPath:      volcengine.String("your-bucket/path/to/backup.json"),
          FileType:     volcengine.String("json"),
       },
       CollectionName: volcengine.String("Your Collection Name"),
       ProjectName:    volcengine.String("default"),
    }

    resp, err := svc.CreateVikingdbTask(input)
    if err != nil {
       panic(err)
    }

    fmt.Println(*resp.TaskId)
}
```

## 返回参数
| 参数 | 类型 | 示例值 | 描述 |
| --- | --- | --- | --- |
| TaskId | string |  | 任务ID |
| Message | string | success | 操作结果信息 |
## 后续处理
如果 NeedConfirm 为 true 且需要人工确认，可执行 **任务更新** 操作进行确认。

