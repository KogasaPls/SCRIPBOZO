from logging import Logger

import torch
from torch import Tensor
from transformers.models.gpt2.modeling_gpt2 import GPT2LMHeadModel as BaseModel

import src.Config as Config
from src.interfaces.LanguageModel import LanguageModel
from src.util.CustomLogger import CustomLogger
from src.util.TensorBuilder import TensorBuilder

log: Logger = CustomLogger(__name__).get_logger()


def get_device_from_config() -> torch.device:
    if (Config.DEVICE == "cuda:0") and not torch.cuda.is_available():
        return torch.device("cpu")
    return torch.device(Config.DEVICE)


class GPT2Model(LanguageModel):
    wrappedModel: BaseModel
    device: torch.device
    maxLength: int = Config.MODEL_MAX_LENGTH
    maxOutputLength: int = Config.OUTPUT_MAX_LENGTH

    def __init__(self) -> None:
        super().__init__()
        self.device = get_device_from_config()
        self.wrappedModel = BaseModel.from_pretrained(Config.MODEL_PATH).to(Config.DEVICE)

    def generate(self, _tokens: Tensor) -> Tensor:
        log.debug(f"generate({_tokens})")

        tokens: Tensor = self.trim_tokens_to_max_input_length(_tokens)
        attention_mask: Tensor = torch.ones_like(tokens)

        assert self.maxOutputLength < self.maxLength

        generated: Tensor = self.wrappedModel.generate(
            tokens.to(Config.DEVICE),
            attention_mask=attention_mask.to(Config.DEVICE),
            max_new_tokens=self.maxOutputLength,
            temperature=Config.TEMPERATURE,
            top_k=Config.TOP_K,
            top_p=Config.TOP_P,
            no_repeat_ngram_size=Config.NO_REPEAT_NGRAM_SIZE,
            repetition_penalty=Config.REPETITION_PENALTY,
            min_length=Config.MIN_LENGTH,
            eos_token_id=Config.NEWLINE_TOKEN_ID,
            do_sample=True,
            num_return_sequences=1,
        )[0]

        # strip input tokens from output
        return generated[tokens.shape[1] :]

    def get_max_input_length(self) -> int:
        return self.maxLength - self.maxOutputLength

    def trim_tokens_to_max_input_length(self, tokens: Tensor) -> Tensor:
        max_input_length: int = self.maxLength - self.maxOutputLength
        if tokens.shape[1] > max_input_length:
            log.debug(f"trimming tokens to max size: {tokens.shape[1]} > {max_input_length}")
            tokens = TensorBuilder().append(tokens).left_trim_to_size(max_input_length).build()
        return tokens
