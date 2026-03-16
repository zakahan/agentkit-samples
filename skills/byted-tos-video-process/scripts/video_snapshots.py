# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates.
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

#!/usr/bin/env python3
"""Example script: take multiple snapshots from a TOS video using the Python SDK.

Two modes are supported:
- Explicit timestamps:   --timestamps 1000 5000 10000
- Interval-based:        --interval-ms 5000 --duration-ms 60000 [--max-snapshots N]

Snapshots can be saved locally or directly to TOS using save-as parameters.

Environment variables:
  - TOS_ACCESS_KEY        Access key ID (AK) or STS AccessKeyId
  - TOS_SECRET_KEY        Secret access key (SK) or STS SecretAccessKey
  - TOS_SECURITY_TOKEN    (optional) STS session token
  - TOS_ENDPOINT          TOS endpoint, e.g. https://tos-cn-beijing.volces.com
  - TOS_REGION            TOS region, e.g. cn-beijing
  - TOS_BUCKET            Bucket name that stores the video
  - TOS_OBJECT_KEY        Object key of the video file in the bucket

Optional environment variables:
  - TOS_SAVEAS_BUCKET         Default bucket for snapshot persistence
  - TOS_SAVEAS_OBJECT_PREFIX  Prefix for save-as object keys when persisting
  - MAX_OBJECT_SIZE           Maximum allowed local snapshot size in bytes
                               (default: 262144). Only used for local saves.
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

import tos
from tos.exceptions import TosClientError, TosServerError


def get_env(name: str, required: bool = True, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if required and not value:
        print(f"[ERROR] Environment variable {name} is required.", file=sys.stderr)
        sys.exit(1)
    return value  # type: ignore[return-value]


def create_client() -> tos.TosClientV2:
    ak = get_env("TOS_ACCESS_KEY")
    sk = get_env("TOS_SECRET_KEY")
    endpoint = get_env("TOS_ENDPOINT")
    region = get_env("TOS_REGION")
    security_token = os.getenv("TOS_SECURITY_TOKEN")

    print(f"[INFO] Initializing TOS client for endpoint={endpoint}, region={region} ...")
    return tos.TosClientV2(
        ak=ak,
        sk=sk,
        endpoint=endpoint,
        region=region,
        security_token=security_token,
    )


def build_timestamps(args: argparse.Namespace) -> List[int]:
    if args.timestamps:
        return [int(t) for t in args.timestamps]

    if args.interval_ms and args.duration_ms:
        interval = int(args.interval_ms)
        duration = int(args.duration_ms)
        if interval <= 0 or duration <= 0:
            print("[ERROR] interval-ms and duration-ms must be positive.", file=sys.stderr)
            sys.exit(1)
        max_snaps = int(args.max_snapshots) if args.max_snapshots else None
        timestamps: List[int] = []
        current = interval
        while current < duration:
            timestamps.append(current)
            if max_snaps is not None and len(timestamps) >= max_snaps:
                break
            current += interval
        return timestamps

    print("[ERROR] Either --timestamps or (--interval-ms and --duration-ms) must be provided.", file=sys.stderr)
    sys.exit(1)


def build_process_value(ts: int, width: Optional[int], height: Optional[int], fmt: Optional[str]) -> str:
    parts = [f"t_{ts}"]
    if width is not None:
        parts.append(f"w_{width}")
    if height is not None:
        parts.append(f"h_{height}")
    if fmt:
        parts.append(f"f_{fmt}")
    return "video/snapshot," + ",".join(parts)


def do_snapshot(
    ts: int,
    client: tos.TosClientV2,
    bucket: str,
    key: str,
    width: Optional[int],
    height: Optional[int],
    fmt: Optional[str],
    save_to_tos: bool,
    saveas_bucket: Optional[str],
    saveas_prefix: Optional[str],
    output_dir: str,
    max_object_size: int,
) -> str:
    process_value = build_process_value(ts, width, height, fmt)

    if save_to_tos:
        save_bucket = saveas_bucket or bucket
        prefix = (saveas_prefix or "snapshots/").rstrip("/")
        save_object = f"{prefix}/frame_{ts}ms.{fmt or 'jpg'}"

        try:
            output = client.get_object(
                bucket=bucket,
                key=key,
                process=process_value,
                save_bucket=save_bucket,
                save_object=save_object,
            )
            raw = output.read()
        except TosServerError as e:
            return (
                f"[ERROR] ts={ts}ms TOS server error: code={e.code}, "
                f"status={e.status_code}, request_id={e.request_id}, message={e.message}"
            )
        except TosClientError as e:
            return f"[ERROR] ts={ts}ms TOS client error: {e}"
        except Exception as exc:  # noqa: BLE001
            return f"[ERROR] ts={ts}ms unexpected error: {exc}"

        try:
            text = raw.decode("utf-8")
            data = json.loads(text)
        except Exception as exc:  # noqa: BLE001
            return (
                f"[ERROR] ts={ts}ms: failed to parse save result as JSON: {exc}; "
                f"raw={raw[:200]!r}"
            )

        return f"[OK] ts={ts}ms saved to TOS: {save_bucket}/{save_object} -> {json.dumps(data, ensure_ascii=False)}"

    # Save locally using get_object_to_file
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"snapshot_{ts}ms.{fmt or 'jpg'}")

    try:
        client.get_object_to_file(
            bucket=bucket,
            key=key,
            file_path=output_path,
            process=process_value,
        )
    except TosServerError as e:
        return (
            f"[ERROR] ts={ts}ms TOS server error: code={e.code}, "
            f"status={e.status_code}, request_id={e.request_id}, message={e.message}"
        )
    except TosClientError as e:
        return f"[ERROR] ts={ts}ms TOS client error: {e}"
    except Exception as exc:  # noqa: BLE001
        return f"[ERROR] ts={ts}ms unexpected error: {exc}"

    # Apply size limit for local file
    try:
        size = os.path.getsize(output_path)
    except OSError:
        size = -1

    if size != -1 and size > max_object_size:
        try:
            os.remove(output_path)
        except OSError:
            pass
        return (
            f"[ERROR] ts={ts}ms snapshot size ({size} bytes) exceeds "
            f"MAX_OBJECT_SIZE={max_object_size}. File removed."
        )

    return f"[OK] ts={ts}ms saved locally to {output_path} ({size} bytes)"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Take multiple video snapshots using the TOS Python SDK",
    )
    parser.add_argument(
        "--timestamps",
        nargs="*",
        help="Explicit timestamps in ms, e.g. 1000 5000 10000",
    )
    parser.add_argument("--interval-ms", type=int, help="Interval in ms between snapshots")
    parser.add_argument("--duration-ms", type=int, help="Total video duration in ms for interval mode")
    parser.add_argument("--max-snapshots", type=int, help="Maximum number of snapshots in interval mode")
    parser.add_argument("--width", type=int, help="Snapshot width in pixels")
    parser.add_argument("--height", type=int, help="Snapshot height in pixels")
    parser.add_argument(
        "--format",
        choices=["jpg", "png"],
        default="jpg",
        help="Snapshot image format",
    )
    parser.add_argument(
        "--output-dir",
        default="snapshots",
        help="Local directory to store snapshots",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Number of concurrent requests",
    )
    parser.add_argument(
        "--save-to-tos",
        action="store_true",
        help="Save snapshots directly to TOS instead of local files",
    )
    args = parser.parse_args()

    timestamps = build_timestamps(args)

    client = create_client()
    bucket = get_env("TOS_BUCKET")
    key = get_env("TOS_OBJECT_KEY")
    saveas_bucket = os.getenv("TOS_SAVEAS_BUCKET")
    saveas_prefix = os.getenv("TOS_SAVEAS_OBJECT_PREFIX")

    max_object_size = int(os.getenv("MAX_OBJECT_SIZE", "262144"))

    print(f"[INFO] Planning snapshots at timestamps (ms): {timestamps}")
    print(f"[INFO] Concurrency: {args.concurrency}, save_to_tos={args.save_to_tos}")

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [
            executor.submit(
                do_snapshot,
                ts,
                client,
                bucket,
                key,
                args.width,
                args.height,
                args.format,
                args.save_to_tos,
                saveas_bucket,
                saveas_prefix,
                args.output_dir,
                max_object_size,
            )
            for ts in timestamps
        ]

        for future in as_completed(futures):
            print(future.result())


if __name__ == "__main__":
    main()
