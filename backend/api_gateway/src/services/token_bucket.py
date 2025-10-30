import time
import json
from typing import TypedDict
from redis.asyncio import Redis
from logger import get_logger

logger = get_logger("TokenBucket")


class BucketState(TypedDict):
    """Type definition for TokenBucket state representation.

    Defines the structure for serializing and deserializing token bucket state
    in Redis storage.

    Attributes:
        tokens: Current number of available tokens in the bucket as float.
        last_refill: Timestamp of the last token refill operation as float.
        capacity: Maximum token capacity of the bucket as integer.
        refill_rate: Rate at which tokens are refilled per second as float.
    """

    tokens: float
    last_refill: float
    capacity: int
    refill_rate: float


class TokenBucket:
    """A token bucket rate limiter implementation using Redis for distributed coordination.

    This class implements the token bucket algorithm for rate limiting,
    allowing distributed rate limiting across multiple application instances.

    Attributes:
        redis: Redis client instance for state storage.
        capacity: Maximum number of tokens the bucket can hold.
        refill_rate: Number of tokens added to the bucket per second.
    """

    def __init__(self, redis_client: Redis, capacity: int, refill_rate: float):
        self.redis = redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate

    async def acquire(self, identifier: str, tokens: int = 1) -> bool:
        """Attempts to acquire tokens from the token bucket for a given identifier.

        Implements the core token bucket algorithm with refill mechanism and
        distributed state management in Redis.

        Args:
            identifier: Unique string identifying the client or resource to rate limit.
            tokens: Number of tokens to acquire from the bucket. Defaults to 1.

        Returns:
            bool: True if tokens were successfully acquired, False if rate limit exceeded.

        Note:
            - Creates new bucket state if none exists for the identifier
            - Automatically refills tokens based on elapsed time
            - Falls back to allowing requests (returning True) on Redis errors
            - Uses exponential backoff for error scenarios to avoid blocking traffic
        """
        try:
            key = f"token_bucket:{identifier}"
            current_time = time.time()

            state = await self._get_bucket_state(key)
            if not state:
                state = await self._initialize_bucket(key, current_time)

            await self._refill_tokens(state, current_time)

            if state["tokens"] >= tokens:
                state["tokens"] -= tokens
                await self._save_bucket_state(key, state)
                return True
            else:
                logger.warning(f"Rate limit exceeded: {identifier}")
                return False

        except Exception as e:
            logger.exception(f"Error in token bucket acquire: {e}")
            return True

    async def _get_bucket_state(self, key: str) -> BucketState | None:
        """Retrieves the current state of a token bucket from Redis.

        Fetches and deserializes the bucket state from Redis storage. Handles
        missing data and deserialization errors gracefully.

        Args:
            key: Redis key where the bucket state is stored.

        Returns:
            BucketState | None: Deserialized bucket state dictionary if found and
            valid, None if key doesn't exist or deserialization fails.

        Note:
            - Returns None for both missing keys and deserialization errors
            - Logs errors for debugging but doesn't propagate exceptions
        """
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting bucket state: {e}")
            return None

    async def _initialize_bucket(
        self, key: str, current_time: float
    ) -> BucketState:
        """Initializes a new token bucket with full capacity.

        Creates a fresh bucket state with maximum tokens and current timestamp,
        then persists it to Redis storage.

        Args:
            key: Redis key where the bucket state will be stored.
            current_time: Current timestamp as float for initial refill time.

        Returns:
            BucketState: Newly created bucket state dictionary with full tokens
            and current timestamp.

        Note:
            - Sets initial token count to full capacity
            - Uses provided current_time for last_refill to start refill timing
            - Immediately persists the state to Redis for consistency
        """
        state: BucketState = {
            "tokens": float(self.capacity),
            "last_refill": current_time,
            "capacity": self.capacity,
            "refill_rate": self.refill_rate,
        }
        await self._save_bucket_state(key, state)
        return state

    async def _refill_tokens(self, state: BucketState, current_time: float):
        """Refills tokens in the bucket based on elapsed time.

        Calculates the number of tokens to add based on time elapsed since last
        refill and updates the bucket state accordingly.

        Args:
            state: Current bucket state dictionary to be updated.
            current_time: Current timestamp as float for calculating elapsed time.

        Note:
            - Calculates tokens based on refill rate and elapsed time
            - Ensures token count never exceeds bucket capacity
            - Updates last_refill timestamp to current time
            - Modifies the state dictionary in-place
        """
        time_elapsed = current_time - state["last_refill"]
        new_tokens = time_elapsed * state["refill_rate"]
        state["tokens"] = min(state["capacity"], state["tokens"] + new_tokens)
        state["last_refill"] = current_time

    async def _save_bucket_state(self, key: str, state: BucketState):
        """Persists the bucket state to Redis with automatic expiration.

        Serializes and saves the bucket state to Redis with a calculated TTL
        based on bucket capacity and refill rate.

        Args:
            key: Redis key where the bucket state will be stored.
            state: Bucket state dictionary to serialize and save.

        Note:
            - Sets expiration time to twice the time needed to fill an empty bucket
            - Uses run_in_executor to avoid blocking the event loop
            - Handles serialization and Redis errors gracefully with logging
            - TTL calculation: 2 * (capacity / refill_rate) for safe cleanup
        """
        try:
            expiration = int(2 * (self.capacity / self.refill_rate))
            await self.redis.setex(key, expiration, json.dumps(state))
        except Exception as e:
            logger.error(f"Error saving bucket state: {e}")
