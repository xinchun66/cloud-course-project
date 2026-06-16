# 成员B进度清单

## 总体进度

| 状态 | 任务 | 当前进度 |
|---|---|---|
| [x] | T1 应用容器化 | 已完成，Dockerfile、docker-compose、SWR推送代码和报告章节均有内容。 |
| [x] | A-1 Spark 数据清洗 | 已完成，`spark/analysis.py` 中数据清洗代码完整（Schema、缺失值、两种策略、统计信息）。 |
| [x] | A-2 Spark SQL 统计分析 | 已完成，`spark/analysis.py` 中 4 个 Spark SQL 查询完整（GROUP BY、Top-N、时间趋势、窗口函数）。 |
| [x] | A-3 性能对比与 Amdahl 分析 | 已完成，`spark/analysis.py` 中 Pandas/PySpark 性能对比、图表生成和 Amdahl 分析代码完整。 |
| [x] | 附加题 3 C-1 分布式 AI 训练 | 已完成，`extra/c1_ddp_mnist.py` 代码完整，支持单机和 DDP 分布式训练。 |
| [ ] | T6 压测（B 负责部分） | 未开始。需执行 `ab` 或 curl 压测脚本，与 A 协作完成扩缩容截图。 |
| [ ] | 附加题 2 CI/CD 构建部分 | 未开始。需配置流水线中的镜像构建、测试和 SWR 推送步骤。 |

### 报告撰写进度

| 状态 | 章节 | 当前进度 |
|---|---|---|
| [x] | 封面、目录、整体格式 | 已完成，导言区、自定义命令、封面、目录完整。 |
| [x] | 项目概述与分工说明（ch01） | ✅ 有详细内容（5059 chars），含设计目标、任务要求、分工、完成清单。 |
| [x] | 华为云环境信息（ch02） | ✅ 有详细内容（12137 chars），含服务配置、K8s 集群信息。 |
| [x] | T1~T6 云计算平台搭建（ch03） | ✅ 有详细内容（16065 chars），T1~T6 全部介绍完整。 |
| [ ] | Spark 大数据分析（ch04） | ❌ 仅框架，28 个子节均为空（仅 `\mbox{}`）。代码已有，需补充文字说明。 |
| [ ] | 问题记录与解决方案（ch05） | ❌ 仅框架，8 个子节均为空。需补充镜像、CCE、Spark、性能测试等问题。 |
| [ ] | 总结与收获（ch06） | ❌ 仅框架，8 个子节均为空。需补充容器化、K8s、Spark、Amdahl 等内容。 |
| [ ] | 附录：核心配置与代码（ch07） | ❌ 仅框架，12 个子节均为空。需粘贴 Dockerfile、YAML、Spark 代码等。 |
| [ ] | 附录：实验截图索引（ch08） | ❌ 仅框架，6 个子节均为空。需按任务组织截图索引。 |

## T1 应用容器化

- [x] 编写后端 Dockerfile，保留多阶段构建结构。
- [x] 修改后端 `requirements.txt`，包含 Flask、redis、requests 等依赖。
- [x] 编写前端 Dockerfile，基于 `nginx:1.25-alpine`。
- [x] 编写前端 Nginx 配置 `frontend/nginx.conf`。
- [x] 修改前端首页 `frontend/static/index.html`，加入姓名和学号。
- [x] 编写 `docker-compose.yml`，定义 backend、redis 服务。
- [x] 本地运行 `docker compose up -d --build` 验证前后端通信。
- [x] 构建后端镜像并推送至 SWR。
- [x] 构建前端镜像并推送至 SWR。
- [x] 保存本地联调截图到 `figures/T1/`。
- [x] 编写 ch03 中 T1 子节报告文字（Dockerfile 多阶段构建、依赖、联调、SWR 推送）。

说明：后端 Dockerfile 使用 `python:3.11-slim` 基础镜像，分为依赖安装（`--no-cache-dir`）和运行时复制两个阶段；前端 Dockerfile 将自定义 `nginx.conf` 和静态页面复制到镜像中；`docker-compose.yml` 中后端通过环境变量连接 Redis，Compose 网络使容器间可直接通过服务名称通信。SWR 推送前已确保镜像 Tag 与 CCE Deployment 中的引用地址一致。

## T6 HPA 弹性伸缩（B 负责部分）

- [ ] 与 A 同学沟通，确认后端 ELB 公网 IP 地址。
- [ ] 安装 `ab`（Apache Bench）或准备 curl 循环脚本。
- [ ] 使用 `ab -n 10000 -c 200 http://<ELB_IP>/api/ping` 发起并发压测。
- [ ] 观察后端 Pod 从 1 个扩容到 2 个或更多。
- [ ] 停止压测后观察 Pod 缩回 1 个。
- [ ] 保存压测过程和扩缩容截图。
- [ ] 将截图提供给 A 同学同步保存到 `figures_A/T6/`。
- [ ] 补写 ch03 中 T6 压测部分的文字和截图说明。

说明：当前 T6 的 HPA 配置（`k8s/backend-hpa.yaml`）和 metrics-server 验证已由 A 完成，但缺少实际压测过程和截图。B 需要执行压测，与 A 配合完成完整验收记录。

