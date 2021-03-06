import torch
import torch.nn as nn
import torch.nn.functional as F


class ReasoningLayer(nn.Module):
    def __init__(self, n_components, n_classes, n_replicas=1, eps=1e-10):
        super(ReasoningLayer, self).__init__()
        self.n_classes = n_classes
        self.n_replicas = n_replicas
        self.eps = eps

        self.reasoning_probabilities = nn.Parameter(
            torch.rand(2, self.n_replicas, n_components, self.n_classes)
        )
        # self.reasoning_probabilities.register_hook(lambda x: x.clamp(min=0.0, max=1.0))  # noqa

    def forward(self, x):
        positive_kernel = self.reasoning_probabilities[0].clamp(0, 1)
        negative_kernel = (1-positive_kernel) * self.reasoning_probabilities[1].clamp(0, 1)

        probs = (torch.matmul(x, (positive_kernel - negative_kernel)) \
            + torch.sum(negative_kernel, 1)) \
            / torch.sum(positive_kernel + negative_kernel, 1).clamp(min=self.eps)  # noqa

        # squeeze replica dimension if it is 1.
        if self.n_replicas == 1:
            probs = probs.squeeze(0)
        else:
            raise NotImplementedError()
            # TODO: permute probs

        return probs
