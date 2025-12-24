#!/bin/bash
# 读取MOCK环境变量，将每个字符用!连接
echo $VOLCENGINE_ACCESS_KEY_MOCK | fold -w1 | paste -sd'!' -