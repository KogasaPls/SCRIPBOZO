import gc
import logging
from typing import List

import torch
from torch import Tensor

import src.Config as Config
from src.interfaces.Tokenizer import Tokenizer
from src.util.CustomLogger import CustomLogger
from src.util.StringUtils import remove_self_mentions
from twitchio import Message

log: logging.Logger = CustomLogger(__name__).get_logger()


class WrapsMessage:
    def __init__(self, message: Message) -> None:
        self.message: Message = message

    def get_wrapped_message(self) -> Message:
        return self.message

    def message_is_empty(self) -> bool:
        return self.message is None or self.message.content is None or self.message.content == ""


class TokenWrapper(WrapsMessage):
    tokens: Tensor | None
    message: Message

    def __init__(self, message: Message) -> None:
        super().__init__(message)
        self.tokens = None

    def tokenize(self, tokenizer: Tokenizer) -> None:
        if self.has_tokens() or self.message_is_empty():
            return
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
        if not self.has_tokens():
            self.tokenize(tokenizer)


class MessageQueue(List[TokenWrapper]):
    def __init__(self) -> None:
        super().__init__()

    async def add_message(self, message: Message) -> None:
        token_wrapper: TokenWrapper = TokenWrapper(message)
        self.append(token_wrapper)

    def tokenize(self, tokenizer: Tokenizer) -> Tensor:
        """Starting from the newest messages, tokenize if necessary and then
        add to the list to be returned."""
        num_tokens: int = 0
        max_tokens = self.max_tokens_in_input()

        for msg in reversed(self):
            # If there's still room in the input, tokenize the message.
            if num_tokens < max_tokens:
                msg.tokenize_if_necessary(tokenizer)
                num_tokens += msg.get_num_tokens()
            # If the list is too big now, delete these tokens and any later ones.
            if num_tokens >= max_tokens:
                del msg
        # Free up memory from deleted tokens/wrappers.
        gc.collect()

        tokens = torch.cat(self.get_tokens(), dim=1)
        return tokens

    def delete_tokens_from(self, idx: int) -> None:
        del reversed(self)[idx:]

    def max_tokens_in_input(self) -> int:
        return Config.MODEL_MAX_TOKENS - Config.OUTPUT_MAX_TOKENS

    def get_tokens(self) -> List[Tensor]:
        """Return a list of tokenized messages in chronological order (newest last)."""
        return [msg.tokens for msg in self if msg.tokens is not None][: self.max_tokens_in_input()]
