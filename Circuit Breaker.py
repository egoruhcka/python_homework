import time
from functools import wraps
from collections import deque
from itertools import islice

class NotAliveError(Exception):
    pass

def circuit_breaker(state_count: int,
                    error_count: int,
                    network_errors: list[type[Exception]],
                    sleep_time_sec: int):
    if state_count <= 10 or error_count >= 10:
        raise ValueError
    def decorator(func):
        state = deque(maxlen=state_count)
        last_time_error = 0
        tuple_errors: tuple[type[Exception]] = tuple(network_errors)

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_time_error

            if list(islice(state, max(0, len(state) - error_count), None)).count(False) == error_count:
                raise NotAliveError()

            if len(state) > 0 and state[-1] is False:
                time.sleep(sleep_time_sec)

            try:
                result = func(*args, **kwargs)
                state.append(True)
                return result

            except tuple_errors: # pylint: disable=catching-non-exception
                last_time_error = time.time()
                state.append(False)
                raise
   
        return wrapper
    return decorator
