import logging
import random
import time
from functools import wraps

from redis import RedisError as redis_error


def backoff(
    start_sleep_time=0.1, factor=2, border_sleep_time=10.0, limit_of_retries=10
):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный
    экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * (factor ^ n), если t < border_sleep_time
        t = border_sleep_time, иначе
    :param limit_of_retries: количество повторений функции, если = 0, то бесконечный цикл
    :param start_sleep_time: начальное время ожидания
    :param factor: во сколько раз нужно увеличивать время ожидания на каждой итерации
    :param border_sleep_time: максимальное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            retries = 0
            delay = start_sleep_time
            while True:
                try:
                    result_func = func(*args, **kwargs)
                    return result_func
                except Exception as e:
                    time.sleep(delay)
                    retries += 1
                    # Compute delay and chose between border_sleep_time and computed
                    computed_delay = min(
                        start_sleep_time * (factor**retries), border_sleep_time
                    )
                    # Add jitter
                    delay = computed_delay / 2 + \
                        random.uniform(0, computed_delay / 2)
                    if isinstance(e, redis_error):
                        logging.error(msg=f"Redis error. {e}")
                    else:
                        logging.error(msg=f"Unknown error. {e}")

                    if limit_of_retries != 0 and retries > limit_of_retries:
                        logging.critical(
                            msg=f"The number of reconnections exceeded. {e}"
                        )
                        raise

        return inner

    return func_wrapper
