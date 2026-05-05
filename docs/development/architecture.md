# APEX 架构说明

本文档是给开发者和代理使用的详细架构参考。`AGENTS.md` 保持为高层开发契约，具体实现地图放在这里维护。

## 入口

- CLI 入口是 `apex/main.py`；`apex/__main__.py` 转发到该入口。
- 公开子命令包括 `submit`、`do`、`retrieve`、`list`、`get`、`getsteps`、`getkeys`、`delete`、`archive` 和 `report`。
- 用户工作流由结构目录、`param_*.json` 和可选全局配置驱动，例如 `global_bohrium.json`。

## 主要执行路径

- `apex/submit.py` 加载配置和参数 JSON，判断 workflow 类型，打包上传目录，配置 dflow/Bohrium，构建 `FlowGenerator`，提交并监控 workflow，获取输出并归档结果。
- `apex/step.py` 实现本地 `apex do` 阶段：`make_relax`、`run_relax`、`post_relax`、`make_props`、`run_props` 和 `post_props`。
- `apex/flow.py` 持有 `FlowGenerator`，当前负责构建 dflow 的 `Workflow`、`Step` 和 `Task`，并支持按结构调度、模板复用和跳过/复用已完成任务。
- `apex/op/relaxation_ops.py` 和 `apex/op/property_ops.py` 将 dflow artifact 和参数桥接到科学核心逻辑。

## 科学核心

- `apex/core/common_equi.py` 处理弛豫任务创建、运行和后处理。
- `apex/core/common_prop.py` 分发性质任务创建、运行和后处理。新增性质类型必须通过 property factory 注册。
- `apex/core/property/` 包含 EOS、Cohesive、Decohesive、Elastic、Surface、Vacancy、Interstitial、Gamma、Phonon、Gruneisen 和 FiniteTlatt。
- `apex/core/calculator/` 持有 VASP、ABACUS、LAMMPS、任务抽象和计算器特定的输入/输出文件规则。
- `apex/report.py`、`apex/reporter/`、`apex/archive.py` 和 `apex/database/` 负责收集结果、生成报告，并写入本地或数据库归档。

## 必须保留的行为

- `rerun_finished=False` 会在所需结果文件存在时跳过已完成的 relaxation/property 结果。
- Joint workflow 可以复用已有弛豫输出，并跳过已完成性质目录，同时继续处理未完成任务。
- `cal_setting.overwrite_interaction` 允许性质级计算器设置覆盖，在 make/run/post 路径中必须保留。
- `skip_mismatch=True` 允许性质流程跳过不兼容的弛豫结构。
- 公开 JSON 键、输出目录名、archive 结构和 CLI 行为变化前必须有明确迁移计划。

## 已知现代化目标

- dflow/Argo 与 workflow 生成和 OP 包装耦合较深。解耦时应先建立兼容边界，再替换提交、监控或回收行为。
- 部分外部命令路径仍使用 shell 执行。替换时要围绕命令参数和失败行为补测试，而不是只做机械改写。
- `dpdata==0.2.17` 这类固定依赖，以及长期存在的 dflow 假设，应通过独立依赖 PR 处理，并包含安装和运行验证。
- 旧 docs、Dockerfile 和镜像 tag 可能陈旧。使用前应对照当前代码、当前 registry 和当前服务文档验证。

