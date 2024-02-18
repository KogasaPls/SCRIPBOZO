from logging import Logger

import torch
from scripbozo.interfaces.LanguageModel import LanguageModel
from scripbozo.ModelConfig import ModelConfig
from scripbozo.util.CustomLogger import CustomLogger
from scripbozo.util.TensorBuilder import TensorBuilder
from torch import Tensor
from transformers.models.gpt2.modeling_gpt2 import GPT2LMHeadModel as BaseModel

log: Logger = CustomLogger(__name__).get_logger()


class GPT2Model(LanguageModel):
    _config: ModelConfig
    wrappedModel: BaseModel
    newline_token_id: int

    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        self._config = config
        self.wrappedModel = BaseModel.from_pretrained(self._config.path()).to(
            self.device()
        )

    def device(self) -> str:
        return self._config.cuda_device()

    def model_max_tokens(self) -> int:
        return self._config.model_max_tokens()

    def output_max_tokens(self) -> int:
        return self._config.output_max_tokens()

    def temperature(self) -> float:
        return self._config.generation_temperature()

    def top_k(self) -> int:
        return self._config.generation_top_k()

    def top_p(self) -> float:
        return self._config.generation_top_p()

    def no_repeat_ngram_size(self) -> int:
        return self._config.generation_no_repeat_ngram_size()

    def repetition_penalty(self) -> float:
        return self._config.generation_repetition_penalty()

    def min_length(self) -> int:
        return self._config.generation_min_length()

    def max_input_length(self) -> int:
        return self.model_max_tokens() - self.output_max_tokens()

    def generate(self, _tokens: Tensor) -> Tensor:
        log.debug(f"generate({_tokens})")

        tokens: Tensor = self.trim_tokens_to_max_input_length(_tokens)
        attention_mask: Tensor = torch.ones_like(tokens)

        generated: Tensor = self.wrappedModel.generate(
            tokens.to(self.device()),
            attention_mask=attention_mask.to(self.device()),
            max_new_tokens=self.output_max_tokens(),
            temperature=self.temperature(),
            top_k=self.top_k(),
            top_p=self.top_p(),
            no_repeat_ngram_size=self.no_repeat_ngram_size(),
            repetition_penalty=self.repetition_penalty(),
            min_length=self.min_length(),
            eos_token_id=self.newline_token_id,
            do_sample=True,
            num_return_sequences=1,
        )[0]

        # strip input tokens from output
        return generated[tokens.shape[1] :]

    def trim_tokens_to_max_input_length(self, tokens: Tensor) -> Tensor:
        max_input_length: int = self.max_input_length()
        if tokens.shape[1] > max_input_length:
            log.debug(
                f"trimming tokens to max size: {tokens.shape[1]} > {max_input_length}"
            )
            tokens = (
                TensorBuilder()
                .append(tokens)
                .left_trim_to_size(max_input_length)
                .build()
            )
        return tokens
