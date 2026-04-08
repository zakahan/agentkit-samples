#!/usr/bin/env python3
# Copyright 2024 ByteDance, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
市场洞察 Agent — ListCustomSubsTask 完整调用示例 (Python)

功能：通过 ListCustomSubsTask 接口分页查询当前账号下所有订阅/监控任务列表，
      支持按状态过滤和任务名称模糊搜索，自动处理分页循环。

使用方式：
  python list_custom_subs_task.py                           # 查询全部任务
  python list_custom_subs_task.py --status 1                # 只看运行中的任务
  python list_custom_subs_task.py --task_name "品牌"         # 按名称搜索
  python list_custom_subs_task.py --page_size 20 --status 1 # 组合使用

使用前准备：
  设置环境变量：
    export ARK_SKILL_API_BASE="https://sd6tqd9ef5hajtf86dic0.apigateway-cn-beijing.volceapi.com"
    export ARK_SKILL_API_KEY="你的APIKey"

响应结构说明：
- Result.InsightSaasTaskList: 任务列表数组
- Result.Total: 总任务数
- 每个 Task 包含: TaskID, Name, Aim, Status, PushStatus,
  CreateTime, ModifyTime, PreviewList 等
  注意：新接口中 Status/PushStatus/CreateTime 的类型为 str（非 int）
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# ===================== 默认值（命令行参数可覆盖） =====================
DEFAULT_STATUS = 2                      # 任务状态过滤：1=运行中, 2=全部状态
DEFAULT_PAGE_SIZE = 30                  # 每页条数
API_VERSION = "2025-09-05"              # 接口版本
REQUEST_INTERVAL = 0.1                  # 请求间隔（秒），避免触发限流
# =====================================================================

STATUS_MAP = {"0": "已关闭", "1": "运行中", 0: "已关闭", 1: "运行中"}


# ===================== 环境变量读取与通用请求 =====================

def _read_env() -> Tuple[str, str]:
    """读取 API 鉴权所需的环境变量"""
    api_host = os.getenv("ARK_SKILL_API_BASE")
    api_key = os.getenv("ARK_SKILL_API_KEY")
    if not api_host or not api_key:
        print("错误：缺少必要环境变量，请先设置：")
        print('  export ARK_SKILL_API_BASE="你的API地址"')
        print('  export ARK_SKILL_API_KEY="你的APIKey"')
        raise SystemExit("缺少必要环境变量: ARK_SKILL_API_BASE, ARK_SKILL_API_KEY")
    return api_host.strip(), api_key.strip()


def _get_json(url: str, payload: Dict[str, Any], api_key: str) -> Tuple[bytes, Dict[str, str]]:
    """发送 GET 请求（带 JSON Body），使用 Bearer Token 鉴权

    注意：该接口要求 GET 方法 + JSON Body，与常规 RESTful 不同。
    通过重写 get_method 强制 urllib 以 GET 方式发送带 Body 的请求。
    """
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": f"Bearer {api_key}",
        "ServiceName": "insight",
    }
    req = urllib.request.Request(url, data=data, headers=headers)
    # 关键：强制使用 GET 方法（urllib 有 data 时默认 POST）
    req.get_method = lambda: "GET"

    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read()
        resp_headers = {k: v for k, v in resp.getheaders()}
        return body, resp_headers


def _json_loads_or_none(data: bytes) -> Optional[Dict[str, Any]]:
    """安全地解析 JSON，失败返回 None"""
    try:
        return json.loads(data.decode("utf-8"))
    except Exception:
        return None


# ===================== 命令行参数 =====================

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="查询订阅/监控任务列表（ListCustomSubsTask）"
    )
    parser.add_argument(
        "--status", type=int, default=DEFAULT_STATUS, choices=[1, 2],
        help="任务状态过滤：1=运行中, 2=全部状态（默认 2）"
    )
    parser.add_argument(
        "--task_name", type=str, default=None,
        help="按任务名称模糊搜索（不传则不过滤）"
    )
    parser.add_argument(
        "--page_size", type=int, default=DEFAULT_PAGE_SIZE,
        help=f"每页条数，默认 {DEFAULT_PAGE_SIZE}"
    )
    return parser.parse_args()


