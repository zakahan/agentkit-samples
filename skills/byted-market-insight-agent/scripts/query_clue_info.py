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
市场洞察 Agent — QueryClueInfo 完整调用示例 (Python)

功能：通过 QueryClueInfo 接口查询指定时间范围内的商机信息，
      自动处理分页循环（基于 NextToken 游标分页），直到所有数据消费完毕。
      ClueText 为 JSON 字符串，包含商机评估、公司画像、竞争分析等丰富结构化数据，
      脚本会自动解析并展示关键信息。

使用方式：
  python query_clue_info.py \
    --start_time "2026-03-18 00:00:00" \
    --end_time "2026-03-18 23:00:00" \
    --max_results 10

使用前准备：
  设置环境变量：
    export ARK_SKILL_API_BASE="https://sd6tqd9ef5hajtf86dic0.apigateway-cn-beijing.volceapi.com"
    export ARK_SKILL_API_KEY="你的密钥"

请求方式：GET（与 ListCustomSubsTask 一致）

接口说明：
  - 分页方式：游标分页（NextToken），NextToken 值为时间戳字符串
  - 必填参数：StartTime、EndTime（格式 "YYYY-MM-DD HH:MM:SS"）
  - 可选参数：MaxResults（每页条数）、NextToken（分页游标）
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
DEFAULT_MAX_RESULTS = 10                # 每页条数（默认 10）
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
        description="通过 QueryClueInfo 接口查询商机信息"
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
        "--max_results", type=int, default=DEFAULT_MAX_RESULTS,
        help=f"每页条数，默认 {DEFAULT_MAX_RESULTS}"
    )
    return parser.parse_args()


# ===================== 工具函数 =====================

def parse_clue_text(clue_text_raw):
    """解析 ClueText JSON 字符串，提取结构化商机信息。

    ClueText 是一个 JSON 字符串，包含以下顶层结构：
    - opportunity_briefing: 商机简报（标题、优先级、执行摘要、关键事实）
    - company_profile: 公司画像（名称、地址、行业、联系方式）
    - acorn_assessment: ACOR 评估（客户画像/核心需求/商机价值/时机与关系维度评分）
    - competitive_analysis: 竞争分析（竞品名称、关系、应对策略）
    - deep_dive_analysis: 深度分析（事件元数据、事件摘要）
    - solution_mapping_and_value_proposition: 解决方案映射（痛点、方案、价值主张）
    - triggering_event: 触发事件（事件描述、来源）
    """
    if not clue_text_raw:
        return None
    try:
        return json.loads(clue_text_raw)
    except (json.JSONDecodeError, TypeError):
        return None


def print_clue_detail(clue_id, clue_data, create_time=None):
    """打印单条商机的详细信息"""
    if not clue_data:
        print(f"  [{clue_id}] (ClueText 解析失败或为空)")
        return

    # 商机简报
    briefing = clue_data.get("opportunity_briefing", {})
    title = briefing.get("title", "(无标题)")
    priority = briefing.get("priority_level", "-")
    summary = briefing.get("executive_summary", "")

    print(f"  [{clue_id}] [优先级:{priority}] {title}")
    if summary:
        print(f"    摘要: {summary[:120]}{'...' if len(summary) > 120 else ''}")

    # 公司画像
    company = clue_data.get("company_profile", {})
    company_name = company.get("legal_name", "")
    biz_category = company.get("business_category", "")
    if company_name:
        print(f"    公司: {company_name}  行业: {biz_category}")

    # ACOR 评分
    assessment = clue_data.get("acorn_assessment", {})
    radar = assessment.get("radar_data", {})
    if radar:
        scores = " | ".join(f"{k}={v}" for k, v in sorted(radar.items()))
        print(f"    ACOR评分: {scores}")

    # 触发事件
    trigger = clue_data.get("triggering_event", {})
    event_desc = trigger.get("event_description", "")
    if event_desc:
        print(f"    触发事件: {event_desc[:100]}{'...' if len(event_desc) > 100 else ''}")

    # 竞争分析
    competitors = clue_data.get("competitive_analysis", [])
    if competitors:
        comp_names = [c.get("competitor_name", "?") for c in competitors]
        print(f"    竞品: {', '.join(comp_names)}")

    # 创建时间
    if create_time:
        print(f"    创建时间: {create_time}")

    print()


# ===================== 核心：调用 QueryClueInfo =====================

def query_clue_info(
    api_host: str,
    api_key: str,
    start_time: str,
    end_time: str,
    max_results: int,
    next_token: Optional[str] = None,
) -> Dict[str, Any]:
    """调用 QueryClueInfo 接口查询单页商机信息

    Args:
        api_host:     API 基地址（不含路径和查询参数）
        api_key:      Bearer Token
        start_time:   起始时间
        end_time:     结束时间
        max_results:  每页最大返回条数
        next_token:   分页游标（首次不传）

    Returns:
        解析后的 Result 字典（已自动展开外层包装）
    """
    # URL 包含 Action 和 Version 查询参数
    url = f"{api_host}/?Action=QueryClueInfo&Version={API_VERSION}"

    payload: Dict[str, Any] = {
        "StartTime": start_time,
        "EndTime": end_time,
        "MaxResults": max_results,
    }
    if next_token:
        payload["NextToken"] = next_token

    print(f"[DEBUG] 调用 QueryClueInfo (GET): url={url}")
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
        raise SystemExit("QueryClueInfo 响应不是有效的 JSON")

    # 从 Result 包装层提取实际数据
    result = data.get("Result")
    if not isinstance(result, dict):
        print(f"[DEBUG] 响应 JSON 顶层 keys: {list(data.keys())}")
        print(f"[DEBUG] 完整响应: {json.dumps(data, ensure_ascii=False)[:2000]}")
        raise SystemExit("QueryClueInfo 响应不包含有效的 Result 字段")

    return result


