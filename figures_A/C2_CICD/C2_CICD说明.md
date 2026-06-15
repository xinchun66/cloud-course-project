# 附加题 2 CI/CD 云端部署验证说明

## 1. 任务目标

根据《课程设计任务书-final.pdf》中附加题 2 的要求，本部分需要为第一部分 Web 应用搭建流水线，实现“代码提交 -> 自动构建镜像 -> 推送 SWR”，并在 CCE 集群中更新 K8s Deployment 完成云端验证，提供流水线 Passed、SWR 镜像 Tag 更新、K8s Deployment 镜像 Tag 更新、Pod Running 和接口访问正常的截图证据。

## 2. 环境文件

本次补充的 CI/CD 环境文件为：

```text
.github/workflows/cicd-app-to-swr-cce.yml
```

该 workflow 用于构建 `backend/` 与 `frontend/` 两个镜像，并将镜像推送到成员 A 的华为云 SWR 组织 `cloud-course-a`。由于 GitHub hosted runner 无法直接复用 CloudShell 的非标准私钥文件访问 CCE，本次 CCE Deployment 更新在华为云 CloudShell 中使用同一镜像 Tag 手动执行并截图验证。

相关 Kubernetes 环境文件仍使用仓库中的 `k8s/` 目录：

```text
k8s/backend-deployment.yaml
k8s/frontend-deployment.yaml
k8s/backend-config.yaml
k8s/redis-secret.yaml
k8s/redis-deployment.yaml
k8s/redis-pvc.yaml
k8s/services.yaml
k8s/backend-hpa.yaml
```

这些 YAML 文件用于说明云端运行环境的 Deployment、Service、ConfigMap、Secret、PVC 和 HPA 配置。workflow 不会把敏感信息写入仓库，而是通过 GitHub Secrets 注入 SWR 登录信息。

## 3. GitHub Secrets 要求

运行 workflow 前，需要在 GitHub 仓库的 Secrets 中配置以下变量：

| Secret 名称 | 作用 |
|---|---|
| `SWR_USERNAME` | 成员 A 的华为云 SWR 登录用户名 |
| `SWR_PASSWORD` | 成员 A 的华为云 SWR 登录密码或临时登录密钥 |

安全要求：不要将 SWR 登录命令、AK/SK 或其他凭据内容提交到仓库，也不要放入截图。

## 4. 流水线步骤

workflow 的主要阶段如下：

1. Checkout repository：拉取仓库代码。
2. Compute image tag：使用当前提交 SHA 的前 7 位作为镜像 Tag。
3. Login to Huawei SWR：通过 GitHub Secrets 登录华为云 SWR。
4. Build backend image：基于 `backend/Dockerfile` 构建后端镜像。
5. Build frontend image：基于 `frontend/Dockerfile` 构建前端镜像。
6. Push backend image：推送后端镜像到 `swr.cn-north-4.myhuaweicloud.com/cloud-course-a/backend:<tag>`。
7. Push frontend image：推送前端镜像到 `swr.cn-north-4.myhuaweicloud.com/cloud-course-a/frontend:<tag>`。
8. Show pushed image tags：输出 backend/frontend 的完整镜像地址和本次提交对应的镜像 Tag，便于后续在 CloudShell 中更新 Deployment。

CloudShell 中使用 workflow 输出的 `<tag>` 执行：

```bash
kubectl set image deployment/backend backend=swr.cn-north-4.myhuaweicloud.com/cloud-course-a/backend:<tag>
kubectl set image deployment/frontend frontend=swr.cn-north-4.myhuaweicloud.com/cloud-course-a/frontend:<tag>
kubectl rollout status deployment/backend
kubectl rollout status deployment/frontend
kubectl get deploy backend frontend -o wide
kubectl get pods -o wide
```

## 5. 验收截图清单

运行完成后，需要将以下截图保存到当前目录：

```text
01_【验收】CICD流水线全部Passed.png
02_【验收】SWR镜像Tag已更新.png
03_【验收】K8sDeployment镜像Tag已更新.png
04_更新后Pod重新创建成功.png
05_更新后接口访问正常.png
```

其中：

- `01_【验收】CICD流水线全部Passed.png`：GitHub Actions 页面显示构建和推送镜像阶段全部成功。
- `02_【验收】SWR镜像Tag已更新.png`：SWR 控制台显示 `backend` 和 `frontend` 已出现本次提交对应的新 Tag。
- `03_【验收】K8sDeployment镜像Tag已更新.png`：CloudShell 中执行 `kubectl get deploy backend frontend -o wide` 或 `kubectl describe deploy`，显示 Deployment 镜像已切换到 workflow 输出的新 Tag。
- `04_更新后Pod重新创建成功.png`：`kubectl get pods -o wide` 显示更新后的 Pod 为 `Running`。
- `05_更新后接口访问正常.png`：`curl http://<ELB_IP>/api/ping` 返回正常 JSON，证明部署后服务仍可访问。

## 6. CI/CD 与 GitOps 概念说明

持续集成（CI）强调每次代码提交后自动执行构建、测试和镜像制作，尽早发现代码或依赖问题。本项目中，后端和前端镜像的自动构建属于 CI 范畴。

持续部署（CD）强调在 CI 成功后将新版本发布到目标环境。本项目中，GitHub Actions 自动将镜像推送到 SWR，随后在 CloudShell 使用同一镜像 Tag 更新 CCE Deployment，构成一次可追踪的部署验证流程。

GitOps 的核心理念是以 Git 仓库作为系统期望状态的唯一来源，通过自动化控制器或流水线将仓库中的配置同步到集群。理想的 GitOps 方式通常会把 Deployment 中的镜像 Tag 更新回 Git 仓库，再由集群侧控制器自动拉取并应用。若进一步改造成 GitOps，可引入 Argo CD 或 Flux，让集群持续对齐 Git 中声明的 YAML 状态。

## 7. 当前状态

当前已补充 CI/CD workflow 和说明文档，K8s 环境 YAML 已在仓库中。下一步需要运行 `Build App Images and Push to SWR` workflow，完成后使用输出的镜像 Tag 在 CloudShell 中更新 Deployment，补充 5 张验收截图，并同步更新 `A_plan/成员A进度.md`。