# ===================== 工具函数 =====================

def ts_to_str(ts):
    """将时间戳或时间字符串转换为可读时间字符串

    注意：新接口中 CreateTime 类型为 str，可能是时间戳字符串或已格式化的时间。
    """
    if not ts:
        return "-"
    try:
        numeric_ts = int(ts) if isinstance(ts, str) else ts
        return datetime.fromtimestamp(numeric_ts).strftime("%Y-%m-%d %H:%M:%S")
    except (OSError, ValueError, TypeError):
        return str(ts)


# ===================== 核心：调用 ListCustomSubsTask =====================

def list_custom_subs_task(
    api_host: str,
    api_key: str,
    status: int,
    task_name: Optional[str],
    page_num: int,
    page_size: int,
) -> Dict[str, Any]:
    """调用 ListCustomSubsTask 接口查询单页任务列表

    Args:
        api_host:  API 基地址（不含路径和查询参数）
        api_key:   Bearer Token
        status:    状态过滤 (1=运行中, 2=全部)
        task_name: 名称模糊搜索（None 则不过滤）
        page_num:  页码（从 1 开始）
        page_size: 每页条数

    Returns:
        解析后的 Result 字典（已自动展开外层包装）
    """
    # URL 包含 Action 和 Version 查询参数
    url = f"{api_host}/?Action=ListCustomSubsTask&Version={API_VERSION}"

    payload: Dict[str, Any] = {
        "Status": status,
        "PageNum": page_num,
        "PageSize": page_size,
    }
    if task_name:
        payload["TaskName"] = task_name

    print(f"[DEBUG] 调用 ListCustomSubsTask: url={url}")
    print(f"[DEBUG] 请求 payload: {json.dumps(payload, ensure_ascii=False)}")

    body, resp_headers = _get_json(url, payload, api_key)

    print(f"[DEBUG] 响应头: {resp_headers}")
    print(f"[DEBUG] 响应体长度: {len(body)} 字节")
    try:
        body_str = body.decode("utf-8")
        print(f"[DEBUG] 响应体前 1000 字符: {body_str[:1000]}...")
    except Exception as e:
        print(f"[DEBUG] 响应体解码失败: {e}")

    data = _json_loads_or_none(body)
    if not data:
        raise SystemExit("ListCustomSubsTask 响应不是有效的 JSON")

    # 从 Result 包装层提取实际数据
    result = data.get("Result")
    if not isinstance(result, dict):
        print(f"[DEBUG] 响应 JSON 顶层 keys: {list(data.keys())}")
        print(f"[DEBUG] 完整响应: {json.dumps(data, ensure_ascii=False)[:2000]}")
        raise SystemExit("ListCustomSubsTask 响应不包含有效的 Result 字段")

    if "InsightSaasTaskList" not in result:
        print(f"[DEBUG] Result 内 keys: {list(result.keys())}")
        print(f"[DEBUG] 完整 Result: {json.dumps(result, ensure_ascii=False)[:2000]}")
        raise SystemExit("ListCustomSubsTask Result 不包含 InsightSaasTaskList 字段")

    print(f"[DEBUG] InsightSaasTaskList 数量: {len(result.get('InsightSaasTaskList', []))}")
    return result


# ===================== 分页循环查询 =====================

