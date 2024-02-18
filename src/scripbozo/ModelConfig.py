from typing import Any
from typing import Dict


class ModelConfig:
    _config: Dict[str, Any]

    def __init__(self, config: Dict[str, Any]) -> None:
        self._config = config

    def path(self) -> str:
        return self._config.get("model_path", "model").strip(" '\"")

    def cuda_device(self) -> str:
        return self._config.get("cuda_device", "cuda:0").strip(" '\"")

    def model_max_tokens(self) -> int:
        return self._config.get("model_max_tokens", 512)

    def output_max_tokens(self) -> int:
        return self._config.get("output_max_tokens", 64)

    def generation_temperature(self) -> float:
        return self._config.get("temperature", 0.6)

    def generation_top_k(self) -> int:
        return self._config.get("top_k", 50)

    def generation_top_p(self) -> float:
        return self._config.get("top_p", 0.92)

    def generation_no_repeat_ngram_size(self) -> int:
        return self._config.get("no_repeat_ngram_size", 6)

    def generation_repetition_penalty(self) -> float:
        return self._config.get("repetition_penalty", 1.6)

    def generation_min_length(self) -> int:
        return self._config.get("min_length", 2)
