DEFAULT_LOG_LEVEL: str = "INFO"
ERROR_MESSAGE_COULD_NOT_GENERATE: str = "I don't know what to say!"

TWITCH_AUTH_JSON: str = "twitch_auth.json"

INPUT_MESSAGE_MAX_CHARS: int = 200

# Model
MODEL_PATH: str = "model"
DEVICE: str = "cuda:0"
NEWLINE_TOKEN_ID: int = 198  # GPT2Tokenizer.from_pretrained("gpt2").encode("\n")[0]
MODEL_MAX_TOKENS: int = 512
OUTPUT_MAX_TOKENS: int = 64

# Generation
TEMPERATURE: float = 0.6
TOP_K: int = 50
TOP_P: float = 0.92
NO_REPEAT_NGRAM_SIZE: int = 6
REPETITION_PENALTY: float = 1.6
LENGTH_PENALTY: float = 0.8
PROMPT_DUPLICATION_FACTOR: int = 3
MIN_LENGTH: int = 2

RATE_LIMIT_SECONDS: int = 30
RATE_LIMIT_VOLUME: int = 50

CLIENT_TIMEOUT: int = 10
MAX_RETRIES_FOR_REPLY: int = 50
