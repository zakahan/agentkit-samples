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
"""Example script: take a single snapshot from a TOS video using the Python SDK.

Reads configuration from environment variables and optional CLI args,
constructs a `process="video/snapshot,..."` rule string, and either:
  - saves the returned image locally (default), or
  - if `--saveas-bucket`/`--saveas-object` is provided, lets TOS persist
    the snapshot to the specified object and prints the JSON result.

Environment variables:
  - TOS_ACCESS_KEY        Access key ID (AK) or STS AccessKeyId
  - TOS_SECRET_KEY        Secret access key (SK) or STS SecretAccessKey
  - TOS_SECURITY_TOKEN    (optional) STS session token
  - TOS_ENDPOINT          TOS endpoint, e.g. https://tos-cn-beijing.volces.com
  - TOS_REGION            TOS region, e.g. cn-beijing
  - TOS_BUCKET            Bucket name that stores the video
  - TOS_OBJECT_KEY        Object key of the video file in the bucket

Optional environment variables for convenience:
  - TOS_SAVEAS_BUCKET     Default bucket for snapshot persistence
  - TOS_SAVEAS_OBJECT     Default object key for snapshot persistence
  - MAX_OBJECT_SIZE       Maximum allowed local snapshot size in bytes
                           (default: 262144). Only used for local save.
"""

import argparse
import json
import os
import sys
from typing import Any, Optional

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


def build_process_rule(args: argparse.Namespace) -> str:
    parts: list[str] = []
    if args.time is not None:
        parts.append(f"t_{args.time}")
    if args.width is not None:
        parts.append(f"w_{args.width}")
    if args.height is not None:
        parts.append(f"h_{args.height}")
    if args.mode:
        parts.append(f"m_{args.mode}")
    if args.output_format:
        parts.append(f"f_{args.output_format}")
    if args.auto_rotate:
        parts.append(f"ar_{args.auto_rotate}")
    if parts:
        return "video/snapshot," + ",".join(parts)
    return "video/snapshot"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Take a single video snapshot using the TOS Python SDK",
    )
    parser.add_argument("--time", type=int, help="Snapshot time in milliseconds")
    parser.add_argument("--width", type=int, help="Snapshot width in pixels")
    parser.add_argument("--height", type=int, help="Snapshot height in pixels")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["fast"],
        help="Snapshot mode: fast or precise (default precise)",
    )
    parser.add_argument(
        "--output-format",
        dest="output_format",
        choices=["jpg", "png"],
        help="Output image format",
    )
    parser.add_argument(
        "--auto-rotate",
        dest="auto_rotate",
        choices=["auto", "w", "h"],
        help="Auto rotate mode",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Local output file (default: snapshot_<time>ms.<fmt>)",
    )
    parser.add_argument(
        "--saveas-bucket",
        type=str,
        help="If set, persist snapshot to this bucket instead of saving locally",
    )
    parser.add_argument(
        "--saveas-object",
        type=str,
        help="If set, persist snapshot as this object key instead of saving locally",
    )
    args = parser.parse_args()

    client = create_client()
    bucket = get_env("TOS_BUCKET")
    key = get_env("TOS_OBJECT_KEY")

    process_value = build_process_rule(args)

    # Decide persistence mode
    saveas_bucket = args.saveas_bucket or os.getenv("TOS_SAVEAS_BUCKET")
    saveas_object = args.saveas_object or os.getenv("TOS_SAVEAS_OBJECT")
    persist_to_tos = bool(saveas_bucket or saveas_object)

    if persist_to_tos:
        # Persist snapshot in TOS and print JSON result
        save_bucket = saveas_bucket or bucket
        # If object not specified, build a simple default name
        if not saveas_object:
            time_part: Any = args.time if args.time is not None else "0"
            fmt = args.output_format or "jpg"
            saveas_object = f"snapshot_{time_part}ms.{fmt}"

        print(
            f"[INFO] Requesting snapshot for {bucket}/{key} -> {save_bucket}/{saveas_object}",
        )
        print(f"[INFO] process = {process_value}")

        try:
            output = client.get_object(
                bucket=bucket,
                key=key,
                process=process_value,
                save_bucket=save_bucket,
                save_object=saveas_object,
            )
            raw = output.read()
        except TosServerError as e:
            print(
                f"[ERROR] TOS server error: code={e.code}, status={e.status_code}, "
                f"request_id={e.request_id}, message={e.message}",
                file=sys.stderr,
            )
            sys.exit(1)
        except TosClientError as e:
            print(f"[ERROR] TOS client error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] Unexpected error: {exc}", file=sys.stderr)
            sys.exit(1)

        try:
            text = raw.decode("utf-8")
            data = json.loads(text)
        except Exception as exc:  # noqa: BLE001
            print("[ERROR] Failed to parse snapshot save result as JSON:", file=sys.stderr)
            print(exc, file=sys.stderr)
            print(raw[:200], file=sys.stderr)
            sys.exit(1)

        print("[OK] Snapshot saved to TOS:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    # Default: save snapshot locally via get_object_to_file
    time_part: Any = args.time if args.time is not None else "0"
    fmt = args.output_format or "jpg"
    output_path = args.output or f"snapshot_{time_part}ms.{fmt}"

    print(f"[INFO] Requesting snapshot for {bucket}/{key} -> {output_path}")
    print(f"[INFO] process = {process_value}")

    try:
        client.get_object_to_file(
            bucket=bucket,
            key=key,
            file_path=output_path,
            process=process_value,
        )
    except TosServerError as e:
        print(
            f"[ERROR] TOS server error: code={e.code}, status={e.status_code}, "
            f"request_id={e.request_id}, message={e.message}",
            file=sys.stderr,
        )
        sys.exit(1)
    except TosClientError as e:
        print(f"[ERROR] TOS client error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Basic protection against unexpectedly large local files
    max_object_size = int(os.getenv("MAX_OBJECT_SIZE", "262144"))  # bytes
    try:
        size = os.path.getsize(output_path)
    except OSError:
        size = -1

    if size != -1 and size > max_object_size:
        print(
            f"[ERROR] Snapshot size ({size} bytes) exceeds MAX_OBJECT_SIZE={max_object_size}. "
            "Deleting local file.",
            file=sys.stderr,
        )
        try:
            os.remove(output_path)
        except OSError:
            pass
        sys.exit(1)

    print(f"[OK] Snapshot saved to {output_path} ({size} bytes)")


if __name__ == "__main__":
    main()