# ===================== 分页循环查询 =====================

def query_all_clues(
    api_host: str,
    api_key: str,
    start_time: str,
    end_time: str,
    max_results: int,
) -> List[Dict[str, Any]]:
    """分页查询所有商机信息"""
    next_token = None
    total_count = 0
    page_num = 0
    all_clues: List[Dict[str, Any]] = []

    while True:
        page_num += 1

        try:
            result = query_clue_info(
                api_host, api_key,
                start_time, end_time, max_results, next_token
            )
        except SystemExit:
            raise
        except Exception as e:
            print(f"\n未预期的错误 (第 {page_num} 页): {e}")
            break

        # 处理当前页数据（JSON 响应中为 PascalCase）
        clues = result.get("ClueList") or []
        result_cnt = result.get("ResultCnt") or len(clues)
        total_count += len(clues)

        print(f"第 {page_num} 页：获取 {len(clues)} 条商机（本页 ResultCnt={result_cnt}，累计 {total_count} 条）")
        print()

        for clue in clues:
            clue_id = clue.get("ClueID", "") or "(无ID)"
            clue_text_raw = clue.get("ClueText", "")
            create_time = clue.get("CreateTime", "")

            # 解析 ClueText JSON
            clue_data = parse_clue_text(clue_text_raw)

            # 构建结构化信息
            clue_info = {
                "clue_id": clue_id,
                "clue_data": clue_data,
                "clue_text_raw": clue_text_raw,
                "create_time": create_time,
            }

            # 如果解析成功，提取关键字段便于统计
            if clue_data:
                briefing = clue_data.get("opportunity_briefing", {})
                company = clue_data.get("company_profile", {})
                clue_info["title"] = briefing.get("title", "")
                clue_info["priority"] = briefing.get("priority_level", "")
                clue_info["company_name"] = company.get("legal_name", "")
                clue_info["business_category"] = company.get("business_category", "")

            all_clues.append(clue_info)

            # 打印详细信息
            print_clue_detail(clue_id, clue_data, create_time)

        # 检查是否还有更多数据
        resp_next_token = result.get("NextToken")
        if not resp_next_token or len(clues) == 0:
            print(f"数据查询完成！共 {total_count} 条商机，{page_num} 页。")
            break

        # 设置下页游标
        next_token = resp_next_token

        # 请求间隔，避免限流
        time.sleep(REQUEST_INTERVAL)

    return all_clues


# ===================== 摘要输出 =====================

def print_summary(clues: List[Dict[str, Any]]):
    """打印商机摘要统计"""
    if not clues:
        print("未查询到任何商机信息。")
        return

    print("\n" + "=" * 80)
    print("商机信息摘要统计")
    print("=" * 80)
    print(f"总条数: {len(clues)}")

    # 唯一商机统计
    unique_ids = set(c.get("clue_id") for c in clues if c.get("clue_id"))
    print(f"唯一商机数: {len(unique_ids)}")

    # 按优先级统计
    priority_counts: Dict[str, int] = {}
    for c in clues:
        p = c.get("priority", "未知")
        if not p:
            p = "未知"
        priority_counts[p] = priority_counts.get(p, 0) + 1
    if priority_counts:
        print(f"\n优先级分布:")
        for p in sorted(priority_counts.keys()):
            print(f"  {p}: {priority_counts[p]} 条")

    # 按行业分类统计
    biz_counts: Dict[str, int] = {}
    for c in clues:
        biz = c.get("business_category", "未知")
        if not biz:
            biz = "未知"
        biz_counts[biz] = biz_counts.get(biz, 0) + 1
    if biz_counts:
        print(f"\n行业分布:")
        for biz, count in sorted(biz_counts.items(), key=lambda x: -x[1]):
            print(f"  {biz}: {count} 条")

    # 输出商机列表
    print(f"\n  {'ClueID':<16} {'优先级':<6} {'公司':<20} {'商机标题':<40}")
    print("  " + "-" * 84)
    for c in clues:
        cid = str(c.get("clue_id", "-"))[:14]
        priority = c.get("priority", "-") or "-"
        company = c.get("company_name", "-") or "-"
        title = c.get("title", "-") or "-"
        if isinstance(company, str) and len(company) > 18:
            company = company[:15] + "..."
        if isinstance(title, str) and len(title) > 38:
            title = title[:35] + "..."
        print(f"  {cid:<16} {priority:<6} {company:<20} {title:<40}")


# ===================== 主入口 =====================

if __name__ == "__main__":
    args = parse_args()

    print("=" * 80)
    print("市场洞察 Agent — QueryClueInfo 商机信息查询 (Bearer Token 模式)")
    print("=" * 80)
    print(f"时间范围: {args.start_time} ~ {args.end_time}")
    print(f"每页条数: {args.max_results}")
    print()

    try:
        api_host, api_key = _read_env()
        print(f"API 鉴权初始化完成 (Host: {api_host})")
        print()

        clues = query_all_clues(
            api_host, api_key,
            args.start_time, args.end_time, args.max_results
        )
        print_summary(clues)

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
