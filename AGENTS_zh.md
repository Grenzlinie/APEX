# APEX 开发指南

本文档是用于指导代理和工程师编辑此 checkout 的工作指南。请使其与当前仓库保持一致，不要套用相邻 APEX 相关项目的约定。

## 项目概述

- APEX 是用于自动化合金性质工作流的 `apex-flow` Python 软件包。它负责准备计算任务、通过 dflow 或本地调试路径分发任务、获取输出、归档结果并生成报告。
- 软件包元数据目前位于 `setup.py`：包名 `apex-flow`，版本 `1.3.0`，Python `>=3.10`，控制台入口点 `apex = apex.__main__:main`，许可证 LGPLv3。
- 公开用户流程由配置驱动。用户提供结构目录、一个或多个 `param_*.json` 文件，以及可选的全局配置，例如 `global_bohrium.json`。
- 支持的计算后端包括 LAMMPS 系列相互作用势、VASP 和 ABACUS。支持的执行后端包括本地 debug 模式、dflow/Argo、Bohrium，以及 DPDispatcher 的 SSH/HPC 或本地调度环境。
- 当前 checkout 中已有生成/未跟踪目录 `build/` 和 `apex_flow.egg-info/`。除非用户明确要求检查或提交，否则将其视为构建产物。

## 架构与代码图谱

- CLI 入口：`apex/main.py` 定义 `submit`、`do`、`retrieve`、`list`、`get`、`getsteps`、`getkeys`、`delete`、`archive` 和 `report` 等子命令。`apex/__main__.py` 转发到该 CLI。
- 提交流程：`apex/submit.py` 加载配置和参数 JSON，判断工作流类型，打包上传目录，配置 dflow/Bohrium，构建 `FlowGenerator`，提交并监控工作流，获取输出并归档结果。
- 工作流图：`apex/flow.py` 持有 `FlowGenerator`，负责构建 dflow 的 `Workflow`、`Step` 和 `Task`。近期开发将弛豫和性质任务按结构拆分，复用模板降低 manifest 大小，并支持已完成任务的跳过/复用。
- OP 层：`apex/op/relaxation_ops.py` 和 `apex/op/property_ops.py` 是 dflow OP 包装器。它们把 artifact 和参数桥接到核心函数，执行后处理，并清理获取结果中的敏感或大体积势函数文件。
- 本地步骤路径：`apex/step.py` 实现 `apex do` 的本地 `make_relax`、`run_relax`、`post_relax`、`make_props`、`run_props` 和 `post_props`。本地 post 步骤会尝试非致命归档，以便和 `apex submit` 行为保持接近。
- 科学核心：`apex/core/common_equi.py` 处理弛豫任务创建、运行和后处理。`apex/core/common_prop.py` 分发性质任务创建、运行和后处理。
- 性质模块：`apex/core/property/` 包含 EOS、Cohesive、Decohesive、Elastic、Surface、Vacancy、Interstitial、Gamma、Phonon、Gruneisen 和 FiniteTlatt。新增性质类型时需要更新 `make_property_instance` 和测试。
- 计算器模块：`apex/core/calculator/` 包含 VASP、ABACUS、LAMMPS、任务抽象和计算器工厂逻辑。计算器特定的输入/输出文件规则应保留在这一层。
- 报告与归档：`apex/report.py`、`apex/reporter/` 和 `apex/archive.py` 收集结果、构建报告，并写入本地或数据库归档。`apex/database/` 支持 local、MongoDB 和 DynamoDB 风格存储。

## 支持的工作流与功能

- 工作流类型包括仅弛豫、仅性质，以及弛豫加性质的 joint 工作流。CLI 可以从参数文件推断，也可以通过 `--flow` 显式指定。
- 目前支持的性质包括状态方程、内聚能、解聚能、弹性常数、表面能、空位形成、间隙形成、广义层错能、声子谱、Gruneisen/热膨胀工作流，以及有限温度晶格参数。
- `rerun_finished=False` 是重要行为。当所需结果文件已存在时，当前代码会在弛豫、性质和 joint 工作流中跳过已完成结果。修改上传、备份或按结构调度逻辑时不能破坏该行为。
- Joint 工作流可以复用已有弛豫输出，也可以跳过单个已完成性质目录，同时继续运行未完成的结构或性质。
- 性质 `cal_setting.overwrite_interaction` 允许性质级计算器设置覆盖。make/run/post 路径都要保留该覆盖行为。
- 当性质设置 `skip_mismatch=True` 时，可以跳过不匹配的弛豫结构。

## 配置与依赖

- 运行时依赖声明在 `setup.py`。关键库包括 `numpy<2.0.0`、`pydflow>=1.7.83`、`pymatgen`、`pymatgen-analysis-defects`、`dpdata==0.2.17`、`dpdispatcher`、`phonopy`、`plotly`、`dash`、`dash_bootstrap_components`、`seekpath`、`fpop`、`boto3`、`pymongo`、`scipy`、`matplotlib`、`pandas`、`requests`、`PyYAML`、`dargs` 和 `packaging`。
- 端到端生产运行可能依赖外部工具和服务：LAMMPS、VASP、ABACUS、phonopy/phonoLAMMPS、Bohrium、dflow/Argo、Docker 镜像、SSH/HPC 调度器和数据库服务。
- `apex/config.py` 将全局 JSON 映射为 dflow 配置、S3 配置、Bohrium 凭证、dispatcher 配置、基础镜像/运行命令设置，以及归档数据库设置。
- 示例配置可能包含凭证占位符。不要提交真实 Bohrium 密码、SSH 密码、云 token、数据库密钥或私有势函数文件。
- README 和 examples 是面向用户的 API 文档。参数 schema、工作流行为、镜像名称或 CLI 行为变化时，应在同一变更中更新 README 和 examples。

