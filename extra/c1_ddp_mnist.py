import argparse
import os
import time

import torch
import torch.distributed as dist
import torch.nn as nn
import torch.optim as optim
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
from torchvision import datasets, transforms


class MnistCnn(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128),
            nn.ReLU(),
            nn.Linear(128, 10),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def parse_args():
    parser = argparse.ArgumentParser(description="MNIST CNN with optional PyTorch DDP")
    parser.add_argument("--data-dir", default="/data/mnist")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--download", action="store_true")
    return parser.parse_args()


def setup_distributed():
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    distributed = world_size > 1

    if distributed:
        dist.init_process_group(backend="gloo", init_method="env://")
        rank = dist.get_rank()
        local_rank = int(os.environ.get("LOCAL_RANK", "0"))
    else:
        rank = 0
        local_rank = 0

    return distributed, rank, local_rank, world_size


def cleanup_distributed(distributed):
    if distributed:
        dist.destroy_process_group()


def build_loaders(args, distributed, rank, world_size):
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,)),
        ]
    )

    train_dataset = datasets.MNIST(
        args.data_dir, train=True, transform=transform, download=args.download
    )
    test_dataset = datasets.MNIST(
        args.data_dir, train=False, transform=transform, download=args.download
    )

    train_sampler = (
        DistributedSampler(
            train_dataset, num_replicas=world_size, rank=rank, shuffle=True
        )
        if distributed
        else None
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=train_sampler is None,
        sampler=train_sampler,
        num_workers=2,
        pin_memory=False,
    )
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, num_workers=2)

    return train_loader, test_loader, train_sampler


def evaluate(model, test_loader, device):
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for data, target in test_loader:
            data = data.to(device)
            target = target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()
            total += target.numel()

    return correct / total


def main():
    args = parse_args()
    distributed, rank, local_rank, world_size = setup_distributed()
    device = torch.device("cuda", local_rank) if torch.cuda.is_available() else torch.device("cpu")

    if rank == 0:
        print(f"distributed={distributed}, world_size={world_size}, device={device}")

    train_loader, test_loader, train_sampler = build_loaders(
        args, distributed, rank, world_size
    )

    model = MnistCnn().to(device)
    if distributed:
        model = DDP(model)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=args.lr, momentum=0.9)

    start_time = time.perf_counter()
    for epoch in range(1, args.epochs + 1):
        if train_sampler is not None:
            train_sampler.set_epoch(epoch)

        model.train()
        running_loss = 0.0
        for data, target in train_loader:
            data = data.to(device)
            target = target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        if rank == 0:
            accuracy = evaluate(model.module if distributed else model, test_loader, device)
            print(
                f"epoch={epoch}, loss={running_loss / len(train_loader):.4f}, "
                f"test_accuracy={accuracy:.4f}"
            )

    elapsed = time.perf_counter() - start_time
    if rank == 0:
        print(f"training_time_seconds={elapsed:.4f}")
        print(
            "Report note: compare this value with a single-process run, then discuss "
            "AllReduce gradient synchronization and communication overhead."
        )

    cleanup_distributed(distributed)


if __name__ == "__main__":
    main()
