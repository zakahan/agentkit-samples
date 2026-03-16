---
name: byted-tos-video-process
version: 1.1.0
description: Uses Volcengine TOS SDK object processing (e.g., `video/info`, `video/snapshot`) to fetch video metadata and extract single or multiple frame snapshots from videos stored in Bytedance TOS. Use when the user needs video info/metadata, thumbnail or frame capture, snapshot extraction, or mentions TOS video processing.
homepage: https://www.volcengine.com/docs/6349/336154
---

# Bytedance TOS Video Process Skill

This skill provides essential video processing functions for video files stored in Bytedance's TOS (TeraObjectStore). It allows you to retrieve video metadata and perform single-frame or multi-frame snapshots directly using the Volcengine TOS SDK.

## Quick Start

### 1. Client Initialization

The following Python snippet demonstrates how to initialize the `TosClientV2` from environment variables.

```python
import os
import tos
from tos.exceptions import TosClientError, TosServerError

def create_client() -> tos.TosClientV2:
    """Initializes a TosClientV2 using AK/SK (and optional STS token) from environment variables."""
    try:
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        endpoint = os.getenv('TOS_ENDPOINT')
        region = os.getenv('TOS_REGION')
        security_token = os.getenv('TOS_SECURITY_TOKEN') # Optional, for STS

        if not all([ak, sk, endpoint, region]):
            raise ValueError("Required environment variables are missing (AK, SK, Endpoint, Region).")

        return tos.TosClientV2(
            ak=ak,
            sk=sk,
            endpoint=endpoint,
            region=region,
            security_token=security_token,
        )
    except (ValueError, ImportError) as e:
        print(f"Error initializing client: {e}")
        # Handle initialization failure
        return None

# Create the client
client = create_client()
```

### 2. Basic Workflow

```python
# (Assumes 'client' is initialized and 'bucket_name', 'object_key' are set)

# 1. Get Video Info
try:
    response = client.get_object(bucket_name, object_key, process="video/info")
    info_data = response.read()
    print("Video Info:", info_data.decode('utf-8'))
except TosServerError as e:
    print(f"Error getting video info: {e}")


# 2. Take a Single Snapshot and save locally
try:
    client.get_object_to_file(
        bucket_name,
        object_key,
        "snapshot_1000ms.jpg",
        process="video/snapshot,t_1000,f_jpg,w_720"
    )
    print("Snapshot saved to snapshot_1000ms.jpg")
except TosServerError as e:
    print(f"Error taking snapshot: {e}")

# 3. Take a Snapshot and save back to TOS
try:
    response = client.get_object(
        bucket_name,
        object_key,
        process="video/snapshot,t_5000,f_jpg",
        save_bucket=bucket_name,
        save_object="processed/snapshot_5000ms.jpg"
    )
    save_result = response.read()
    print("Snapshot saved to TOS:", save_result.decode('utf-8'))
except TosServerError as e:
    print(f"Error saving snapshot to TOS: {e}")
```

## Core Operations

All video processing is achieved via the `process` parameter in the `get_object` or `get_object_to_file` SDK methods.

### 1. Get Video Info (`videoInfo`)

Retrieves metadata of a video file, such as resolution, duration, and format.

**SDK Method**: `client.get_object(..., process="video/info")`

```python
# 'client', 'bucket_name', and 'object_key' must be defined
try:
    response = client.get_object(bucket_name, object_key, process="video/info")
    # The response body is a JSON string
    video_metadata = response.read().decode('utf-8')
    print(video_metadata)
except TosServerError as e:
    print(f"Server Error: {e.code} - {e.message}")
```

### 2. Take a Single Snapshot (`videoSnapshot`)

Captures a single frame from a video. It supports various parameters for customization and can either return the image data or save the result directly back to TOS.

**SDK Method**: `client.get_object_to_file(..., process="video/snapshot,...")` for local save.
**SDK Method**: `client.get_object(..., process="video/snapshot,...", save_bucket=..., save_object=...)` for saving to TOS.

```python
# Example: Take a snapshot at 10 seconds, resize to 720p width, and save locally
try:
    client.get_object_to_file(
        bucket_name,
        object_key,
        file_path="local_snapshot.jpg",
        process="video/snapshot,t_10000,w_720,f_jpg"
    )
    print("Snapshot saved successfully to local_snapshot.jpg")
except (TosClientError, TosServerError) as e:
    print(f"An error occurred: {e}")
```

### 3. Take Multiple Snapshots (`videoSnapshots`)

This is a client-side orchestration pattern. You loop through a series of timestamps and make multiple calls to the `videoSnapshot` operation. The `scripts/video_snapshots.py` provides a reference implementation for parallel execution.

```python
# (Assumes 'client', 'bucket_name', 'object_key' are set)
timestamps = [1000, 5000, 10000]  # In milliseconds

for i, ts in enumerate(timestamps):
    output_filename = f'snapshot_{i+1}_at_{ts}ms.jpg'
    process_rule = f"video/snapshot,t_{ts},w_720,f_jpg"
    try:
        client.get_object_to_file(
            bucket_name,
            object_key,
            output_filename,
            process=process_rule
        )
        print(f"Saved snapshot to {output_filename}")
    except (TosClientError, TosServerError) as e:
        print(f"Failed for timestamp {ts}: {e}")
```

## Authorization

Authentication is handled directly by the `tos.TosClientV2` constructor. Provide credentials via environment variables.

### Required Environment Variables
- `TOS_ACCESS_KEY`: Your Access Key ID.
- `TOS_SECRET_KEY`: Your Secret Access Key.
- `TOS_ENDPOINT`: The endpoint for the TOS service (e.g., `https://tos-cn-beijing.volces.com`).
- `TOS_REGION`: The region for the TOS service (e.g., `cn-beijing`).

### Optional for STS
- `TOS_SECURITY_TOKEN`: If using a temporary token (STS), provide the session token here. The client will automatically use it if present.

## Best Practices
- **Error Handling**: Always wrap SDK calls in `try...except` blocks to handle `TosClientError` and `TosServerError`.
- **Parameter Validation**: Validate parameters like `time`, `width`, and `height` on the client side before making an API call to prevent unnecessary errors.
- **Batch Operations**: For `videoSnapshots`, use a thread pool (like `ThreadPoolExecutor`) to perform multiple snapshot requests in parallel for better performance. See `scripts/video_snapshots.py` for an example.
- **Credentials Management**: Use a secure method to manage and refresh credentials, especially when using short-lived STS tokens.

## Additional Resources

- For detailed parameters of each operation, see [REFERENCE.md](REFERENCE.md).
- For common end-to-end examples, see [WORKFLOWS.md](WORKFLOWS.md).
- For executable Python examples, see the `scripts/` directory.
