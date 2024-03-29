from typing import List

import torch
from scripbozo.interfaces.Tokenizer import Tokenizer
from scripbozo.util.StringUtils import remove_self_mentions
from torch import Tensor
from twitchio import Message


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


class MessageStack(List[TokenWrapper]):
    _max_tokens: int

    def __init__(self, max_tokens: int) -> None:
        super().__init__()
        self._max_tokens = max_tokens

    async def add_message(self, message: Message) -> None:
        token_wrapper: TokenWrapper = TokenWrapper(message)
        self.append(token_wrapper)

    def tokenize(self, tokenizer: Tokenizer) -> Tensor:
        """Starting from the newest messages, tokenize if necessary and then
        add to the list to be returned."""
        num_tokens: int = 0
        is_full: bool = False
        max_tokens: int = self._max_tokens

        for msg in reversed(self):
            # If we have enough tokens, delete the rest of the list.
            if is_full:
                self.remove(msg)
                del msg
                continue

            msg.tokenize_if_necessary(tokenizer)
            num_tokens += msg.get_num_tokens()

            if num_tokens >= max_tokens:
                is_full = True

        tokens = torch.cat(self.get_tokens(), dim=1)
        return tokens

    def delete_tokens_from(self, idx: int) -> None:
        del reversed(self)[idx:]

    def get_tokens(self) -> List[Tensor]:
        """Return a list of tokenized messages in chronological order (newest last)."""
        return [msg.tokens for msg in self if msg.tokens is not None][
            : self._max_tokens
        ]
