# 云计算课程设计项目

本仓库用于云计算技术课程设计，包含应用容器化、Kubernetes 部署配置、Spark 数据分析代码，以及附加题 C-1 的 PyTorch DDP 分布式训练代码。

## 项目结构

```text
cloud-course-project/
|-- backend/                 # Flask 后端与后端 Dockerfile
|-- frontend/                # Nginx 静态前端与前端 Dockerfile
|-- spark/                   # Spark A-0/A-1/A-2/A-3 脚本和模板
|-- k8s/                     # T3/T4/T5/T6 与 C-1 的 Kubernetes 配置
|-- extra/                   # C-1 PyTorch DDP MNIST 训练代码
|-- figures/                 # 实验截图和生成的图表
|-- docker-compose.yml       # 本地 backend + Redis 联调配置
`-- douban_movies.csv        # 豆瓣电影数据集
```

## T1 应用容器化

构建后端镜像：

```powershell
docker build -t backend:v1 ./backend
```

构建前端镜像：

```powershell
docker build -t frontend:v1 ./frontend
```

本地联调：

```powershell
docker compose up -d --build
docker compose ps
curl.exe http://localhost:5000/api/ping
docker compose logs backend --tail 80
```

接口期望返回：

```json
{"redis":"connected","status":"ok"}
```

已推送到华为云 SWR 的镜像：

```text
swr.cn-north-4.myhuaweicloud.com/xinchunli/backend:v1
swr.cn-north-4.myhuaweicloud.com/xinchunli/frontend:v1
```

登录 SWR 后的推送命令：

```powershell
docker tag backend:v1 swr.cn-north-4.myhuaweicloud.com/xinchunli/backend:v1
docker tag frontend:v1 swr.cn-north-4.myhuaweicloud.com/xinchunli/frontend:v1
docker push swr.cn-north-4.myhuaweicloud.com/xinchunli/backend:v1
docker push swr.cn-north-4.myhuaweicloud.com/xinchunli/frontend:v1
```

## Kubernetes 配置

`k8s/` 目录中包含后端、Redis、前端、PVC、ConfigMap Volume 挂载和 HPA 所需的 YAML。

CCE 集群创建完成后，建议按以下顺序应用：

```bash
kubectl apply -f k8s/redis-pvc.yaml
kubectl apply -f k8s/backend-config.yaml
kubectl apply -f k8s/redis-secret.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/frontend-nginx-config.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/backend-hpa.yaml
```

常用检查命令：

```bash
kubectl get pods
kubectl get svc
kubectl get pvc
kubectl get hpa
```

T5 ConfigMap Volume 挂载相关文件：

```text
k8s/frontend-nginx-config.yaml
k8s/frontend-deployment.yaml
```

T6 HPA 弹性伸缩相关文件：

```text
k8s/backend-hpa.yaml
```

## Spark 数据分析

`spark/analysis.py` 包含以下任务代码：

- A-1 数据清洗
- A-2 Spark SQL 统计分析
- A-3 Pandas vs PySpark 性能对比与 Amdahl 分析

在本地 PySpark 环境中运行：

```bash
spark-submit spark/analysis.py douban_movies.csv
```

在 Kubernetes Spark 环境或 OBS 数据路径上运行：

```bash
spark-submit /opt/spark/work/analysis.py s3a://<BUCKET>/douban_movies.csv
```

A-2 已实现的查询：

- 按电影类型进行 `GROUP BY` 聚合
- 按评分人数 `rating_count` 进行 Top-N 排序
- 按年份统计评分趋势
- 使用窗口函数统计各国家或地区的电影排名

A-3 输出文件位于 `figures/`：

```text
figures/a3_performance_exec_1.csv
figures/a3_performance_exec_2.csv
figures/a3_amdahl_summary.csv
figures/a3_amdahl_speedup.png
```

A-3 需要分别以 `executor.instances=1` 和 `executor.instances=2` 运行一次，用于对比性能和估算 Amdahl 并行比例。

## A-0 Spark Operator 模板

相关文件：

```text
spark/sparkapplication.yaml
spark/wordcount.py
```

运行前需要替换以下占位内容：

```text
swr.cn-north-4.myhuaweicloud.com/<YOUR_ORG>/pyspark:3.4
s3a://<BUCKET>/sample.txt
```

Spark Operator 安装完成后提交任务：

```bash
kubectl apply -f spark/sparkapplication.yaml
kubectl get pods -n default
```

## 附加题 C-1 PyTorch DDP

相关文件：

```text
extra/c1_ddp_mnist.py
extra/Dockerfile.pytorch
k8s/c1-single-mnist-job.yaml
k8s/c1-pytorchjob.yaml
```

构建并推送训练镜像：

```bash
docker build -f extra/Dockerfile.pytorch -t swr.cn-north-4.myhuaweicloud.com/xinchunli/mnist-ddp:v1 extra
docker push swr.cn-north-4.myhuaweicloud.com/xinchunli/mnist-ddp:v1
```

PyTorchJob Operator 可用后，分别运行单机和分布式任务：

```bash
kubectl apply -f k8s/c1-single-mnist-job.yaml
kubectl apply -f k8s/c1-pytorchjob.yaml
```

报告中对比日志里的 `training_time_seconds`，并说明 AllReduce 梯度同步、通信开销、数据并行和模型并行的区别。

## 注意事项

- 不要提交云平台访问密钥或登录凭据。
- `credentials.csv` 只应保存在本地，不应推送到公开仓库。
- 运行到 CCE 前，需要替换所有 `<BUCKET>`、`<YOUR_ORG>` 等占位符。
