import configparser


class ModelConfig:
    _config: configparser.SectionProxy

    def __init__(self, config: configparser.SectionProxy) -> None:
        self._config = config

    def path(self) -> str:
        return self._config.get("model_path", "model")

    def cuda_device(self) -> str:
        return self._config.get("cuda_device", "cuda:0")

    def newline_token_id(self) -> int:
        return self._config.getint("newline_token_id", 198)

    def model_max_tokens(self) -> int:
        return self._config.getint("model_max_tokens", 512)

    def output_max_tokens(self) -> int:
        return self._config.getint("output_max_tokens", 64)

    def generation_temperature(self) -> float:
        return self._config.getfloat("temperature", 0.6)

    def generation_top_k(self) -> int:
        return self._config.getint("top_k", 50)

    def generation_top_p(self) -> float:
        return self._config.getfloat("top_p", 0.92)

    def generation_no_repeat_ngram_size(self) -> int:
        return self._config.getint("no_repeat_ngram_size", 6)

    def generation_repetition_penalty(self) -> float:
        return self._config.getfloat("repetition_penalty", 1.6)

    def generation_min_length(self) -> int:
        return self._config.getint("min_length", 2)
