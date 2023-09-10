import torch
from torch import Tensor
from typing_extensions import Self


class TensorBuilder:
    tensor: Tensor = torch.empty(size=(1, 0), dtype=torch.int64)

    def build(self) -> Tensor:
        return self.tensor

    def append(self, tensor: Tensor) -> Self:
        self.tensor = torch.cat((self.tensor, tensor), dim=1)
        return self

    def append_n_times(self, tensor: Tensor, n: int) -> Self:
        for _ in range(n):
            self.append(tensor)
        return self

    def tail(self, n: int) -> Self:
        self.tensor = self.tensor[-n:]
        return self

    def remove_initial_tokens(self, n: int) -> Self:
        self.tensor = self.tensor[:, n:]
        return self

    def left_trim_to_size(self, n: int) -> Self:
        if self.tensor.size(1) > n:
            self.tensor = self.tensor[:, -n:]
        return self
