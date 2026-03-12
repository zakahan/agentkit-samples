---
name: byted-text-to-speech
description: 将文本合成为语音（TTS）。使用火山引擎豆包语音合成 API，支持流式/一次性合成。当用户需要把文字转成语音、生成朗读音频、或需要 TTS 能力时使用本技能。
license: Complete terms in LICENSE
---

# Byted-Text-to-Speech Skill

基于[火山引擎豆包语音合成](https://www.volcengine.com/docs/6561/1598757)（HTTP Chunked/SSE 单向流式-V3）将文本转为语音并保存为音频文件。

## 适用场景

1. 用户要求把一段文字转成语音/朗读
2. 用户需要生成配音、旁白或播报音频
3. 用户提到「文字转语音」「TTS」「语音合成」

## 使用步骤

1. 准备要合成的文本 `text`（中文或英文，避免特殊字符）。
2. 运行脚本前先 `cd` 到本技能目录：`skills/byted-text-to-speech`。
3. 执行：`python scripts/text_to_speech.py --text "要合成的文字" [选项]`。
4. 根据返回的 `local_path` 或 `url` 将生成的音频提供给用户。

## 环境变量与鉴权（新版控制台）

鉴权采用**新版控制台方案**，详见：[API Key 管理](https://console.volcengine.com/speech/new/setting/apikeys)。

使用前需配置：

- **必填**：`MODEL_SPEECH_API_KEY` — 在豆包语音新版控制台创建/获取的 API Key。
- **可选**：`MODEL_SPEECH_API_BASE`（API 域名，默认 `openspeech.bytedance.com`）、`MODEL_SPEECH_TTS_RESOURCE_ID`（资源 ID，默认 `seed-tts-2.0`）。

控制台与开通说明见：[豆包语音-产品简介](https://www.volcengine.com/docs/6561/1257543)。

## 脚本参数

| 参数 | 简写 | 必填 | 说明 |
|------|------|------|------|
| `--text` | `-t` | 是 | 要合成的文本内容 |
| `--output` | `-o` | 否 | 输出音频文件路径（默认自动生成） |
| `--speaker` | `-s` | 否 | 发音人，默认 `zh_female_vv_uranus_bigtts`，[音色列表](https://www.volcengine.com/docs/6561/1257544) |
| `--format` | | 否 | 音频格式：`mp3`（默认）、`pcm`、`ogg_opus` |
| `--sample-rate` | | 否 | 采样率，如 16000、24000（默认 24000） |
| `--speech-rate` | | 否 | 语速 [-50, 100]，100 代表 2.0 倍速，-50 代表 0.5 倍速，默认 0 |
| `--pitch-rate` | | 否 | 音调 [-12, 12]，默认 0 |
| `--loudness-rate` | | 否 | 音量 [-50, 100]，100 代表 2.0 倍音量，-50 代表 0.5 倍音量，默认 0 |
| `--bit-rate` | | 否 | 比特率，对 mp3 和 ogg_opus 格式生效（如 64000、128000），默认 64000 |
| `--filter-markdown` | | 否 | 过滤 markdown 语法（如 `**你好**` 读为"你好"），默认关闭 |
| `--enable-latex` | | 否 | 启用 LaTeX 公式播报（使用 latex\_parser v2，自动开启 markdown 过滤），默认关闭 |

## 返回值说明

脚本输出 JSON，包含：

- `status`: `"success"` 或 `"error"`
- `local_path`: 本地音频文件路径
- `format`: 音频格式
- `error`: 失败时的错误信息

请将 `local_path` 或可访问的音频 URL 返回给用户，便于播放或下载。

## 错误处理

- 若报错 `PermissionError: MODEL_SPEECH_API_KEY ... 需在环境变量中配置`：提示用户在 [API Key 管理](https://console.volcengine.com/speech/new/setting/apikeys) 获取并配置 `MODEL_SPEECH_API_KEY`，写入 workspace 下的环境变量文件后重试。
- 若返回 4xx/5xx 或业务错误码：根据错误信息提示用户检查文本内容、发音人 ID 及账号是否已开通豆包语音服务。

## 参考文档

- [API Key 管理](https://console.volcengine.com/speech/new/setting/apikeys) — 鉴权与开通
- [HTTP Chunked/SSE 单向流式-V3](https://www.volcengine.com/docs/6561/1598757)
- [音色列表](https://www.volcengine.com/docs/6561/1257544)
- [SSML 标记语言](https://www.volcengine.com/docs/6561/1330194)（高级用法）

## 示例

```bash
# 基本用法
python scripts/text_to_speech.py -t "欢迎使用火山引擎语音合成服务。"

# 指定发音人与输出格式
python scripts/text_to_speech.py -t "这是一段测试语音。" -s zh_female_vv_uranus_bigtts -o output.mp3 --format mp3

# 指定语速与采样率
python scripts/text_to_speech.py -t "语速和音调可调。" --speech-rate 10 --sample-rate 16000
```
