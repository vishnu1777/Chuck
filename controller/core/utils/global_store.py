class GlobalStore:
    """Singleton class for global shared data storage."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalStore, cls).__new__(cls)
            cls._instance._store = {}  # Shared global store
        return cls._instance

    def set_value(self, key, value):
        self._store[key] = value

    def get_value(self, key):
        return self._store.get(key)

    def get_all_values(self):
        return self._store


class LocalStore:
    """Singleton class for local execution storage."""
    
    _instance = None  # Class-level variable to store the single instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalStore, cls).__new__(cls)
            cls._instance._store = {}  # Initialize store for the singleton instance
        return cls._instance

    def set_value(self, key, value):
        """Stores a key-value pair in the local store."""
        self._store[key] = value

    def get_value(self, key):
        """Retrieves a value by key from the local store."""
        return self._store.get(key)

    def get_all_values(self):
        """Returns all stored key-value pairs."""
        return self._store
