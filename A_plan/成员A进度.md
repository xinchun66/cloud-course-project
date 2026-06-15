# 成员A进度清单

## 总体进度

| 状态 | 任务 | 当前进度 |
|---|---|---|
| [x] | T2 CCE 集群搭建 | 已完成，已提交 `figures_A/T2` 截图和说明。 |
| [x] | T3 应用部署 | 已完成，已提交 `figures_A/T3` 截图和说明。 |
| [x] | T4 Redis 持久化存储 | 已完成，已提交 `figures_A/T4` 截图。 |
| [x] | T5 ConfigMap Volume 挂载 | 已完成，已提交 `figures_A/T5` 截图和说明。 |
| [x] | T6 HPA 弹性伸缩 | 已完成，已提交 `figures_A/T6` 截图和说明。 |
| [x] | A-0 Spark Operator 环境部署 | 已完成，已提交 `figures_A/A-0` 截图和说明。 |
| [x] | 附加题 1 Prometheus + Grafana 监控系统 | 已完成，已提交 `figures_A/附加题1` 截图和说明。 |
| [ ] | 附加题 2 CI/CD 云端部署验证 | 未开始。 |

## T2 CCE 集群搭建

- [x] 确认华为云代金券到账。
- [x] 选择区域：华北-北京四。
- [x] 创建 CCE Standard 集群 `cloud-course-cce`。
- [x] 使用按需计费模式。
- [x] 创建 VPC：`cloud-course-vpc`。
- [x] 创建子网：`cloud-course-subnet`。
- [x] 集群版本选择 v1.34。
- [x] 创建 2 个 Worker 节点。
- [x] Worker 节点规格为 `c9.large.2`，2 vCPUs / 4 GiB。
- [x] Worker 节点系统为 Ubuntu 22.04。
- [x] 通过 CloudShell 配置 kubectl。
- [x] 执行 `kubectl get nodes -o wide`，两个 Worker 节点均为 Ready。
- [x] 保存 T2 截图到 `figures_A/T2/`。
- [x] 编写 `figures_A/T2/T2说明.md`。
- [x] 提交 T2 截图和说明。

## T3 应用部署

- [x] 确认 SWR 中存在后端镜像：`swr.cn-north-4.myhuaweicloud.com/cloud-course-a/backend:v1`。
- [x] 确认 SWR 中存在前端镜像：`swr.cn-north-4.myhuaweicloud.com/cloud-course-a/frontend:v1`。
- [x] 检查并准备 `k8s/backend-config.yaml`。
- [x] 检查并准备 `k8s/redis-secret.yaml`。
- [x] 检查并准备 `k8s/redis-deployment.yaml`。
- [x] 检查并准备 `k8s/backend-deployment.yaml`，镜像地址已切换到 `cloud-course-a/backend:v1`。
- [x] 检查并准备 `k8s/frontend-deployment.yaml`，镜像地址已切换到 `cloud-course-a/frontend:v1`。
- [x] 检查并准备 `k8s/frontend-nginx-config.yaml`。
- [x] 检查并准备 `k8s/services.yaml`。
- [x] 执行 `kubectl apply` 部署 ConfigMap、Secret、Redis、Backend、Service。
- [x] 执行 `kubectl get pods`，确认所有 Pod Running。
- [x] 执行 `kubectl get svc`，确认 backend Service 获得 ELB 公网 IP。
- [x] 访问 `/api/ping`，确认返回 `{"redis":"connected","status":"ok"}`。
- [x] 保存 T3 截图到 `figures_A/T3/`。
- [x] 编写 `figures_A/T3/T3说明.md`。
- [x] 提交 T3 截图和说明。

说明：T3 部署过程中遇到两个问题：一是 backend/frontend 私有 SWR 镜像拉取时出现 `401 Unauthorized`，通过为 Deployment 绑定 `default-secret` 解决；二是 `backend-svc` 的 `LoadBalancer` 外部 IP 长时间 `<pending>`，通过创建共享型公网 ELB 并为 Service 添加 `kubernetes.io/elb.id` 注解解决。T3 核心验收截图已保存：

```text
figures_A/T3/02_【验收】Pod全部Running状态.png
figures_A/T3/05_【验收】浏览器访问api_ping返回ok.png
figures_A/T3/06_【验收】curl访问api_ping返回ok.png
```

## T4 Redis 持久化存储

- [x] 创建 Redis PVC。
- [x] 修改 Redis Deployment，将 PVC 挂载到 `/data`。
- [x] 执行 `kubectl get pvc`，确认 PVC Bound。
- [x] 向 Redis 写入 `testkey = hello`。
- [x] 删除 Redis Pod 触发重建。
- [x] 重建后查询 `testkey`，确认仍返回 `hello`。
- [x] 保存 T4 截图到 `figures_A/T4/`。
- [x] 编写 `figures_A/T4/T4说明.md`。
- [x] 提交 T4 截图和说明。

