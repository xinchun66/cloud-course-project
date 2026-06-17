# -*- coding: utf-8 -*-
"""为报告截图添加轻量红框与中文标签，输出 *_annot.png 副本。"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]

# 相对坐标 (0~1)：x1, y1, x2, y2
# label_pos: above（默认）| below | inside
ANNOTATIONS: dict[str, list[dict]] = {
    "figures_B/T1/t1-12-curl-ping-json.png": [
        {"box": (0.02, 0.52, 0.98, 0.88), "label": "验收：status ok + redis connected"},
    ],
    "figures_B/T1/t1-18-frontend-page-student-id.png": [
        {"box": (0.01, 0.04, 0.42, 0.13), "label": "本地 8080 端口"},
        {"box": (0.02, 0.18, 0.38, 0.42), "label": "姓名与学号展示"},
    ],
    "figures_B/T1/t1-11-compose-ps-running.png": [
        {"box": (0.02, 0.45, 0.98, 0.92), "label": "backend / redis 均为 Up"},
    ],
    "figures_B/T1/t1-10-compose-up-build.png": [
        {"box": (0.02, 0.55, 0.98, 0.95), "label": "compose 构建并启动成功"},
    ],
    "figures_B/T1/t1-13-backend-logs.png": [
        {"box": (0.02, 0.55, 0.98, 0.92), "label": "HTTP 200 请求日志"},
    ],
    "figures_B/T1/t1-14-docker-images.png": [
        {"box": (0.02, 0.35, 0.98, 0.75), "label": "backend / frontend 本地镜像"},
    ],
    "figures_B/T1/t1-15-frontend-build-success.png": [
        {"box": (0.02, 0.70, 0.98, 0.95), "label": "frontend:v1 构建成功"},
    ],
    # ── 附加题 2 ──
    "figures_B/附加题2/01_CICD_GitHubSecrets_已配置.png": [
        {"box": (0.02, 0.06, 0.52, 0.94), "label": "SWR Secrets 已配置", "label_pos": "below"},
    ],
    "figures_B/附加题2/02_CICD_PushBackendImage_日志.png": [
        {"box": (0.21, 0.14, 0.98, 0.22), "label": "Push backend image 步骤"},
        {"box": (0.22, 0.23, 0.98, 0.31), "label": "docker push 命令"},
        {"box": (0.22, 0.90, 0.98, 0.99), "label": "digest 推送完成", "label_pos": "above"},
    ],
    "figures_B/附加题2/03_CICD_PushFrontendImage_日志.png": [
        {"box": (0.21, 0.14, 0.98, 0.22), "label": "Push frontend image 步骤"},
        {"box": (0.22, 0.23, 0.98, 0.31), "label": "docker push 命令"},
        {"box": (0.22, 0.90, 0.98, 0.99), "label": "digest 推送完成", "label_pos": "above"},
    ],
    "figures_A/附加题2/01_acceptance_cicd_pipeline_passed.png": [
        {"box": (0.02, 0.43, 0.12, 0.49), "label": "build-push Passed"},
        {"box": (0.36, 0.12, 0.44, 0.16), "label": "Status: Success"},
        {"box": (0.26, 0.68, 0.44, 0.80), "label": "作业 55s 完成"},
    ],
    "figures_A/附加题2/02_acceptance_swr_backend_image_tag_updated.png": [
        {"box": (0.05, 0.833, 0.93, 0.848), "label": "镜像版本 b7817d3 + pull 命令", "label_pos": "above"},
    ],
    "figures_A/附加题2/03_acceptance_swr_frontend_image_tag_updated.png": [
        {"box": (0.05, 0.833, 0.93, 0.848), "label": "镜像版本 b7817d3 + pull 命令", "label_pos": "above"},
    ],
    "figures_A/附加题2/04_acceptance_k8s_deployment_image_tag_updated.png": [
        {"box": (0.55, 0.52, 0.98, 0.72), "label": "backend Tag b7817d3", "label_pos": "above"},
        {"box": (0.55, 0.72, 0.98, 0.94), "label": "frontend Tag b7817d3", "label_pos": "above"},
    ],
    "figures_A/附加题2/05_updated_pods_recreated_running.png": [
        {"box": (0.36, 0.26, 0.46, 0.34), "label": "backend Running"},
        {"box": (0.46, 0.26, 0.56, 0.34), "label": "AGE ~3m", "label_pos": "below"},
        {"box": (0.36, 0.46, 0.46, 0.54), "label": "frontend Running"},
        {"box": (0.36, 0.66, 0.46, 0.74), "label": "redis Running"},
    ],
    "figures_A/附加题2/06_updated_api_access_ok.png": [
        {"box": (0.01, 0.36, 0.58, 0.54), "label": "127.0.0.1 /api/ping ok"},
        {"box": (0.01, 0.74, 0.58, 0.96), "label": "backend-svc /api/ping ok"},
    ],
    # ── 附加题 1 ──
    "figures_A/附加题1/04_monitoring_pods_running.png": [
        {"box": (0.01, 0.12, 0.98, 0.44), "label": "monitoring 命名空间 Pod 列表"},
        {"box": (0.43, 0.17, 0.56, 0.42), "label": "全部 Running"},
    ],
    "figures_A/附加题1/08_cluster_cpu_memory_monitoring.png": [
        {"box": (0.04, 0.30, 0.49, 0.86), "label": "CPU 分配率 / 使用率"},
        {"box": (0.51, 0.30, 0.96, 0.86), "label": "内存 分配率 / 使用率"},
    ],
    "figures_A/附加题1/09_backend_workload_cpu_memory_monitoring.png": [
        {"box": (0.05, 0.40, 0.27, 0.70), "label": "CPU 使用率 0.10%"},
        {"box": (0.30, 0.40, 0.52, 0.70), "label": "内存 5.37%"},
        {"box": (0.54, 0.72, 0.96, 0.92), "label": "磁盘 / 网络 I/O", "label_pos": "above"},
    ],
    # ── 附加题 3 C-1 ──
    "figures/c1-single-node-mnist-result.png": [
        {"box": (0.01, 0.66, 0.42, 0.78), "label": "epoch loss 输出"},
        {"box": (0.01, 0.80, 0.98, 0.96), "label": "train_seconds=59.05 acc=0.9842", "label_pos": "above"},
    ],
    "figures/c1-distributed-ddp-mnist-result.png": [
        {"box": (0.01, 0.05, 0.98, 0.95), "label": "DDP 35.64s acc=0.9798", "label_pos": "below"},
    ],
    "figures_B/附加题3/01_single_job_pod_running.png": [
        {"box": (0.01, 0.14, 0.98, 0.82), "label": "kubectl get pods 输出"},
        {"box": (0.36, 0.30, 0.56, 0.50), "label": "mnist-single Pod 状态"},
    ],
    "figures_B/A2/a2-query4-window-function.png": [
        {"box": (0.02, 0.45, 0.98, 0.92), "label": "窗口函数排名结果"},
    ],
}

FONT_CANDIDATES = [
    Path(r"C:/Windows/Fonts/msyh.ttc"),
    Path(r"C:/Windows/Fonts/msyhbd.ttc"),
    Path(r"C:/Windows/Fonts/simhei.ttf"),
    Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def draw_annotation(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    label: str,
    width: int,
    height: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    label_pos: str = "above",
) -> None:
    x1 = int(box[0] * width)
    y1 = int(box[1] * height)
    x2 = int(box[2] * width)
    y2 = int(box[3] * height)
    color = (220, 38, 38)
    draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 4
    tx = max(min(x1, width - tw - pad * 2 - 4), 4)

    if label_pos == "below":
        ty = min(y2 + pad, height - th - pad * 2 - 4)
    elif label_pos == "inside":
        ty = y1 + pad
    else:  # above
        ty = max(y1 - th - pad * 2, 4)
        if ty + th + pad * 2 > y1 and y1 < th + pad * 4:
            ty = min(y2 + pad, height - th - pad * 2 - 4)

    draw.rectangle([tx, ty, tx + tw + pad * 2, ty + th + pad * 2], fill=(255, 255, 255))
    draw.rectangle([tx, ty, tx + tw + pad * 2, ty + th + pad * 2], outline=color, width=2)
    draw.text((tx + pad, ty + pad), label, fill=color, font=font)


def annotate_file(src: Path, items: list[dict], dst: Path) -> None:
    img = Image.open(src).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    font_size = max(12, min(20, w // 60))
    if h < 120:
        font_size = max(10, min(14, h // 4))
    font = load_font(font_size)
    for item in items:
        draw_annotation(
            draw,
            tuple(item["box"]),
            item["label"],
            w,
            h,
            font,
            item.get("label_pos", "above"),
        )
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, format="PNG", optimize=True)


def main() -> None:
    manifest: list[dict] = []
    for rel, items in ANNOTATIONS.items():
        src = ROOT / Path(rel)
        if not src.exists():
            print(f"skip missing: {rel}")
            continue
        dst = src.with_name(f"{src.stem}_annot{src.suffix}")
        annotate_file(src, items, dst)
        manifest.append({"source": rel, "annotated": dst.relative_to(ROOT).as_posix()})
        print(f"annotated: {rel} -> {dst.name}")

    manifest_path = ROOT / "scripts" / "annotated_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"done: {len(manifest)} files")


if __name__ == "__main__":
    main()