## A-1 Spark 数据清洗

- [x] 加载豆瓣电影数据集（`douban_movies.csv`）。
- [x] 打印 Schema，确认字段类型。
- [x] 打印前 5 行数据预览。
- [x] 统计各字段缺失值比例。
- [x] 策略一：删除 `movie_id`、`title`、`year`、`rating_score`、`rating_count` 等关键字段为空的行。
- [x] 策略二：用 `"Unknown"` / `"No summary"` 填充 `original_title`、`genres`、`countries`、`directors`、`summary` 等可选字段。
- [x] 输出清洗前后行数对比：`before_count` → `after_count`。
- [x] 输出清洗后 mean/stddev/min/max 等统计信息。
- [x] 补写 ch04 中 A-1 子节的报告文字（数据集说明、清洗策略、统计结果分析）。

说明：数据清洗代码位于 `spark/analysis.py` 的 A-1 部分，使用 PySpark DataFrame API 完成。关键逻辑包括：`dropna(subset=[...])` 删除关键字段缺失行，`fillna({...})` 填充可选字段，`year` 字段强转为 int 类型。输出包括 `print_missing_ratios()` 和 `print_numeric_statistics()` 两个辅助函数。

## A-2 Spark SQL 统计分析

- [x] 查询一：GROUP BY 聚合分析——按类型统计电影数量、平均评分、平均评分人数，筛选出现次数 >= 5 的类型并按评分降序排列。
- [x] 查询二：ORDER BY Top-N 分析——按评分人数降序排列，输出评分最高的 10 部电影。
- [x] 查询三：时间维度趋势分析——按年份统计电影数量、平均评分、平均评分人数，筛选 1900~2030 年间且电影数量 >= 3 的年份。
- [x] 查询四：窗口函数分析——按国家/地区分区，使用 `ROW_NUMBER()` 输出每个国家评分前三的电影。
- [x] 每个查询附带不少于 50 字的中文分析说明。
- [x] 结果保存（控制台输出）。
- [x] 补写 ch04 中 A-2 子节的报告文字（4 个查询的目的、逻辑、结果分析）。

说明：SQL 分析代码位于 `spark/analysis.py` 的 `run_spark_sql_analysis()` 函数。数据集通过 `LATERAL VIEW explode(split(...))` 对 genres 和 countries 进行列转行，各查询的结果截图需在运行时保存到 `figures/` 目录。四个查询覆盖了 GROUP BY、ORDER BY、时间趋势、窗口函数四种 SQL 分析模式。

## A-3 性能对比与 Amdahl 分析

- [x] 使用 Pandas 实现与 Query 1 相同的分组聚合查询，记录执行时间。
- [x] 使用 PySpark（executor=1）执行相同查询，记录执行时间。
- [x] 使用 PySpark（executor=2）执行相同查询，记录执行时间。
- [x] 输出性能对比表（method, executor_instances, time_seconds, speedup_vs_pandas）。
- [x] 使用 Matplotlib 绘制性能对比柱状图（`a3_performance_exec_{n}.png`）。
- [x] 基于 executor=1 和 executor=2 的实测加速比，计算并行比例 f。
- [x] 绘制实测加速比 vs Amdahl 理论加速比对比图（`a3_amdahl_speedup.png`）。
- [x] 保存性能 CSV 和 Amdahl 汇总 CSV 到 `figures/` 目录。
- [x] 补写 ch04 中 A-3 子节的报告文字（实验设计、对比图、Amdahl 分析、非线性原因讨论）。

说明：性能对比代码位于 `spark/analysis.py` 的 `run_performance_comparison()` 函数。需要分别在 executor=1 和 executor=2 的条件下各运行一次 `analysis.py`，两次运行生成的数据文件由 `write_amdahl_outputs()` 函数汇总。Amdahl 分析中重点说明：加速比受限于串行工作（CSV 解析、任务启动、shuffle 通信、序列化）和小数据集无法分摊分布式开销等因素，导致加速比远低于线性。

## 附加题 3 C-1 分布式 AI 训练

- [x] 实现 MNIST CNN 模型（`MnistCnn`），含 2 个卷积层 + 2 个池化层 + 全连接分类器。
- [x] 支持单机训练模式（`--ddp` 参数控制）。
- [x] 支持 PyTorch DDP 分布式训练模式。
- [x] 使用 `DistributedSampler` 确保数据分片。
- [x] 记录单机训练时间与分布式训练时间。
- [x] 保存训练日志截图。
- [x] 补写报告中 C-1 子节的文字说明（AllReduce、数据并行、模型并行区别）。

说明：DDP 代码位于 `extra/c1_ddp_mnist.py`。训练过程中会分别记录单机和分布式的训练时间，用于对比分析。代码通过 `torch.distributed.init_process_group` 初始化分布式环境，通过 `DistributedDataParallel` 包装模型，通过 `DistributedSampler` 切分数据。报告中需要补充 AllReduce 梯度同步机制、数据并行与模型并行的适用场景说明。

## 附加题 2 CI/CD 构建部分