## 开发环境

- 以 Python 3.10 兼容性为基线，因为 CI 使用 Python 3.10。包声明 `python_requires='>=3.10'`。
- 当前打包来源是 `setup.py`。根目录没有 `pyproject.toml`，因此不要假设已有 uv、Poetry、hatch 或现代 setuptools 工作流，除非后续显式添加。
- 本地开发安装使用 `pip install -e .`。测试依赖使用 `pip install -e ".[test]"`；该 extra 已在 `setup.py` 中定义，并与当前 CI 工作流一致。
- 不要提交生成物或环境目录：`.venv/`、`build/`、`dist/`、`*.egg-info/`、coverage 产物、本地工作流输出、获取的模拟输出和临时 debug 目录。
- 许多测试和示例会在 `tests/` 输入目录下创建或删除目录。运行前后都要检查 `git status --short`。

## 测试与 CI

- GitHub Actions 工作流 `.github/workflows/main.yml` 在 push 和 pull request 时运行，Python 版本为 3.10。
- CI 安装命令为 `pip install --upgrade pip` 和 `pip install -e ".[test]"`。
- CI 测试命令从 `tests/` 目录运行：`SKIP_UT_WITH_DFLOW=0 DFLOW_DEBUG=1 coverage run -m unittest -v -f`，随后执行 `coverage report`。
- 当前仓库观察到的规范测试运行器是 `unittest`。除非项目迁移或添加 pytest 配置，不要把 pytest 描述为规范测试入口。
- 针对性本地验证优先运行最小相关 unittest 模块，例如 `cd tests && python -m unittest -v test_gruneisen`。
- 修改 dflow OP 签名、工作流生成或任务打包时，要覆盖 artifact 路径和生成任务列表。
- 修改性质类时，尽量覆盖参数校验、`task_type`、`task_param`、生成任务目录结构，以及 `compute`/后处理行为。
- 修改计算器时，要覆盖生成输入文件、forward/backward 文件和势函数/模型文件清理。

## Git 与协作

- 当前 checkout 观察到的分支布局：`exp-1.3.0` 与本地和远程 `devel-1.3.0` 指向同一提交；`main` 跟踪 `origin/main`。提交或推送前重新检查分支状态。
- 近期 git 历史重点包括 README 更新、Gruneisen 工作流、phonon 和 LAMMPS 工具链验证、`rerun_finished=False`、按结构弛豫和性质调度、有限温度晶格参数、decohesive 更新和示例维护。重构时要保留这些行为。
- 保持提交范围小。不要把生成目录、本地环境、下载 artifact、凭证或无关输出混入代码/文档提交。
- 提交前运行 `git status --short`，检查 `git diff`，确认只暂存预期文件。
- 优先使用非交互式 git 命令。除非明确要求，不要重写历史、删除分支或强推。
- 如果分支同步很重要，使用 `git branch -vv`、`git remote -v`，以及在允许时使用 `git fetch` 加分歧计数验证。

## 工程风险与缺口

- 打包说明：测试依赖集中在 `setup.py` 的 `test` extra 中；保持 CI 和本地安装命令与之对齐。
- 卫生说明：根目录 `.gitignore` 排除了打包生成物、环境目录、缓存、coverage 和本地工作流产物。除非用户明确要求，不要强制暂存被忽略的产物。
- 工具缺口：目前未观察到 lint、format、type-check、tox 或 pytest 配置。需要时应显式添加，不要假设默认存在。
- 安全缺口：部分外部模拟命令仍使用 shell 执行。不要重新引入基于 shell 的文件清理，尤其是路径来自用户配置或 interaction model 名称时。
- 集成缺口：许多真实工作流依赖重型外部可执行文件和云服务。单元测试应尽量 mock 外部命令，并把本地确定性验证和生产工作流提交分开。
- 文档漂移风险：README badge 已更新为 `1.3.0`；Bohrium 镜像 tag 示例可能滞后于 Python 包版本，使用前要确认 registry 中实际可用 tag。
- 密钥管理风险：`global_bohrium.json` 示例描述了凭证。示例只能保留占位符，避免记录真实密钥。
- 兼容性风险：科学文件格式和第三方库经常变化。升级依赖时要运行计算器相关测试并检查生成文件，不要只做 import 检查。

## Agent 操作规则

- 编辑前先读取相关代码路径。本项目存在本地、dflow、dispatcher 和 archive 多条路径，必须保持一致。
- 除非任务明确包含迁移，否则保留公开 JSON 参数键和输出目录约定。
- 除非用户明确要求且凭证/资源清楚，不要运行真实 Bohrium、SSH/HPC、VASP、ABACUS 或长时间 LAMMPS 提交。
- 编辑后优先运行小范围针对性测试。完整工作流提交不能替代参数处理和生成文件相关的单元测试。
- 将 `build/` 和 `apex_flow.egg-info/` 视为当前 checkout 的生成 artifact。除非用户要求，不要修改或暂存它们。
- 新增性质时，要同步更新性质类、`apex/core/common_prop.py` 中的工厂、README/examples 参数文档和测试。
- 修改工作流图生成时，要分别验证本地 debug 行为和 dflow OP 行为，因为它们共享科学核心代码，但 artifact plumbing 不同。
