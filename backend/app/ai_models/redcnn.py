import torch
from torch import nn


class REDCNN(nn.Module):
    """Residual Encoder-Decoder CNN for low-dose CT denoising.

    This mirrors the RED-CNN architecture from `E:\RED-CNN-master\networks.py`.
    The original file uses `nn.Conv2D`, which is corrected here to PyTorch's
    `nn.Conv2d`.
    """

    def __init__(self, out_channels: int = 96) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(1, out_channels, kernel_size=5, stride=1, padding=0)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=5, stride=1, padding=0)
        self.conv3 = nn.Conv2d(out_channels, out_channels, kernel_size=5, stride=1, padding=0)
        self.conv4 = nn.Conv2d(out_channels, out_channels, kernel_size=5, stride=1, padding=0)
        self.conv5 = nn.Conv2d(out_channels, out_channels, kernel_size=5, stride=1, padding=0)

        self.tconv1 = nn.ConvTranspose2d(out_channels, out_channels, kernel_size=5, stride=1, padding=0)
        self.tconv2 = nn.ConvTranspose2d(out_channels, out_channels, kernel_size=5, stride=1, padding=0)
        self.tconv3 = nn.ConvTranspose2d(out_channels, out_channels, kernel_size=5, stride=1, padding=0)
        self.tconv4 = nn.ConvTranspose2d(out_channels, out_channels, kernel_size=5, stride=1, padding=0)
        self.tconv5 = nn.ConvTranspose2d(out_channels, 1, kernel_size=5, stride=1, padding=0)

        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual_1 = x
        out = self.relu(self.conv1(x))
        out = self.relu(self.conv2(out))
        residual_2 = out
        out = self.relu(self.conv3(out))
        out = self.relu(self.conv4(out))
        residual_3 = out
        out = self.relu(self.conv5(out))

        out = self.tconv1(out)
        out += residual_3
        out = self.tconv2(self.relu(out))
        out = self.tconv3(self.relu(out))
        out += residual_2
        out = self.tconv4(self.relu(out))
        out = self.tconv5(self.relu(out))
        out += residual_1
        out = self.relu(out)
        return out