说明：由于 T3 仍在等待 B 同学将 backend/frontend 镜像推送到 A 同学的 SWR 组织 `cloud-course-a`，先完成了不依赖业务镜像的 Redis PVC 持久化验证。T4 核心验收截图已保存：

```text
figures_A/T4/01_【验收】RedisPVC绑定Bound状态.png
figures_A/T4/03_【验收】Redis写入testkey成功.png
figures_A/T4/04_【验收】删除RedisPod触发重建.png
figures_A/T4/06_【验收】重建后查询testkey仍返回hello.png
```

## T5 ConfigMap Volume 挂载

- [x] 创建或检查 Nginx ConfigMap。
- [x] 修改前端 Deployment，将 ConfigMap 以 Volume 形式挂载到 `/etc/nginx/conf.d/default.conf`。
- [x] 执行 `kubectl exec` 查看前端 Pod 内 Nginx 配置文件。
- [x] 修改 ConfigMap 中的配置内容，加入 `# T5 ConfigMap volume update verified` 验证标记。
- [x] 重新 `kubectl apply`。
- [x] 再次 exec 验证配置文件已更新。
- [x] 保存 T5 截图到 `figures_A/T5/`。
- [x] 编写 `figures_A/T5/T5说明.md`。
- [x] 提交 T5 截图和说明。

说明：frontend Deployment 使用 `frontend-nginx-config` 作为 ConfigMap Volume，并挂载到 `/etc/nginx/conf.d/default.conf`。由于当前挂载方式使用 `subPath`，修改 ConfigMap 后通过 `kubectl rollout restart deployment frontend` 触发新 Pod 重新挂载配置。T5 核心验收截图已保存：

```text
figures_A/T5/05_【验收】修改后exec验证配置文件已更新.png
```

## T6 HPA 弹性伸缩

- [x] 确认 metrics-server 可用，执行 `kubectl top nodes`。
- [x] 创建 backend HPA。
- [x] 执行 `kubectl get hpa`，确认 HPA 参数正确。
- [x] 使用 curl 循环脚本发起压测。
- [x] 观察 Pod 从 1 个扩容到 4 个。
- [x] 停止压测后观察 Pod 自然缩回 1 个。
- [x] 恢复 HPA 标准配置：`minReplicas=1`、`maxReplicas=4`、CPU 目标 `60%`。
- [x] 保存 T6 截图到 `figures_A/T6/`。
- [x] 编写 `figures_A/T6/T6说明.md`。
- [x] 提交 T6 截图和说明。

说明：T6 中先安装并验证 Kubernetes Metrics Server，随后创建 `backend-hpa`，参数为 `minReplicas=1`、`maxReplicas=4`、CPU 目标 `60%`。由于 CloudShell 未安装 `ab`，使用 curl 循环脚本访问 `http://1.92.151.224/api/ping` 进行压测，HPA 成功将 backend Pod 从 1 个扩容到 4 个。停止压测时发现后台 `while true curl` 任务仍在持续产生请求，清理全部后台任务后，CPU 下降到目标值以下，HPA 自然缩容回 1 个 Pod。最终已删除并重新应用 `k8s/backend-hpa.yaml`，确保云上 HPA 配置恢复为任务书模板。T6 核心验收截图已保存：

```text
figures_A/T6/06_【验收】Pod数量从1扩容到2或更多.png
figures_A/T6/08_【验收】Pod数量缩回1个.png
```

## A-0 Spark Operator 环境部署

- [x] 获取或确认 Spark Operator 安装方式。
- [x] 安装 Spark Operator。
- [x] 检查 `sparkapplication-a0.yaml` 的镜像地址和 executor 参数。
- [x] 提交 SparkApplication。
- [x] 执行 `kubectl get pods`，确认 Driver 和两个 Executor Pod。
- [x] 查看 Driver 日志，确认 WordCount 作业完成。
- [x] 保存 A-0 截图到 `figures_A/A-0/`。
- [x] 编写 `figures_A/A-0/A0说明.md`。
- [x] 提交 A-0 截图和说明。

说明：A-0 中先完成 Spark Operator 部署。由于默认 Operator 镜像 `ghcr.io/kubeflow/spark-operator/controller:2.5.0` 拉取失败，将 `spark-operator-controller` 和 `spark-operator-webhook` 两个 Deployment 镜像切换为成员 A 的 SWR 镜像 `swr.cn-north-4.myhuaweicloud.com/cloud-course-a/spark-operator-controller:2.5.0`，并复制、绑定 `default-secret` 作为镜像拉取密钥，最终两个 Operator Pod 均为 `1/1 Running`。

