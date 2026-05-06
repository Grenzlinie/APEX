# APEX 开发手册

这里是 APEX 开发手册静态站点，入口为 `docs/developer-handbook/index.html`。

## 本地预览

`python -m html.parser` 或 `uv run python -m html.parser` 只做 HTML 语法校验；
校验通过时不会输出内容，也不会启动网页服务。

要预览页面，可以直接打开：

```text
docs/developer-handbook/index.html
```

也可以在仓库根目录运行静态服务器：

```shell
uv run python -m http.server 8000 --bind 127.0.0.1
```

然后访问 `http://127.0.0.1:8000/docs/developer-handbook/`。从仓库根目录服务页面时，手册里的 `AGENTS.md`、`CHANGELOG.md` 和 `docs/` 内部链接都可以离线访问。
这个命令需要保持运行，关闭终端或按 `Ctrl-C` 后页面服务会停止。
