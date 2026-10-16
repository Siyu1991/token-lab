# Token Lab：Token 可视化 + API 调用成本计算器

知乎专栏「代码与模型之间」第 1 期《Token 与账单》的配套小项目。在浏览器里输入一段文字，看它被切成哪些 token（彩色分块，可切换显示 token id），再按自己填的单价估算 API 调用成本。

- 不运行模型，不需要 API Key，不需要 GPU。
- 后端：Python + FastAPI + [tiktoken](https://github.com/openai/tiktoken)（提供 `o200k_base` / `cl100k_base` 两种编码）；前端：单个 HTML 文件，无构建步骤。
- 单次请求最多处理 20000 个字符。
- 计数基于 OpenAI 的编码。Claude、Gemini、Qwen 等使用各自的分词器，这里的数字只能当近似值，精确用量以各家 API 返回的 usage 字段为准。

## 本地运行

需要 Python 3.9+。

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8800
```

浏览器打开 http://127.0.0.1:8800 。

接口：

```bash
curl http://127.0.0.1:8800/healthz
curl -X POST http://127.0.0.1:8800/api/tokenize \
  -H 'Content-Type: application/json' \
  -d '{"text":"你好，大模型！Hello","encoding":"o200k_base"}'
```

### 词表缓存

tiktoken 第一次使用某个编码时会从 `openaipublic.blob.core.windows.net` 下载词表。服务器访问不畅时，可以在能联网的机器上预先下载：

```bash
export TIKTOKEN_CACHE_DIR=./tiktoken_cache
.venv/bin/python -c "import tiktoken; [tiktoken.get_encoding(n) for n in ('o200k_base','cl100k_base')]"
```

把 `tiktoken_cache/` 目录拷到服务器，服务进程设置同样的 `TIKTOKEN_CACHE_DIR` 即可。

## 部署到 Linux 服务器（systemd + nginx）

以 Alibaba Cloud Linux 3 为例（其他发行版换成对应的包管理器）：

```bash
dnf install -y python3.11 nginx
mkdir -p /opt/tokenlab            # 拷入 app.py、static/、requirements.txt、tiktoken_cache/
cd /opt/tokenlab
python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp deploy/tokenlab.service /etc/systemd/system/
cp deploy/nginx-tokenlab.conf /etc/nginx/conf.d/tokenlab.conf
systemctl daemon-reload && systemctl enable --now tokenlab
nginx -t && systemctl enable --now nginx
```

- uvicorn 只监听 `127.0.0.1:8800`，对外由 nginx 走 80 端口。
- 服务以 `nobody` 用户运行，`tiktoken_cache/` 需要提前下载好并对其可读。
- 云服务器需要在安全组入方向放行 TCP 80；若启用了 firewalld，再执行 `firewall-cmd --add-service=http --permanent && firewall-cmd --reload`。

## 许可

MIT，见 [LICENSE](LICENSE)。
