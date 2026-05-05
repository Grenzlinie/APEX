# APEX 开发契约

本文档是 Codex、Claude Code 和人类开发者在当前 checkout 中协作开发的共同契约。请让它与当前仓库保持一致，不要把相邻 APEX 相关项目当作事实来源。

`CLAUDE.md` 是指向本文件的软链接，不要单独编辑。为降低维护成本，本仓库只维护这一份中文 AGENTS 文档，不再维护 `AGENTS_zh.md`。

## 当前项目事实

- APEX 是用于自动化合金性质工作流的 `apex-flow` Python 包。它负责准备计算任务、分发或本地运行任务、获取输出、归档结果并生成报告。
- 包元数据当前位于 `setup.py`：包名 `apex-flow`，开发版本 `2.0.0.dev0`，目标发布版本 `2.0.0`，Python `>=3.10`，命令行入口 `apex = apex.__main__:main`，许可证 LGPLv3。
- 当前 GitHub Actions CI 使用 Python `3.11`，执行 `pip install -e ".[test]"`，随后在 `tests/` 中运行 `coverage run -m unittest -v -f` 和 `coverage report`。
- 公开用户流程由配置驱动：结构目录、一个或多个 `param_*.json` 文件，以及可选的全局配置，例如 `global_bohrium.json`。
- 支持的计算器包括 LAMMPS 系列相互作用势、VASP 和 ABACUS。支持的执行路径包括本地 debug 模式、dflow/Argo、Bohrium，以及 DPDispatcher 的 SSH/HPC 或本地调度环境。
- `.venv/`、`build/`、`dist/`、`*.egg-info/`、coverage 输出、本地工作流输出、获取的模拟输出和临时 debug 目录等生成物或本地产物不能提交。

## 开发原则

- 提方案或改代码前先读相关代码路径。APEX 同时存在本地、dflow、dispatcher 和 archive 多条路径，行为上必须保持一致。
- 非平凡改动前，人类和 Codex 应先确认目标、架构、公开接口、迁移影响和测试证据，再修改代码。本地规划草稿放在 `.codex/workplans/`；该目录除 `.gitkeep` 外被忽略。
- 每个实现都必须能解释清楚：为什么要改、真实改了什么、保留了哪些旧行为、新增了哪些行为，以及证据如何证明这些结论。
- 未经人类明确同意，不要加入静默 fallback、宽泛异常吞掉逻辑，或会改变科学语义/输出约定的替代执行路径。缺少必要输入、API、命令、凭证或 artifact 时应清楚失败。
- 除非任务明确包含迁移计划，否则保留公开 JSON 参数键、CLI 行为、输出目录布局和 archive schema。
- 计算器特定的输入/输出规则应保留在 calculator 层；性质相关的科学逻辑应保留在 property 类和共享 property helper 中。
- 示例配置只能包含占位符。不要提交真实 Bohrium 密码、SSH 密码、API token、数据库密钥或私有势函数文件。
- 当用户可见的 CLI 行为、参数 schema、输出布局、依赖、镜像或 workflow 行为变化时，同一变更中要更新 `CHANGELOG.md` 和相关 README/examples。

## APEX 2.0 方向与边界

- 可以使用 Subagents 提出并对抗式审查新的性质工作流，但生成的工作流必须经过人类 review、确定性测试和领域验证，才能视为 APEX 支持行为。
- 结构建模功能必须清楚区分 CLI 输入、skill/agent 输入和人类确认选择。不要猜测材料结构，也不要把无效输入静默替换为生成结构。
- Skill 化 APEX 必须保留现有 CLI 和 JSON 工作流。Skill 应调用稳定的 APEX 命令并检查明确 artifact，而不是依赖隐藏状态或聊天上下文假设。
- 解耦 dflow/Argo 必须作为有意迁移进行。在评估 DPDispatcher 和可能的 Bohr CLI 提交、监控、回收和失败报告路径时，要为现有 dflow 行为保留兼容边界。
- 依赖现代化应减少不必要的锁定并提升兼容性，但每次依赖变化都必须包含安装验证、针对性运行检查，并在适用时检查生成的科学文件。
- CI/CD 工作应让贡献者更容易上手，并让测试行为更接近真实工作流。Mock 数据只有在能映射真实计算器输入、输出、日志和失败模式时才可接受。

## 测试与证据

- 当前 CI 观察到的规范测试运行器是带 coverage 的 `unittest`。除非项目有意加入，否则不要把 pytest、ruff、mypy、tox 或格式化工具描述成现有项目标准。
- 单元测试应覆盖参数校验、生成目录形状、生成输入文件、forward/backward 文件列表、结果解析、错误处理，以及敏感或大体积势函数/模型文件清理。
- Mock VASP、ABACUS、LAMMPS、phonopy、Bohrium、dflow 或调度器的测试，必须使用足够接近真实输入/输出的 fixture，以便暴露集成错误。
- 除非人类明确要求且凭证/资源清楚，不要运行真实 Bohrium、SSH/HPC、VASP、ABACUS 或长时间 LAMMPS 提交。如果验证需要真实 API 或生产数据，应向人类请求，并将确定性的本地测试分开。
- 修改 workflow graph 或 OP 时，要分别验证本地 debug 行为和 dflow OP 行为，因为它们共享科学核心代码，但 artifact plumbing 不同。
- 新增性质时，要在一个连贯变更中同步更新性质类、工厂注册、README/examples 参数文档和测试。

## Deprecated 或陈旧区域

- 只有代码或文档明确写出 `deprecated` 的内容才视为 deprecated。例如 README 当前将 `remote_host` 标记为 deprecated，并建议使用 `machine.remote_profile`。
- 旧 docs、镜像和 examples 在未验证前都视为可能陈旧，包括 `docs/Hands_on_auto-test.pdf`、`docs/Dockerfile`、README 中对 setup scripts 的引用，以及 examples 中的 Bohrium 镜像 tag。
- 不要只根据 examples 推断运行镜像行为。修改镜像名称或执行行为前，要追踪配置加载和代码路径。
- 除非任务包含明确迁移和弃用路径，不要把 dflow/Argo、旧配置键或现有 examples 当作清理项移除。

## Git 与协作

- 提交应保持小范围，聚焦一个 bug fix、功能切片或文档更新。不要把无关 bug fix、重构、依赖变化和文档混进一个 commit。
- 提交前运行 `git status --short`，检查 `git diff`，确认只暂存预期文件。
- 优先使用非交互式 git 命令。除非明确要求，不要重写历史、删除分支或强推。
- 如果分支同步很重要，使用 `git branch -vv`、`git remote -v`，以及在允许时使用 `git fetch` 加分歧计数验证。
- 测试或示例可能修改 `tests/` 下文件；运行前后都要检查 `git status`。

## 辅助参考

- 详细架构说明：`docs/development/architecture.md`
- 测试策略和 fixture 要求：`docs/development/testing.md`
- APEX 2.0 工程方向：`docs/development/apex-2-roadmap.md`
- 人类-Codex 协作 SOP：`docs/development/collaboration-sop.md`
- 用户可见变更记录：`CHANGELOG.md`
