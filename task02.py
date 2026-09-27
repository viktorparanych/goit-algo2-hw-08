import time
import random
from typing import Dict

class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval
        self.user_last_message: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        """Перевіряє, чи пройшов мінімально необхідний інтервал з моменту останнього повідомлення."""
        if user_id not in self.user_last_message:
            return True
        return (time.time() - self.user_last_message[user_id]) >= self.min_interval

    def record_message(self, user_id: str) -> bool:
        """Оновлює час останнього повідомлення, якщо відправка дозволена."""
        if self.can_send_message(user_id):
            self.user_last_message[user_id] = time.time()
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """Розраховує точний час у секундах, який залишився чекати до наступного повідомлення."""
        if user_id not in self.user_last_message:
            return 0.0
        
        elapsed_time = time.time() - self.user_last_message[user_id]
        return max(0.0, self.min_interval - elapsed_time)

def test_throttling_limiter():
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\nСимуляція потоку повідомлень - Throttling")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 10 секунд...")
    time.sleep(10)

    print("\nНова серія повідомлень після очікування")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_throttling_limiter()