随后使用成员 B 提供的 PySpark 镜像 `swr.cn-north-4.myhuaweicloud.com/xinchunli/pyspark:3.5.4-a3` 提交 WordCount 示例作业，`mainApplicationFile` 为 `local:///opt/spark/work/wordcount.py`，`sparkVersion` 为 `3.5.4`，`executor.instances=2`，`driver/executor memory=1g`。调试过程中曾遇到镜像缺少脚本、Driver 内存设置过低以及原 2 个 `c9.large.2` 节点资源不足导致 Executor Pending 等问题。最终新增 2 个 `c9.large.4` Worker 节点后，Driver 和两个 Executor 均成功运行并进入 `Completed` 状态。

A-0 核心验收截图已保存：

```text
figures_A/A-0/01_SparkOperator命名空间和Pod状态.png
figures_A/A-0/02_SparkApplicationYAML关键参数.png
figures_A/A-0/03_提交SparkApplication成功.png
figures_A/A-0/04_【验收】Driver和两个Executor完成状态_watch.png
figures_A/A-0/05_SparkDriver日志输出.png
figures_A/A-0/06_SparkApplication完成状态.png
```

## 附加题 1 Prometheus + Grafana 监控系统

- [x] 获取 kube-prometheus-stack Helm Chart 或确认安装方式。
- [x] 部署 Prometheus 和 Grafana/CCE 云原生监控组件。
- [x] 确认监控相关 Pod Running。
- [x] 打开 CCE 云原生观测监控面板。
- [x] 截图节点 CPU 利用率折线图。
- [x] 截图 Pod/工作负载内存使用图。
- [x] 保存监控截图到 `figures_A/附加题1/`。
- [x] 编写 `figures_A/附加题1/C1监控说明.md`。
- [x] 提交监控截图和说明。

说明：附加题 1 使用 CCE 云原生监控插件 `kube-prometheus-stack` 完成。监控相关 Pod 均位于 `monitoring` 命名空间，`alertmanager`、`custom-metrics-apiserver`、`kube-state-metrics`、`node-exporter`、`prometheus-operator` 和 `prometheus-server` 均为 `Running`；`prometheus-server` Service 和 `pvc-prometheus-server-0` PVC 已创建，Prometheus 可通过 `kubectl port-forward -n monitoring svc/prometheus-server 9090:9090` 访问。

当前截图已覆盖任务书附加题 1 的核心要求：`08_集群CPU和内存监控分析图.png` 展示集群 CPU 和内存时间趋势，`09_backend工作负载CPU内存监控图.png` 展示 backend 工作负载 CPU、内存、磁盘和网络指标。`C1监控说明.md` 已补充 Prometheus Pull 采集原理，以及 CPU 使用率、内存使用率、CPU 分配率、内存分配率、网络上下行速率等指标含义。

## 附加题 2 CI/CD 云端部署验证

- [x] 准备 GitHub Actions CI/CD workflow 环境文件。
- [x] 编写 CI/CD 验证说明和截图清单。
- [ ] 配合 B 同学确认 CI/CD 流水线构建并推送镜像。
- [ ] 检查 SWR 镜像 Tag 已更新。
- [ ] 检查 K8s Deployment 镜像 Tag 已更新。
- [ ] 确认更新后的 Pod Running。
- [ ] 确认更新后 `/api/ping` 仍正常。
- [ ] 保存 CI/CD 云端验证截图到 `figures_A/C2_CICD/`。
- [ ] 编写 `figures_A/C2_CICD/C2_CICD说明.md`。
- [ ] 提交 CI/CD 云端验证截图和说明。

说明：已补充 `.github/workflows/cicd-app-to-swr-cce.yml`，用于对第一部分 backend/frontend 应用执行“代码提交 -> 自动构建镜像 -> 推送成员 A 的 SWR -> 更新 CCE 中 backend/frontend Deployment”的端到端流程。该 workflow 依赖 GitHub Secrets：`SWR_USERNAME`、`SWR_PASSWORD` 和 `CCE_KUBE_CONFIG_B64`，不会在仓库中保存明文账号、AK/SK 或 kubeconfig。

已在 `figures_A/C2_CICD/C2_CICD说明.md` 中整理 workflow 阶段、所需环境文件、Secrets 配置、验收截图清单，以及 CI/CD 与 GitOps 概念说明。下一步需要配置 Secrets 并运行 GitHub Actions，运行成功后补充流水线 Passed、SWR 新 Tag、Deployment 新镜像、Pod Running 和接口访问正常截图。

## 下一步

当前下一步是附加题 2 CI/CD 云端部署验证。附加题 1 Prometheus + Grafana/CCE 云原生监控系统已完成截图整理和说明文档补充。
