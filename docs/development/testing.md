# 测试策略

APEX 测试应在本地保持确定性，同时尽量贴近真实计算器工作流。当改动涉及外部工具或云服务时，单元测试通过不等于真实计算流程已经验证。

## 当前基线

- GitHub Actions 当前使用 Python 3.11。
- 安装命令：`pip install -e ".[test]"`。
- 测试命令从 `tests/` 目录运行：`SKIP_UT_WITH_DFLOW=0 DFLOW_DEBUG=1 coverage run -m unittest -v -f`。
- 当前观察到的规范测试运行器是带 coverage 的 `unittest`。其他工具只有在有意加入后才算项目标准。

## Fixture 来源

- `tests/confs/` 存放 POSCAR、STRU、CIF 等结构输入。
- `tests/vasp_input/`、`tests/abacus_input/` 和 `tests/lammps_input/` 存放输入模板、示例势函数/轨道/模型，以及参数 JSON。
- `tests/equi/` 存放有代表性的弛豫输出和解析参考，例如 VASP OUTCAR/CONTCAR、ABACUS 日志和 LAMMPS 结构。
- `tests/output/` 存放部分性质或弛豫的 golden output。

## 按变更类型要求覆盖

- CLI 或 JSON schema 变化：覆盖解析、默认值、非法输入和向后兼容。
- Workflow graph 或 OP 变化：覆盖生成任务路径、artifact 路径、本地 debug 行为和 dflow OP 行为。
- Calculator 变化：覆盖生成输入文件、forward/backward 文件列表、势函数/模型文件处理和失败路径。
- Property 变化：覆盖参数校验、`task_type`、`task_param`、任务目录形状、后处理，以及适用时的 report/archive 输出。
- 依赖变化：验证安装、导入、针对性行为，以及受该依赖影响的生成科学文件。

## Mock 规则

- Mock VASP、ABACUS、LAMMPS、phonopy、dflow、Bohrium 或调度器的测试，必须使用与真实 workflow 对应的文件名、目录形状、日志和结果片段。
- 不要把正在修改的行为 mock 掉。如果 bug 在命令构造，就测试构造出的命令或 argv；如果 bug 在解析，就用接近真实输出的片段测试。
- 明确区分确定性单元测试和可选集成测试。后者可能需要外部可执行文件、凭证或集群/云资源。

## 真实 workflow 验证

- 未经人类明确授权且凭证/资源不清楚时，不要运行真实 Bohrium、SSH/HPC、VASP、ABACUS 或长时间 LAMMPS 任务。
- 如果某个改动无法用本地 fixture 验证，应说明需要的真实 API、可执行文件、输入、镜像或账户。
- 执行真实验证时，要记录命令、环境、输入 fixture、结果 artifact 和所需清理动作。

