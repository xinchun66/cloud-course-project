# 成员 B 进度清单

> 成员：李欣纯（2023116052）  
> 对照文档：`分工/分工文档.md`  
> 最后更新：2026-06-16

## 总体进度

| 状态 | 任务 | 当前进度 |
|---|---|---|
| [x] | T1 应用容器化 | 已完成：Dockerfile、Compose、SWR 推送、第三章 T1 正文与截图引用。 |
| [x] | A-1 Spark 数据清洗 | 已完成：`spark/analysis.py` 清洗逻辑 + 第四章 A-1 正文与截图。 |
| [x] | A-2 Spark SQL 统计分析 | 已完成：4 类查询 + 第四章 A-2 正文与截图。 |
| [x] | A-3 性能对比与 Amdahl 分析 | 已完成：性能对比代码、图表输出 + 第四章 A-3 正文与截图。 |
| [x] | 附加题 3 C-1 分布式 AI 训练（代码） | 已完成：`extra/c1_ddp_mnist.py`、`k8s/c1-*.yaml`、PyTorch 镜像 Dockerfile。 |
| [~] | T6 压测（B 负责部分） | 部分完成：A 已在 CloudShell 用 curl 循环完成压测并保存 `figures_A/T6/` 截图；B 已补写第三章 T6 全文。B 原定的 `ab` 压测未单独执行，与分工文档“或其他压测工具”一致，可视为协作完成。 |
| [x] | 附加题 2 CI/CD 构建部分 | 已完成：workflow 跑通（Tag `b7817d3`）、`figures_A/附加题2/` 验收截图 8 张、`figures_B/附加题2/` Secrets 截图、报告 ch04sup/ch05/ch08 已补全。 |
| [x] | 附加题专章（ch04sup） | 已完成：`chapters/ch04sup_附加题实践.tex`，含监控、CI/CD、C-1 三节及三级标题；附加题 2 已嵌入验收截图。 |
| [x] | 附加题 2 CI/CD 验收截图 | 已完成：`figures_A/附加题2/` 6 张核心验收 + 2 张问题排查；`figures_B/附加题2/01_CICD_GitHubSecrets_已配置.png`。 |
| [~] | 附加题 3 C-1 云端运行截图 | 代码与报告原理已写；CCE 训练日志截图可后续替换进正文。 |

### 报告撰写进度

| 状态 | 章节 | 当前进度 |
|---|---|---|
| [x] | 封面、目录、整体格式 | 已完成；主文档含 `listings` 代码清单样式。 |
| [x] | 项目概述与分工说明（ch01） | 已完成：设计目标、分工表、概述截图。 |
| [x] | 华为云环境信息（ch02） | 已完成：SWR/CCE/ELB 配置与 T2 环境截图。 |
| [x] | T1~T6 云计算平台搭建（ch03） | 已完成：T1~T6 全文；T6 已由“待补充”更新为完整验收记录。 |
| [x] | Spark 大数据分析（ch04） | 已完成：A-0~A-3 正文、截图与分析说明。 |
| [x] | 问题记录与解决方案（ch05） | 已完成：仅保留 7 张故障现场图 + 学术化排错叙述。 |
| [x] | 总结与收获（ch06） | 已完成：平台搭建、Spark、Amdahl 与反思。 |
| [x] | 附录：核心配置与代码（ch07） | 已完成：Dockerfile、YAML、Spark 核心代码摘录。 |
| [x] | 附录：实验截图索引（ch08） | 已完成：按任务分类索引，含统计表与第五章问题专索引。 |
| [x] | 附加题专章（ch04sup） | 已完成：接在第四章 Spark 之后，含监控、CI/CD、C-1。 |

---

## T1 应用容器化

- [x] 编写后端 Dockerfile（多阶段构建）。
- [x] 修改 `backend/requirements.txt`（Flask、redis、requests）。
- [x] 编写前端 Dockerfile 与 `frontend/nginx.conf`。
- [x] 修改 `frontend/static/index.html`（姓名、学号）。
- [x] 编写 `docker-compose.yml` 并完成本地联调。
- [x] 构建并推送 backend/frontend 镜像至 SWR（组织以 A 侧 `cloud-course-a` 为准）。
- [x] 报告第三章 T1 文字与截图引用（路径 `assets/report_figures/t1/`）。

