# 成员A进度清单

## 总体进度

| 状态 | 任务 | 当前进度 |
|---|---|---|
| [x] | T2 CCE 集群搭建 | 已完成，已提交 `figures_A/T2` 截图和说明。 |
| [x] | T3 应用部署 | 已完成，已提交 `figures_A/T3` 截图和说明。 |
| [x] | T4 Redis 持久化存储 | 已完成，已提交 `figures_A/T4` 截图。 |
| [ ] | T5 ConfigMap Volume 挂载 | 未开始。 |
| [ ] | T6 HPA 弹性伸缩 | 未开始。 |
| [ ] | A-0 Spark Operator 环境部署 | 未开始。 |
| [ ] | 附加题 1 Prometheus + Grafana 监控系统 | 未开始。 |
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

- [ ] 创建或检查 Nginx ConfigMap。
- [ ] 修改前端 Deployment，将 ConfigMap 以 Volume 形式挂载到 `/etc/nginx/conf.d/default.conf`。
- [ ] 执行 `kubectl exec` 查看前端 Pod 内 Nginx 配置文件。
- [ ] 修改 ConfigMap 中的端口或配置内容。
- [ ] 重新 `kubectl apply`。
- [ ] 再次 exec 验证配置文件已更新。
- [ ] 保存 T5 截图到 `figures_A/T5/`。
- [ ] 编写 `figures_A/T5/T5说明.md`。
- [ ] 提交 T5 截图和说明。

## T6 HPA 弹性伸缩

- [ ] 确认 metrics-server 可用，执行 `kubectl top nodes`。
- [ ] 创建 backend HPA。
- [ ] 执行 `kubectl get hpa`，确认 HPA 参数正确。
- [ ] 配合 B 同学发起压测。
- [ ] 观察 Pod 从 1 个扩容到 2 个或更多。
- [ ] 停止压测后观察 Pod 缩回 1 个。
- [ ] 保存 T6 截图到 `figures_A/T6/`。
- [ ] 编写 `figures_A/T6/T6说明.md`。
- [ ] 提交 T6 截图和说明。

## A-0 Spark Operator 环境部署

- [ ] 获取或确认 Spark Operator 安装方式。
- [ ] 安装 Spark Operator。
- [ ] 检查 `spark/sparkapplication.yaml` 的镜像地址和 executor 参数。
- [ ] 提交 SparkApplication。
- [ ] 执行 `kubectl get pods`，确认 Driver 和 Executor Pod。
- [ ] 查看 Driver 日志，确认作业完成。
- [ ] 保存 A-0 截图到 `figures_A/A0/`。
- [ ] 编写 `figures_A/A0/A0说明.md`。
- [ ] 提交 A-0 截图和说明。

## 附加题 1 Prometheus + Grafana 监控系统

- [ ] 获取 kube-prometheus-stack Helm Chart 或确认安装方式。
- [ ] 部署 Prometheus 和 Grafana。
- [ ] 确认监控相关 Pod Running。
- [ ] 打开 Grafana Dashboard。
- [ ] 截图节点 CPU 利用率折线图。
- [ ] 截图 Pod 内存使用柱状图。
- [ ] 保存监控截图到 `figures_A/C1监控/`。
- [ ] 编写 `figures_A/C1监控/C1监控说明.md`。
- [ ] 提交监控截图和说明。

## 附加题 2 CI/CD 云端部署验证

- [ ] 配合 B 同学确认 CI/CD 流水线构建并推送镜像。
- [ ] 检查 SWR 镜像 Tag 已更新。
- [ ] 检查 K8s Deployment 镜像 Tag 已更新。
- [ ] 确认更新后的 Pod Running。
- [ ] 确认更新后 `/api/ping` 仍正常。
- [ ] 保存 CI/CD 云端验证截图到 `figures_A/C2_CICD/`。
- [ ] 编写 `figures_A/C2_CICD/C2_CICD说明.md`。
- [ ] 提交 CI/CD 云端验证截图和说明。

## 下一步

当前下一步是 T5 ConfigMap Volume 挂载。T4 已提前完成，后续需要在当前 frontend Deployment 基础上验证 Nginx ConfigMap 以 Volume 形式挂载到 `/etc/nginx/conf.d/default.conf`，并完成修改 ConfigMap 后进入 Pod 查看配置文件更新的验收截图。
