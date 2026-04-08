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
市场洞察 Agent — PullPost 完整调用示例 (Python)

功能：通过 PullPost 接口拉取指定监测任务的 AI 精筛数据，
      自动处理分页循环，直到所有数据消费完毕。

使用方式：
  python pull_post_python.py \
    --task_id 1509 \
    --start_time "2026-01-20 00:00:00" \
    --end_time "2026-01-21 00:00:00" \
    --size 50

使用前准备：
  设置环境变量：
    export ARK_SKILL_API_BASE="https://sd6tqd9ef5hajtf86dic0.apigateway-cn-beijing.volceapi.com"
    export ARK_SKILL_API_KEY="你的密钥"

官方文档：https://www.volcengine.com/docs/83600/1174737

请求方式：POST
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


# ===================== 默认值（命令行参数可覆盖） =====================
DEFAULT_PAGE_SIZE = 50                  # 每页条数（默认 50，最大 100）
API_VERSION = "2025-09-05"              # 接口版本
REQUEST_INTERVAL = 0.1                  # 请求间隔（秒），避免触发限流
# =====================================================================


# ===================== 环境变量读取与通用请求 =====================

def _read_env() -> Tuple[str, str]:
    """读取 API 鉴权所需的环境变量"""
    api_host = os.getenv("ARK_SKILL_API_BASE")
    api_key = os.getenv("ARK_SKILL_API_KEY")
    if not api_host or not api_key:
        print("错误：缺少必要环境变量，请先设置：")
        print('  export ARK_SKILL_API_BASE="你的API地址"')
        print('  export ARK_SKILL_API_KEY="你的密钥"')
        raise SystemExit("缺少必要环境变量: ARK_SKILL_API_BASE, ARK_SKILL_API_KEY")
    return api_host.strip(), api_key.strip()


def _post_json(url: str, payload: Dict[str, Any], api_key: str) -> Tuple[bytes, Dict[str, str]]:
    """发送 POST 请求（带 JSON Body），使用 Bearer Token 鉴权

    PullPost 接口要求 POST 方法 + JSON Body。
    """
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": f"Bearer {api_key}",
        "ServiceName": "insight",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

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
        description="通过 PullPost 接口拉取指定监测任务的 AI 精筛数据"
    )
    parser.add_argument(
        "--task_id", type=int, required=True,
        help="监测任务 ID（从任务管理页面 URL 获取，如 .../risk/1509 中的 1509）"
    )
    parser.add_argument(
        "--start_time", type=str, required=True,
        help='数据起始时间，格式 "YYYY-MM-DD HH:MM:SS"'
    )
    parser.add_argument(
        "--end_time", type=str, required=True,
        help='数据结束时间，格式 "YYYY-MM-DD HH:MM:SS"'
    )
    parser.add_argument(
        "--size", type=int, default=DEFAULT_PAGE_SIZE,
        help=f"每页条数，默认 {DEFAULT_PAGE_SIZE}，最大 100"
    )
    return parser.parse_args()


# ===================== 核心：调用 PullPost =====================

def pull_post(
    api_host: str,
    api_key: str,
    task_id: int,
    start_time: str,
    end_time: str,
    size: int,
    page_token: Optional[str] = None,
) -> Dict[str, Any]:
    """调用 PullPost 接口查询单页数据

    Args:
        api_host:    API 基地址（不含路径和查询参数）
        api_key:     Bearer Token
        task_id:     监测任务 ID
        start_time:  起始时间（仅首次请求生效）
        end_time:    结束时间（仅首次请求生效）
        size:        每页条数
        page_token:  分页游标（首次不传）

    Returns:
        解析后的 Result 字典（已自动展开外层包装）
    """
    # URL 包含 Action 和 Version 查询参数
    url = f"{api_host}/?Action=PullPost&Version={API_VERSION}"

    payload: Dict[str, Any] = {
        "TaskID": task_id,
        "StartTime": start_time,
        "EndTime": end_time,
        "Size": size,
    }
    if page_token:
        payload["PageToken"] = page_token

    print(f"[DEBUG] 调用 PullPost (POST): url={url}")
    print(f"[DEBUG] 请求 payload: {json.dumps(payload, ensure_ascii=False)}")

    body, resp_headers = _post_json(url, payload, api_key)

    print(f"[DEBUG] 响应头: {resp_headers}")
    print(f"[DEBUG] 响应体长度: {len(body)} 字节")
    try:
        body_str = body.decode("utf-8")
        print(f"[DEBUG] 响应体前 1000 字符: {body_str[:1000]}...")
    except Exception as e:
        print(f"[DEBUG] 响应体解码失败: {e}")

    data = _json_loads_or_none(body)
    if not data:
        raise SystemExit("PullPost 响应不是有效的 JSON")

    # 从 Result 包装层提取实际数据
    result = data.get("Result")
    if not isinstance(result, dict):
        print(f"[DEBUG] 响应 JSON 顶层 keys: {list(data.keys())}")
        print(f"[DEBUG] 完整响应: {json.dumps(data, ensure_ascii=False)[:2000]}")
        raise SystemExit("PullPost 响应不包含有效的 Result 字段")

    return result