说明：镜像 Tag 需与 A 同学 CCE Deployment 中引用地址一致；推送前核对 `swr.cn-north-4.myhuaweicloud.com/<组织>/backend:v1`。

---

## T6 HPA 弹性伸缩（B 负责部分）

- [x] 与 A 确认 ELB 公网 IP（`1.92.151.224`，见 `figures_A/T6/T6说明.md`）。
- [~] 使用 `ab` 压测：CloudShell 未安装 `ab`，由 A 使用 curl 循环脚本替代（符合任务书允许方式）。
- [x] 扩容/缩容截图已归档至 `figures_A/T6/`（核心验收：06、08）。
- [x] 第三章 T6 章节已由 B 补写完整（metrics-server、HPA 配置、压测、扩缩容、问题处理）。

说明：按分工文档，B 负责压测、A 负责 HPA 资源与截图整理；实际压测在 A 侧 CloudShell 完成，B 负责报告整合。若答辩需说明分工，可注明“压测脚本由 A 执行，B 撰写 T6 验收叙述”。

---

## A-1 Spark 数据清洗

- [x] 加载 `douban_movies.csv`，输出 Schema 与前 5 行。
- [x] 统计缺失值比例；策略一 `dropna`、策略二 `fillna`。
- [x] 清洗前后行数与数值统计输出。
- [x] 第四章 A-1 正文与 `figures_B/A1/` 截图引用。

---

## A-2 Spark SQL 统计分析

- [x] Query 1：GROUP BY 类型聚合。
- [x] Query 2：ORDER BY Top-N（评分人数）。
- [x] Query 3：按年份趋势分析。
- [x] Query 4：窗口函数国家排名。
- [x] 每查询不少于 50 字分析说明（嵌入 `analysis.py` 与第四章正文）。
- [x] 第四章 A-2 正文与 `figures_B/A2/` 截图引用。

---

## A-3 性能对比与 Amdahl 分析

- [x] Pandas / PySpark（1 Executor）/ PySpark（2 Executor）三组对比。
- [x] 输出 CSV 与 Matplotlib 图表（`figures/a3_*.csv/png`）。
- [x] Amdahl 理论加速比计算与讨论。
- [x] 第四章 A-3 正文；A 协助截图见 `figures_A/A-3协助/`。
- [x] 第五章保留 A-3 相关故障截图 3 张（内存、Pending、权限）。

实测数据（报告第四章表格）：Pandas 0.5031 s，PySpark×1 1.1460 s，PySpark×2 1.1605 s。

---

## 附加题 2 CI/CD 构建部分

- [x] 选定 GitHub Actions 作为 CI 平台。
- [x] 编写 `.github/workflows/cicd-app-to-swr-cce.yml`（checkout → 构建 backend/frontend → 推送 SWR，Tag 为 commit SHA 前 7 位）。
- [x] 编写 `figures_A/附加题2/C2_CICD说明.md`（Secrets 要求、CloudShell 更新 Deployment 命令、验收清单）。
- [x] 在 GitHub 配置 `SWR_USERNAME`、`SWR_PASSWORD` Secrets（见 `figures_B/附加题2/`）。
- [x] 手动触发 workflow（`b7817d3`），保存 **Passed** 截图。
- [x] 与 A 协作：CloudShell `kubectl set image` 更新 Deployment，保存 SWR Tag / Deployment / Pod / 接口截图至 `figures_A/附加题2/`。
- [x] 报告增写 CI/CD 专节（流水线阶段、验收截图、CI/CD 与 GitOps 概念；第五章补充 kubeconfig 与 Service 访问问题）。

---

## 附加题 3 C-1 分布式 AI 训练

