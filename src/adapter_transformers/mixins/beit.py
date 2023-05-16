from typing import Iterable, Tuple

import torch.nn as nn

from ..layer import AdapterLayer
from ..lora import Linear as LoRALinear
from ..model_mixin import ModelBaseAdaptersMixin
from ..prefix_tuning import PrefixTuningShim


class BeitSelfAttentionAdaptersMixin:
    def init_adapters(self, config):
        self.location_key = "self"

        # Wrap layers for LoRA
        self.query = LoRALinear.wrap(self.query, "selfattn", config, attn_key="q")
        self.key = LoRALinear.wrap(self.key, "selfattn", config, attn_key="k")
        self.value = LoRALinear.wrap(self.value, "selfattn", config, attn_key="v")

        self.prefix_tuning = PrefixTuningShim(self.location_key + "_prefix" if self.location_key else None, config)


class BeitIntermediateAdaptersMixin:
    def init_adapters(self, config):
        # Wrap layers for LoRA
        self.dense = LoRALinear.wrap(self.dense, "intermediate", config)


class BeitOutputAdaptersMixin:
    def init_adapters(self, config):
        # Wrap layers for LoRA
        self.dense = LoRALinear.wrap(self.dense, "output", config)


class BeitLayerAdaptersMixin:
    """Adds adapters to the BeitLayer module."""

    def init_adapters(self, config):
        self.attention_adapters = AdapterLayer("mh_adapter")
        self.output_adapters = AdapterLayer("output_adapter")


class BeitModelAdaptersMixin(ModelBaseAdaptersMixin):
    """Adds adapters to the BeitModel module."""

    def init_adapters(self, config):
        super().init_adapters(config)

    def iter_layers(self) -> Iterable[Tuple[int, nn.Module]]:
        for i, layer in enumerate(self.encoder.layer):
            yield i, layer

    def set_input_embeddings(self, value):
        self.embeddings.patch_embeddings = value
