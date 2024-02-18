from logging import Logger

from scripbozo.interfaces.Tokenizer import Tokenizer
from scripbozo.util.CustomLogger import CustomLogger
from torch import Tensor
from transformers.models.gpt2.tokenization_gpt2 import (
    GPT2Tokenizer as BaseGPT2Tokenizer,
)

log: Logger = CustomLogger(__name__).get_logger()


class GPT2Tokenizer(Tokenizer):
    wrappedTokenizer: BaseGPT2Tokenizer

    def __init__(self) -> None:
        super().__init__()
        self.wrappedTokenizer = BaseGPT2Tokenizer.from_pretrained("gpt2")

    def encode(self, message: str) -> Tensor:
        log.debug(f"encode: {message}")
        encoded: list[int] = self.wrappedTokenizer.encode(
            message + "\n", return_tensors="pt", truncation=True
        )
        log.debug(f"encoded: {encoded}")
        return Tensor(encoded)

    def decode(self, tokenized: Tensor) -> str:
        log.debug(f"decode: {tokenized}")
        decoded: str = self.wrappedTokenizer.decode(tokenized)
        log.debug(f"decoded: {decoded}")
        return decoded