- [x] 实现 `extra/c1_ddp_mnist.py`（MNIST CNN、单机/DDP、gloo 后端）。
- [x] 提供 `extra/Dockerfile.pytorch`、`k8s/c1-single-mnist-job.yaml`、`k8s/c1-pytorchjob.yaml`。
- [ ] 在 CCE 运行单机与 PyTorchJob 分布式任务，保存训练时间日志截图。
- [ ] 报告增写 C-1 专节：训练时间对比、AllReduce、数据并行 vs 模型并行（分工文档要求 B 主笔）。

---

## 附加题 1 监控章节（B 主写，A 提供材料）

- [ ] 阅读 A 提供的 `figures_A/附加题1/C1监控说明.md` 与 Grafana 截图。
- [ ] 撰写 Prometheus Pull 采集原理（可参考 C1 说明第 4 节）。
- [ ] 撰写至少 3 个指标含义（CPU 使用率、内存使用率、分配率等，见 C1 说明第 5 节）。
- [ ] 将监控内容并入报告（建议：新增“附加题”小节，或并入第六章改进方向之外的独立附录）。

说明：第五章仅收录 Helm 超时 **问题** 截图，正常监控验收图不在第五章重复出现。

---

## 报告章节完成明细（B 主笔）

| 章节 | 文件 | 状态 | 备注 |
|---|---|---|---|
| ch01 | `chapters/ch01_课程设计概述.tex` | ✅ | 含分工表 |
| ch02 | `chapters/ch02_华为云实验环境.tex` | ✅ | A 提供截图，B 整理 |
| ch03 | `chapters/ch03_云计算平台搭建.tex` | ✅ | T6 已更新 |
| ch04 | `chapters/ch04_Spark大数据分析.tex` | ✅ | A-0 材料来自 A |
| ch05 | `chapters/ch05_问题记录与解决方案.tex` | ✅ | 仅问题截图 |
| ch06 | `chapters/ch06_总结与收获.tex` | ✅ | A 可补充云环境经验 |
| ch07 | `chapters/ch07_附录核心配置与代码.tex` | ✅ | 代码摘录 |
| ch08 | `chapters/ch08_附录实验截图索引.tex` | ✅ | 119 张索引统计（含附加题 2） |

---

## 与分工文档的对照（B 职责摘要）

| 分工文档条目 | B 负责内容 | 当前状态 |
|---|---|---|
| T1 应用容器化 | Dockerfile、Compose、SWR、截图 | ✅ 完成 |
| T6 压测 | ab/curl 压测、协作截图 | ✅ 协作完成（curl 由 A 执行） |
| A-1 / A-2 / A-3 | Spark 代码与报告 | ✅ 完成 |
| 附加题 2 CI/CD | 流水线构建推送 | ✅ workflow 跑通，验收截图与报告已补 |
| 附加题 3 C-1 | DDP 代码与报告 | 🔶 代码完成，报告与云端日志待补 |
| 报告主笔 | ch01~ch08 + 排版 | ✅ 主体完成，附加题专章待补 |
| 附加题 1 监控 | Pull 原理与指标说明 | ❌ 待写 |

---

## 下一步（按优先级）

1. **编译并通读 PDF**：在项目根目录执行两遍 `xelatex`，检查交叉引用、中文截图路径与目录页码。
2. **CI/CD 跑通**：触发 workflow，将 5 张验收截图补入 `figures_A/C2_CICD/` 并在 ch04sup 中引用（可选插图）。
3. **C-1 云端日志**：在 CCE 运行单机 Job 与 PyTorchJob，将 `training_time_seconds` 截图补入正文。
4. **与 A 核对分工表述**：ch01 分工表与答辩口径一致（T6 压测实际执行人、SWR 组织名 `cloud-course-a` vs `xinchunli`）。
5. **可选**：请 A 审阅 ch07 K8s YAML 摘录与 ch05 问题描述是否与实际排错一致。

---

## 仓库关键路径（B 常改）

```text
backend/          frontend/         docker-compose.yml
spark/analysis.py spark/wordcount.py
extra/c1_ddp_mnist.py
.github/workflows/cicd-app-to-swr-cce.yml
chapters/ch01~ch08*.tex
【云计算课设】2023116052_李欣纯、2023115271_郑瑞璟.tex
figures_B/A1|A2|A3/   assets/report_figures/
```
