# 附加题 2 CI/CD 云端部署验证说明

## 1. 任务目标

根据《课程设计任务书-final.pdf》中附加题 2 的要求，本部分为第一部分 Web 应用搭建 CI/CD 验证流程，完成“代码提交 -> 自动构建镜像 -> 推送 SWR -> 更新 K8s Deployment”的云端验证，并补充 CI/CD、持续部署与 GitOps 的概念说明。

## 2. 环境文件

本次使用的 CI/CD workflow 文件为：

```text
.github/workflows/cicd-app-to-swr-cce.yml
```

该 workflow 在 GitHub Actions 中自动构建 `backend/` 和 `frontend/` 镜像，并推送到成员 A 的华为云 SWR 组织 `cloud-course-a`。镜像 Tag 使用当前提交 SHA 的前 7 位，本次成功推送和部署验证使用的 Tag 为：

```text
b7817d3
```

Kubernetes 运行环境仍使用仓库中的 `k8s/` 目录，包括 backend/frontend Deployment、Redis、Service、ConfigMap、Secret、PVC 和 HPA 等配置文件。

## 3. GitHub Secrets

GitHub Actions 中只保存 SWR 登录所需的 Secret：

| Secret 名称 | 作用 |
|---|---|
| `SWR_USERNAME` | 成员 A 的华为云 SWR 登录用户名 |
| `SWR_PASSWORD` | 成员 A 的华为云 SWR 登录密码或临时登录密钥 |

SWR 登录命令、AK/SK、kubeconfig、证书和私钥均不提交到仓库，也不放入报告截图。

## 4. 流水线与部署过程

workflow 的主要阶段如下：

1. Checkout repository：拉取仓库代码。
2. Compute image tag：生成镜像 Tag。
3. Login to Huawei SWR：登录华为云 SWR。
4. Build backend image：构建后端镜像。
5. Build frontend image：构建前端镜像。
6. Push backend image：推送 `backend:b7817d3`。
7. Push frontend image：推送 `frontend:b7817d3`。
8. Show pushed image tags：输出本次推送的完整镜像地址。

由于 GitHub hosted runner 无法直接复用华为云 CloudShell 的非标准私钥文件访问 CCE，最终采用“Actions 自动构建并推送 SWR，CloudShell 使用同一镜像 Tag 更新 Deployment”的方式完成部署验证。CloudShell 中执行的核心命令为：

```bash
kubectl set image deployment/backend backend=swr.cn-north-4.myhuaweicloud.com/cloud-course-a/backend:b7817d3
kubectl set image deployment/frontend frontend=swr.cn-north-4.myhuaweicloud.com/cloud-course-a/frontend:b7817d3
kubectl rollout status deployment/backend
kubectl rollout status deployment/frontend
kubectl get deploy backend frontend -o wide
kubectl get pods -l app=backend -o wide
kubectl get pods -l app=frontend -o wide
kubectl get pods -l app=redis -o wide
```

## 5. 验收截图

本目录中的核心验收截图如下：

| 文件名 | 说明 |
|---|---|
| `01_acceptance_cicd_pipeline_passed.png` | GitHub Actions workflow 运行成功，构建和推送阶段均为绿色。 |
| `02_acceptance_swr_backend_image_tag_updated.png` | SWR 中 `backend` 镜像存在 `b7817d3` Tag。 |
| `03_acceptance_swr_frontend_image_tag_updated.png` | SWR 中 `frontend` 镜像存在 `b7817d3` Tag。 |
| `04_acceptance_k8s_deployment_image_tag_updated.png` | backend/frontend Deployment 均已更新到 `b7817d3` 镜像。 |
| `05_updated_pods_recreated_running.png` | 更新后的 backend、frontend 和 redis Pod 均处于 Running。 |
| `06_updated_api_access_ok.png` | 通过 backend Pod 访问本地接口和 `backend-svc` 均返回 `{"redis":"connected","status":"ok"}`。 |

## 6. 问题记录

初始方案尝试让 GitHub Actions 在 hosted runner 中直接执行 `kubectl set image` 更新 CCE Deployment。排查过程中遇到两个问题：

- CloudShell kubeconfig 依赖本地证书与私钥文件，且私钥文件不是 GitHub runner 可直接解析的标准 PEM 格式，导致 `tls: failed to find any PEM data in key input`。
- 原始 kubeconfig 默认使用 CCE 内网 API Server 地址，GitHub hosted runner 无法访问该内网地址。

为保证流程稳定可复现，最终将 GitHub Actions 职责收敛为自动构建并推送 backend/frontend 镜像到 SWR，再在华为云 CloudShell 中使用同一镜像 Tag 更新 Deployment 并截图验证。

此外，更新后曾在 CloudShell 中直接访问 `backend-svc` 的 ClusterIP，出现连接超时。该现象记录在 `07_issue_backend_service_timeout_after_update.png` 中。后续通过 `kubectl exec deploy/backend` 从集群内访问 `backend-svc/api/ping`，返回 `{"redis":"connected","status":"ok"}`，证明 Service 和后端接口正常，对应截图为 `08_fix_backend_service_access_from_pod_ok.png`。

## 7. 概念说明

持续集成（CI）强调代码提交后自动执行构建、测试和镜像制作，尽早发现代码或依赖问题。本项目中，GitHub Actions 自动构建 backend/frontend 镜像并推送 SWR，属于 CI 的核心环节。

持续部署（CD）强调在 CI 成功后将新版本发布到目标环境。本项目中，使用 Actions 产出的镜像 Tag 在 CCE 中更新 Deployment，并完成 Pod Running 与接口访问验证，体现了部署链路的闭环。

GitOps 的核心理念是以 Git 仓库作为系统期望状态的唯一来源，通过自动化控制器或流水线将仓库中的配置同步到集群。若进一步改造本项目，可使用 Argo CD 或 Flux 监听仓库中 Deployment YAML 的镜像 Tag 变化，由集群侧控制器自动完成同步。
