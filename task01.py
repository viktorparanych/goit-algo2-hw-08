import random
import time
from typing import Dict
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_history: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """Очищає застарілі запити з вікна та видаляє користувача, якщо його історія порожня."""
        if user_id not in self.user_history:
            return
            
        user_deque = self.user_history[user_id]
        while user_deque and user_deque[0] <= current_time - self.window_size:
            user_deque.popleft()
            
        if not user_deque:
            del self.user_history[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """Перевіряє, чи не перевищено ліміт повідомлень у поточному вікні."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        return len(self.user_history.get(user_id, [])) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """Фіксує нове повідомлення, якщо це дозволено лімітами."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        
        if len(self.user_history.get(user_id, [])) < self.max_requests:
            if user_id not in self.user_history:
                self.user_history[user_id] = deque()
            self.user_history[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """Повертає кількість секунд до можливості відправити наступне повідомлення."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        
        if len(self.user_history.get(user_id, [])) < self.max_requests:
            return 0.0
        
        oldest_message_time = self.user_history[user_id][0]
        return max(0.0, self.window_size - (current_time - oldest_message_time))

#демонстрація роботи
def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print("\nСимуляція потоку повідомлень")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\nНова серія повідомлень після очікування")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()