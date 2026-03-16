# Bytedance TOS Video Process Skill

This skill enables an agent to perform basic video processing tasks on files stored in Bytedance's TOS (TeraObjectStore) by directly using the Volcengine TOS Python SDK.

## Overview

The skill allows an agent to:
1.  **Retrieve Video Information**: Get metadata like resolution, duration, codec, etc.
2.  **Take Snapshots**: Capture single or multiple frames from a video.
3.  **Save Results**: Persist snapshot results back into a TOS bucket or save them locally.

It is designed to be a self-contained skill that interacts directly with the TOS API via its official Python SDK.

## Skill Structure

```
byted-tos-video-process/
├── SKILL.md              # Main skill file with quick start and core operations
├── README.md             # This file: detailed setup and environment guide
├── REFERENCE.md          # Complete parameter reference for each operation
├── WORKFLOWS.md          # Common end-to-end workflow examples
├── scripts/              # Executable Python scripts demonstrating each core capability
│   ├── video_info.py     # Script to get video information
│   ├── video_snapshot.py # Script for single-frame snapshots
│   └── video_snapshots.py# Script for multi-frame snapshots (batch processing)
├── .gitignore            # Excludes temporary files from version control
└── requirements.txt      # Python dependencies for the scripts
```

## Setup and Configuration

### Requirements
- Python 3.7+
- `tos` Python SDK

### Installation

Install the necessary Python library:
```bash
pip install tos
```

### Environment Variables

All scripts and examples rely on environment variables to avoid hardcoding sensitive information.

| Variable | Description | Example |
|---|---|--- |
| `TOS_ACCESS_KEY` | Your Access Key ID for TOS authentication. | `AKL...` |
| `TOS_SECRET_KEY` | Your Secret Access Key for TOS authentication. | `your-secret-key` |
| `TOS_SECURITY_TOKEN` | (Optional) The session token for temporary STS credentials. | `STS...` |
| `TOS_ENDPOINT` | The full URL of the TOS service endpoint. | `https://tos-cn-beijing.volces.com` |
| `TOS_REGION` | The region of the TOS service. | `cn-beijing` |
| `TOS_BUCKET` | The name of the bucket where the target video is stored. | `my-video-assets` |
| `TOS_OBJECT_KEY` | The full path (key) of the video file within the bucket. | `input/demos/wildlife.mp4` |
| `TOS_SAVEAS_BUCKET` | (Optional) The bucket to save snapshot results into. If not set, `TOS_BUCKET` is used. | `my-video-snapshots` |
| `TOS_SAVEAS_OBJECT_PREFIX` | (Optional) A prefix for the object key when saving snapshots. | `output/wildlife-snapshots/` |

**Security Note**: For production environments, it is highly recommended to use short-lived STS (Security Token Service) credentials. The SDK will automatically use `TOS_SECURITY_TOKEN` if it is present.

## Quick Start

### 1. Set Environment Variables

```bash
# --- Required ---
export TOS_ACCESS_KEY="YOUR_AK"
export TOS_SECRET_KEY="YOUR_SK"
export TOS_ENDPOINT="https://tos-cn-beijing.volces.com"
export TOS_REGION="cn-beijing"
export TOS_BUCKET="your-video-bucket"
export TOS_OBJECT_KEY="path/to/your/video.mp4"

# --- Optional (for STS credentials) ---
export TOS_SECURITY_TOKEN="YOUR_STS_TOKEN"

# --- Optional (for saving snapshots to TOS) ---
export TOS_SAVEAS_BUCKET="your-snapshot-bucket"
export TOS_SAVEAS_OBJECT_PREFIX="snapshots/demo-"
```

### 2. Run Example Scripts

The `scripts/` directory contains ready-to-run examples that use the SDK.

**Get Video Info:**
```bash
python3 scripts/video_info.py
```

**Take a Single Snapshot and Save Locally:**
This captures a frame at 5 seconds and saves it as `snapshot_5000ms.jpg`.
```bash
python3 scripts/video_snapshot.py --time 5000 --output local_frame.jpg
```

**Take Multiple Snapshots and Save to TOS:**
This captures frames at 1, 3, and 5 seconds, and saves them to the bucket specified by `TOS_SAVEAS_BUCKET`.
```bash
python3 scripts/video_snapshots.py --timestamps 1000 3000 5000 --save-to-tos
```

## Note on Large Files

The TOS `get_object` API (which this skill uses for snapshots) streams data. The provided example scripts include a `MAX_OBJECT_SIZE` environment variable (defaulting to 256KB) as a safeguard to prevent accidentally downloading excessively large snapshot files to the local disk. This check does not apply when snapshots are saved directly within TOS.
