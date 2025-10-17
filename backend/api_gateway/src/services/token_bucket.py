import time
import json
import asyncio
from typing import TypedDict
from redis import Redis
from logger import get_logger

logger = get_logger("TokenBucket")


class BucketState(TypedDict):
    tokens: float
    last_refill: float
    capacity: int
    refill_rate: float


class TokenBucket:
    def __init__(self, redis_client: Redis, capacity: int, refill_rate: float):
        self.redis = redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate

    async def acquire(self, identifier: str, tokens: int = 1) -> bool:
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
        try:
            data = await asyncio.get_event_loop().run_in_executor(
                None, self.redis.get, key
            )
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting bucket state: {e}")
            return None

    async def _initialize_bucket(
        self, key: str, current_time: float
    ) -> BucketState:
        state: BucketState = {
            "tokens": float(self.capacity),
            "last_refill": current_time,
            "capacity": self.capacity,
            "refill_rate": self.refill_rate,
        }
        await self._save_bucket_state(key, state)
        return state

    async def _refill_tokens(self, state: BucketState, current_time: float):
        time_elapsed = current_time - state["last_refill"]
        new_tokens = time_elapsed * state["refill_rate"]
        state["tokens"] = min(state["capacity"], state["tokens"] + new_tokens)
        state["last_refill"] = current_time

    async def _save_bucket_state(self, key: str, state: BucketState):
        try:
            expiration = int(2 * (self.capacity / self.refill_rate))
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.redis.setex(key, expiration, json.dumps(state)),
            )
        except Exception as e:
            logger.error(f"Error saving bucket state: {e}")