# ===================== 分页循环拉取 =====================

def pull_all_posts(
    api_host: str,
    api_key: str,
    task_id: int,
    start_time: str,
    end_time: str,
    size: int,
) -> List[Dict[str, Any]]:
    """分页拉取所有数据"""
    page_token = None
    total_count = 0
    page_num = 0
    all_posts: List[Dict[str, Any]] = []

    while True:
        page_num += 1

        try:
            result = pull_post(
                api_host, api_key, task_id,
                start_time, end_time, size, page_token
            )
        except SystemExit:
            raise
        except Exception as e:
            print(f"\n未预期的错误 (第 {page_num} 页): {e}")
            break

        # 处理当前页数据
        docs = result.get("ItemDocs") or []
        has_more = result.get("HasMore", False)
        next_page_token = result.get("NextPageToken")
        total_count += len(docs)

        print(f"第 {page_num} 页：获取 {len(docs)} 条数据（累计 {total_count} 条）")

        for doc in docs:
            # 提取关键字段（JSON 响应中为 PascalCase）
            post_info = {
                "post_id": doc.get("PostID", ""),
                "title": doc.get("Title", ""),
                "summary": doc.get("Summary", ""),
                "url": doc.get("URL", "") or doc.get("Url", ""),
                "publish_time": doc.get("PublishTime", ""),
                "update_time": doc.get("UpdateTime", ""),
                "main_domain": doc.get("MainDomain", ""),
                "media_name": doc.get("MediaName", ""),
                "fans_count": doc.get("FansCount", 0),
                "is_follow": doc.get("IsFollow", False),
                "emotion": doc.get("Emotion", ""),
                "reason": doc.get("Reason", ""),
                "dedup_id": doc.get("DedupID", "") or doc.get("DedupId", ""),
                "risk_type": doc.get("RiskType", []),
                "content_length": len(doc.get("Content", "") or ""),
            }
            all_posts.append(post_info)

            # 打印摘要信息
            title = post_info["title"]
            print(f"  [{post_info['post_id']}] {title[:50] if title else '(无标题)'}...")
            reason = post_info["reason"]
            if reason:
                print(f"    AI 精筛原因: {reason[:80]}...")

        # 检查是否还有更多数据
        if not has_more:
            print(f"\n数据拉取完成！共 {total_count} 条数据，{page_num} 页。")
            break

        # 设置下页游标
        page_token = next_page_token

        # 请求间隔，避免限流
        time.sleep(REQUEST_INTERVAL)

    return all_posts


# ===================== 摘要输出 =====================

def print_summary(posts: List[Dict[str, Any]]):
    """打印数据摘要统计"""
    if not posts:
        print("未获取到数据。")
        return

    print("\n" + "=" * 60)
    print("数据摘要统计")
    print("=" * 60)
    print(f"总条数: {len(posts)}")

    # 来源统计
    domains: Dict[str, int] = {}
    for p in posts:
        domain = p.get("main_domain", "unknown")
        domains[domain] = domains.get(domain, 0) + 1
    print(f"\n来源分布:")
    for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"  {domain}: {count} 条")

    # 情感统计
    emotions: Dict[str, int] = {}
    for p in posts:
        emotion = p.get("emotion", "unknown")
        emotions[emotion] = emotions.get(emotion, 0) + 1
    print(f"\n情感分布:")
    for emotion, count in sorted(emotions.items(), key=lambda x: -x[1]):
        print(f"  {emotion}: {count} 条")

    # 去重统计
    unique_dedup = set(p.get("dedup_id") for p in posts if p.get("dedup_id"))
    print(f"\n聚类事件数: {len(unique_dedup)}")
    print(f"唯一帖子数: {len(set(p['post_id'] for p in posts))}")


# ===================== 主入口 =====================

if __name__ == "__main__":
    args = parse_args()

    print("=" * 60)
    print("市场洞察 Agent — PullPost 数据拉取 (Bearer Token 模式)")
    print("=" * 60)
    print(f"任务 ID: {args.task_id}")
    print(f"时间范围: {args.start_time} ~ {args.end_time}")
    print(f"每页条数: {args.size}")
    print()

    try:
        api_host, api_key = _read_env()
        print(f"API 鉴权初始化完成 (Host: {api_host})")
        print()

        posts = pull_all_posts(
            api_host, api_key, args.task_id,
            args.start_time, args.end_time, args.size
        )
        print_summary(posts)

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
