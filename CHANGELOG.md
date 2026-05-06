# 更新日志

APEX 中所有用户可见的重要变化都应记录在这里。

本文件按 `Added`、`Changed`、`Deprecated`、`Removed`、`Fixed` 和
`Security` 分类维护。条目应保持小范围；如果有对应 commit 或 PR，应在后续补充链接。

## Unreleased

### Added

- 新增仓库开发契约和配套开发文档，用于 APEX 2.0 规划和新贡献者上手。
- 新增可静态部署的开发手册 `docs/developer-handbook/`，帮助开发者按需求快速定位代码路径、测试位置和修改检查项。

### Changed

- 开发分支切换到 `exp-2.0.0`，包开发版本为 `2.0.0.dev0`，目标发布版本为 `2.0.0`。
- 移除 CI 中已无实际用途的 `SKIP_UT_WITH_DFLOW` 和 `DFLOW_DEBUG` 环境变量。
- 将 CI 测试入口从 `coverage run -m unittest` 切换为 pytest-cov，并明确新增测试应使用 pytest 风格。

### Deprecated

- 明确只有代码或文档显式标记的内容才视为 deprecated；陈旧示例、镜像或教程文件在使用前必须重新验证。
