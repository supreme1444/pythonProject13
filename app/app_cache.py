class ReferralCodeCache:
    def __init__(self):
        self.cache = {}

    def __setitem__(self, key, value):
        """Сохранение реферального кода по ключу."""
        self.cache[key] = value

    def __getitem__(self, key):
        """Получение реферального кода по ключу."""
        return self.cache.get(key)

    def __contains__(self, key):
        """Проверка, существует ли реферальный код в кэше."""
        return key in self.cache

    def delete(self, key):
        """Удаление элемента из кэша по ключу."""
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """Очистка кэша."""
        self.cache.clear()

    def __repr__(self):
        """Представление кэша в виде строки."""
        return f"{self.cache}"
