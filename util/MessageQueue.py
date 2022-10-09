import logging
from typing import List

import torch
from torch import Tensor

import src.Config as Config
from twitchio import Message
from util.CustomLogger import CustomLogger
from util.StringUtils import remove_self_mentions
from util.Tokenizer import Tokenizer

log: logging.Logger = CustomLogger(__name__).get_logger()


class WrapsMessage:
    def __init__(self, message: Message) -> None:
        self.message: Message = message

    def get_wrapped_message(self) -> Message:
        return self.message

    def message_is_empty(self) -> bool:
        return (
            self.message is None
            or self.message.content is None
            or self.message.content == ""
        )


class TokenWrapper(WrapsMessage):
    tokens: Tensor | None
    message: Message

    def __init__(self, message: Message) -> None:
        self.message = message
        self.tokens = None

    def tokenize(self, tokenizer: Tokenizer) -> None:
        if self.has_tokens() or self.message_is_empty():
            return
        assert self.message.content
        cleaned: str = remove_self_mentions(self.message.content)
        self.set_tokens(tokenizer.encode(cleaned))

    def has_tokens(self) -> bool:
        return self.tokens is not None

    def set_tokens(self, tokens: Tensor) -> None:
        self.tokens = tokens

    def get_num_tokens(self) -> int:
        assert self.tokens is not None
        return self.tokens[0].shape[0]

    def tokenize_if_necessary(self, tokenizer: Tokenizer) -> None:
        if self.has_tokens():
            return
        self.tokenize(tokenizer)


class MessageQueue(List[TokenWrapper]):
    def __init__(self) -> None:
        super().__init__()

    async def add_message(self, message: Message) -> None:
        token_wrapper: TokenWrapper = TokenWrapper(message)
        self.append(token_wrapper)

    async def tokenize(self, tokenizer: Tokenizer) -> Tensor:
        num_tokens: int = 0
        for token_wrapper in self:
            if num_tokens > self.max_tokens_in_input():
                del token_wrapper
                continue

            token_wrapper.tokenize_if_necessary(tokenizer)
            num_tokens += token_wrapper.get_num_tokens()

        return torch.cat(self.get_tokens(), dim=1)

    def max_tokens_in_input(self) -> int:
        return Config.MODEL_MAX_LENGTH - 2 * Config.OUTPUT_MAX_LENGTH

    def get_tokens(self) -> List[Tensor]:
        return [msg.tokens for msg in self if msg.tokens is not None]