def list_all_tasks(
    api_host: str,
    api_key: str,
    status: int,
    task_name: Optional[str],
    page_size: int,
) -> List[Dict[str, Any]]:
    """分页查询所有订阅任务"""
    page_num = 1
    all_tasks: List[Dict[str, Any]] = []

    while True:
        try:
            data = list_custom_subs_task(
                api_host, api_key, status, task_name, page_num, page_size
            )
        except SystemExit:
            raise
        except Exception as e:
            print(f"\n未预期的错误 (第 {page_num} 页): {e}")
            break

        tasks = data.get("InsightSaasTaskList") or []
        total = data.get("Total") or 0
        # Total 可能是 str 类型
        try:
            total = int(total)
        except (ValueError, TypeError):
            total = 0

        all_tasks.extend(tasks)

        print(f"第 {page_num} 页：获取 {len(tasks)} 个任务（累计 {len(all_tasks)}/{total}）")

        for task in tasks:
            tid = task.get("TaskID", "-")
            name = task.get("Name", "-")
            s = task.get("Status")
            status_text = STATUS_MAP.get(s, str(s))
            aim = task.get("Aim", "")
            print(f"  [{tid}] {name} ({status_text}) — {aim}")

            # 显示预览列表（如果有）
            preview_list = task.get("PreviewList") or []
            for preview in preview_list[:2]:  # 最多显示 2 条预览
                p_title = preview.get("Title", "") if isinstance(preview, dict) else ""
                if p_title:
                    print(f"      预览: {p_title[:60]}...")

        # 检查是否还有更多页
        if page_num * page_size >= total:
            print(f"\n任务列表查询完成！共 {total} 个任务，{page_num} 页。")
            break

        page_num += 1
        time.sleep(REQUEST_INTERVAL)

    return all_tasks


# ===================== 摘要输出 =====================

def print_summary(tasks: List[Dict[str, Any]]):
    """打印任务摘要统计"""
    if not tasks:
        print("未查询到任何任务。")
        return

    print("\n" + "=" * 80)
    print("订阅任务列表摘要")
    print("=" * 80)
    print(f"总任务数: {len(tasks)}")

    # 按状态统计
    status_counts: Dict[str, int] = {}
    for t in tasks:
        s = t.get("Status")
        status_text = STATUS_MAP.get(s, str(s))
        status_counts[status_text] = status_counts.get(status_text, 0) + 1
    if status_counts:
        print(f"\n状态分布:")
        for s, count in sorted(status_counts.items(), key=lambda x: -x[1]):
            print(f"  {s}: {count} 个")

    # 输出详细列表
    print(f"\n  {'TaskID':<10} {'任务名称':<24} {'状态':<8} {'推送':<6} {'创建时间':<20} {'意图':<20}")
    print("  " + "-" * 90)
    for t in tasks:
        tid = t.get("TaskID", "-")
        name = t.get("Name", "-")
        s = t.get("Status")
        status_text = STATUS_MAP.get(s, str(s))
        push_status = t.get("PushStatus")
        push_text = "开启" if str(push_status) == "1" else "关闭"
        create_time = t.get("CreateTime")
        aim = t.get("Aim", "-")

        # 截断过长的名称和意图
        if isinstance(name, str) and len(name) > 22:
            name = name[:19] + "..."
        if isinstance(aim, str) and len(aim) > 18:
            aim = aim[:15] + "..."

        print(f"  {tid:<10} {name:<24} {status_text:<8} {push_text:<6} {ts_to_str(create_time):<20} {aim:<20}")


# ===================== 主入口 =====================

if __name__ == "__main__":
    args = parse_args()

    print("=" * 80)
    print("市场洞察 Agent — ListCustomSubsTask 订阅任务列表查询 (APIKey 模式)")
    print("=" * 80)
    status_text = {1: "运行中", 2: "全部"}.get(args.status, str(args.status))
    print(f"状态过滤: {status_text}")
    if args.task_name:
        print(f"名称搜索: {args.task_name}")
    print(f"每页条数: {args.page_size}")
    print()

    try:
        api_host, api_key = _read_env()
        print(f"API 鉴权初始化完成 (Host: {api_host})")
        print()

        tasks = list_all_tasks(api_host, api_key, args.status, args.task_name, args.page_size)
        print_summary(tasks)

    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8")
        except Exception:
            detail = ""
        raise SystemExit(f"HTTP 错误: {e.code} {e.reason} {detail}".strip())
    except urllib.error.URLError as e:
        raise SystemExit(f"网络错误: {e.reason}")
    except KeyboardInterrupt:
        raise SystemExit("已中断")
