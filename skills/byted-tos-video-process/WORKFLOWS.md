# Bytedance TOS Video Process Workflows

This document illustrates common workflows for using the TOS Video Process skill with the Volcengine TOS Python SDK. These examples demonstrate how to combine environment setup, SDK calls, and result handling for practical use cases.

## Table of Contents
- [Workflow 1: Get Video Information](#workflow-1-get-video-information)
- [Workflow 2: Take a Single Snapshot and Save Locally](#workflow-2-take-a-single-snapshot-and-save-locally)
- [Workflow 3: Take a Single Snapshot and Save to TOS](#workflow-3-take-a-single-snapshot-and-save-to-tos)
- [Workflow 4: Batch Snapshotting with a Time Interval](#workflow-4-batch-snapshotting-with-a-time-interval)
- [Workflow 5: Handling Errors](#workflow-5-handling-errors)

---

### Prerequisite: Client Initialization

All workflows assume you have a `tos.TosClientV2` instance initialized as shown below. See `README.md` for details on environment variables.

```python
import os
import tos
from tos.exceptions import TosClientError, TosServerError

def create_client() -> tos.TosClientV2:
    """Initializes a TosClientV2 from environment variables."""
    ak = os.getenv('TOS_ACCESS_KEY')
    sk = os.getenv('TOS_SECRET_KEY')
    endpoint = os.getenv('TOS_ENDPOINT')
    region = os.getenv('TOS_REGION')
    security_token = os.getenv('TOS_SECURITY_TOKEN')

    if not all([ak, sk, endpoint, region]):
        raise ValueError("Missing required environment variables for TOS client.")

    return tos.TosClientV2(
        ak=ak,
        sk=sk,
        endpoint=endpoint,
        region=region,
        security_token=security_token,
    )

client = create_client()
bucket_name = os.getenv("TOS_BUCKET")
object_key = os.getenv("TOS_OBJECT_KEY")
```

---

### Workflow 1: Get Video Information

**Goal:** Retrieve the format and stream information for a video file.

**Steps:**
1.  Initialize the `TosClientV2` client.
2.  Call `client.get_object()` with `process="video/info"`.
3.  Read the response body and parse it as JSON.
4.  Extract the desired information.

**Python Example (`scripts/video_info.py`):**
```python
import json

# Assumes 'client', 'bucket_name', 'object_key' are initialized
try:
    response = client.get_object(
        bucket=bucket_name,
        key=object_key,
        process="video/info"
    )
    raw_data = response.read()
    video_info = json.loads(raw_data.decode('utf-8'))

    duration = video_info.get("Format", {}).get("Duration")
    width = video_info.get("VideoStream", {}).get("Width")
    height = video_info.get("VideoStream", {}).get("Height")

    print("Successfully retrieved video info:")
    print(f"  - Duration: {duration} seconds")
    print(f"  - Dimensions: {width}x{height}")
    print("\nFull details:")
    print(json.dumps(video_info, indent=2))

except TosServerError as e:
    print(f"Server Error: {e.code} - {e.message}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

---

### Workflow 2: Take a Single Snapshot and Save Locally

**Goal:** Capture a single frame at a specific timestamp and save it as a local image file.

**Steps:**
1.  Define the snapshot parameters (time, dimensions, format).
2.  Construct the `process` string (e.g., `"video/snapshot,t_10000,w_1280,f_jpg"`).
3.  Call `client.get_object_to_file()` with the `process` string and a local file path.

**Python Example (`scripts/video_snapshot.py`):**
```python
# Assumes 'client', 'bucket_name', 'object_key' are initialized
time_ms = 10000  # Snapshot at 10 seconds
output_filename = f"snapshot_{time_ms}ms.jpg"

process_rule = f"video/snapshot,t_{time_ms},w_1280,f_jpg"

print(f"Requesting snapshot at {time_ms}ms...")
try:
    client.get_object_to_file(
        bucket=bucket_name,
        key=object_key,
        file_path=output_filename,
        process=process_rule
    )
    print(f"Snapshot successfully saved to {output_filename}")
except (TosClientError, TosServerError) as e:
    print(f"An error occurred: {e}")
```

---

### Workflow 3: Take a Single Snapshot and Save to TOS

**Goal:** Capture a single frame and have the TOS server save it directly to another object in the same or a different bucket.

**Steps:**
1.  Define the snapshot and save-as parameters.
2.  Construct the `process` string.
3.  Call `client.get_object()`, providing the `process`, `save_bucket`, and `save_object` arguments.
4.  Parse the JSON response to confirm the save location.

**Python Example:**
```python
# Assumes 'client', 'bucket_name', 'object_key' are initialized
import json

time_ms = 15000
saveas_bucket = os.getenv("TOS_SAVEAS_BUCKET", bucket_name)
saveas_prefix = os.getenv("TOS_SAVEAS_OBJECT_PREFIX", "snapshots/")
saveas_object_key = f"{saveas_prefix}frame_{time_ms}ms.jpg"
process_rule = f"video/snapshot,t_{time_ms}"

try:
    response = client.get_object(
        bucket=bucket_name,
        key=object_key,
        process=process_rule,
        save_bucket=saveas_bucket,
        save_object=saveas_object_key
    )
    result = json.loads(response.read().decode('utf-8'))
    print("Snapshot successfully saved to TOS:")
    print(json.dumps(result, indent=2))
except (TosClientError, TosServerError) as e:
    print(f"An error occurred: {e}")
```

---

### Workflow 4: Batch Snapshotting with a Time Interval

**Goal:** Generate multiple snapshots every `N` seconds of a video and save them all to TOS.

**Steps:**
1.  **Get Video Duration**: Use Workflow 1 to get the video's total duration.
2.  **Generate Timestamps**: Calculate a list of timestamps based on a desired interval (e.g., every 30 seconds).
3.  **Loop and Request**: Iterate through the timestamps and execute the "Save to TOS" workflow for each one, generating a unique `save_object` name for each frame. This is best done concurrently using a thread pool.

**Python Example (`scripts/video_snapshots.py` logic):**
```python
# (This is a simplified logic; see the script for a complete implementation)
# 1. Get video duration first (implement Workflow 1)
# video_duration_seconds = 125

interval_seconds = 30
timestamps_ms = [i * 1000 for i in range(interval_seconds, int(video_duration_seconds), interval_seconds)]
# -> [30000, 60000, 90000, 120000]

# 3. Loop and request
for ts in timestamps_ms:
    saveas_object = f"{saveas_prefix}interval_frame_{ts}ms.jpg"
    process_rule = f"video/snapshot,t_{ts}"
    try:
        client.get_object(
            bucket=bucket_name,
            key=object_key,
            process=process_rule,
            save_bucket=saveas_bucket,
            save_object=saveas_object
        )
        print(f"Successfully triggered save for timestamp {ts}ms to {saveas_bucket}/{saveas_object}")
    except (TosClientError, TosServerError) as e:
        print(f"Failed to save snapshot for timestamp {ts}ms: {e}")
```

---

### Workflow 5: Handling Errors

**Goal:** Gracefully handle common errors like invalid credentials, missing files, or server-side issues when using the SDK.

**Error Handling Strategy:**
- Wrap all SDK calls in `try...except` blocks.
- Catch `tos.exceptions.TosServerError` for API errors returned by the TOS service. The exception object contains `.code`, `.status_code`, `.message`, and `.request_id`.
- Catch `tos.exceptions.TosClientError` for client-side issues like network problems or invalid input.
- Check for missing environment variables before initializing the client.

**Python Example:**
```python
# (Assumes 'client' is initialized)
try:
    # An example call that might fail
    response = client.get_object(
        bucket="non-existent-bucket",
        key="non-existent-key",
        process="video/info"
    )
    # ... process successful response
except TosServerError as e:
    print(f"TOS Server Error occurred:")
    print(f"  - Status Code: {e.status_code}")
    print(f"  - Error Code: {e.code}")
    print(f"  - Message: {e.message}")
    print(f"  - Request ID: {e.request_id}")
except TosClientError as e:
    print(f"TOS Client Error: {e.message}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```
