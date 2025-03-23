import os
from utils.file_utils import read_json_file
from utils.global_store import GlobalStore

class EnvManager:
    """Manages environment loading and selection."""

    def __init__(self, root_path):
        self.env_file = os.path.join(root_path, "config", "env.json")
        self.global_store = GlobalStore()

    def load_env(self):
        """Loads the environment configuration from the JSON file."""
        return read_json_file(self.env_file) or {}

    def prompt_env(self):
        """Prompts the user to select an environment and sets it globally."""
        env_data = self.load_env()
        environments = list(env_data.get("environments", {}).keys())

        print(f"Select environment: {', '.join(environments)}")
        while True:
            env = input("Enter environment: ").strip().lower()
            if env in environments:
                self.global_store.set_value("selected_env", env)
                return env
            print("Invalid selection. Try again.")