- [ ] 确定 CI/CD 平台（如 GitHub Actions、GitLab CI 或华为云 SWR 流水线）。
- [ ] 编写 CI/CD 配置文件，定义流水线阶段：
  - [ ] 代码检出。
  - [ ] 镜像构建（backend 和 frontend）。
  - [ ] 本地测试或镜像扫描。
  - [ ] 镜像推送至 SWR。
- [ ] 配置 SWR 认证凭据（Secret 或登录步骤）。
- [ ] 与 A 协作，确认流水线执行并通过。
- [ ] 保存 CI/CD 流水线 Passed 截图。
- [ ] 保存 SWR 镜像 Tag 更新截图。
- [ ] 补写报告中 CI/CD 子节的文字说明（流水线流程、构建推送过程）。

说明：CI/CD 构建部分由 B 负责，云端部署验证由 A 负责。建议使用 GitHub Actions，将 backend 和 frontend 的构建和推送合并到同一个 workflow 中。backend 和 frontend 镜像需分别构建，Tag 建议使用 `v1-{commit_sha}` 格式以区分版本。

## 报告待补充章节

### ch04 Spark 大数据分析

- [ ] A-0 部分：写 Spark Operator 安装过程、YAML 参数说明、WordCount 作业提交和 Pod 状态验证。
- [ ] A-1 部分：写数据集选择说明、Schema 输出、前 5 行预览、缺失值统计、两种清洗策略、前后行数对比。
- [ ] A-2 部分：写 4 个查询的目的、SQL 逻辑、结果截图和不少于 50 字的分析说明。
- [ ] A-3 部分：写实验设计、Pandas 和 PySpark 执行时间对比、性能对比图、Amdahl 加速比分析、非线性原因讨论。

### ch05 问题记录与解决方案

- [ ] 镜像构建与推送问题：如 docker-compose 中 Redis 连接失败、SWR 登录认证、镜像 Tag 不一致等。
- [ ] CCE 部署与网络访问问题：如 ELB 公网 IP pending、跨命名空间 Service 访问等。
- [ ] PVC 与 HPA 验证问题：如 PVC 创建后状态为 Pending、HPA 指标采集延迟等。
- [ ] Spark 作业提交问题：如 SparkApplication YAML 参数配置错误、Driver/Executor OOM 等。
- [ ] OBS 或本地数据读取问题：如 CSV 解析中字段引号转义、s3a 路径认证等。
- [ ] 性能测试误差问题：如 Pandas 和 PySpark 运行环境差异、Cache 未预热导致的偏差等。

### ch06 总结与收获

- [ ] 容器化与 K8s 部署理解：Dockerfile 多阶段构建、Service 发现、ConfigMap/Secret 配置分离。
- [ ] 配置分离、持久化与弹性伸缩理解：PVC 生命周期、HPA 指标采集和缩容冷却。
- [ ] 分布式数据处理流程理解：Spark on K8s 架构、Driver/Executor 角色、数据清洗到 SQL 分析。
- [ ] 性能对比与 Amdahl 定律理解：Pandas 单机 vs PySpark 分布式、并行比例 f 的意义。
- [ ] 主要挑战和改进方向：云环境排错经验、CI/CD 自动化建议。

### ch07 附录：核心配置与代码

- [ ] 后端 Dockerfile 全文。
- [ ] 前端 Dockerfile 全文。
- [ ] docker-compose.yml 全文。
- [ ] Deployment 与 Service YAML 全文。
- [ ] ConfigMap 与 Secret YAML 全文。
- [ ] PVC 与 HPA YAML 全文。
- [ ] wordcount.py 全文。
- [ ] analysis.py 全文（或核心代码片段）。
- [ ] 性能测试脚本（如 ab 命令、curl 循环脚本）。

### ch08 附录：实验截图索引

- [ ] T1 截图索引：本地联调、后端返回、后端日志、SWR 镜像列表。
- [ ] T2 截图索引：CCE 集群信息、节点 Ready 状态。
- [ ] T3 截图索引：Pod Running、Service、ELB 公网 IP、/api/ping 返回。
- [ ] T4 截图索引：PVC Bound、Redis 写入、删除 Pod、重建查询。
- [ ] T5 截图索引：ConfigMap 挂载、exec 验证。
- [ ] T6 截图索引：metrics-server、HPA、扩容、缩容。
- [ ] A-0 截图索引：Spark Operator Pod、Driver/Executor Pod、作业日志。
- [ ] A-1/A-2/A-3 截图索引：数据清洗、SQL 查询结果、性能对比图、Amdahl 图表。

## 下一步

1. **立即执行 T6 压测**：与 A 配合完成压测并获取扩缩容截图，补全 T6 验收记录。
2. **补写 ch04 报告正文**：A-1/A-2/A-3 代码已有，将代码分析和运行结果编写为报告文字。
3. **补写 ch05~ch08**：问题记录、总结收获、附录代码和截图索引。
4. **推进 CI/CD 构建配置**：确定平台后编写流水线配置文件并执行验证。
5. **在 CCE 上运行 analysis.py**：提交 SparkApplication 到集群，获取实际运行截图。
