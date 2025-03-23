import os
from pathlib import Path
from handlers.executor import Executor
from utils.global_store import GlobalStore,LocalStore
from utils.file_utils import *
from manager.env_manager import EnvManager
from manager.config_manager import ConfigLoader

class ScenarioExecutor:
    def __init__(self):
        """Initialize global store and configuration loader."""
        self.global_store = GlobalStore()
        self.config_loader = ConfigLoader(self.global_store)
        self.root_path = None

    def setup_environment(self):
        """Loads environment configurations and sets base URL."""
        root_path = get_folder_root_path()
        env_manager = EnvManager(os.path.join(root_path, self.global_store.get_value("selected_region")))
        env_data = env_manager.load_env()
        self.global_store.set_value("env_data", env_data)
        self.global_store.set_value("region_config_path",os.path.join(root_path,self.global_store.get_value("selected_region"),"config"))
        selected_env = env_manager.prompt_env()
        base_url = env_data["environments"].get(selected_env, {}).get("base_url", "")
        self.global_store.set_value("base_url", base_url)
        return root_path

    def setup_region_and_scenarios(self):
        """Loads region configurations and prompts user to select a region."""
        root_path = get_folder_root_path()
        self.config_loader.prompt_region(self.global_store)
        self.config_loader.prompt_scenarios(self.global_store, root_path) 
        self.root_path = self.setup_environment()  # Update root_path after env setup
        self.config_loader.select_channels(self.global_store)
        return self.root_path

    def load_api_paths(self):
        """Loads API path configurations."""
        region_path=os.path.join(self.root_path,self.global_store.get_value("selected_region"))
        path_config_path = os.path.join(self.root_path, self.global_store.get_value("selected_region"), "config", "path_config.json")
        global_config_path = os.path.join(self.root_path, self.global_store.get_value("selected_region"), "config", "global_config.json")
        path_config = read_json_file(path_config_path)
        self.global_store.set_value("path_config_path", path_config_path)
        self.global_store.set_value("region_path",region_path)
        self.global_store.set_value("path_config", path_config)
        self.global_store.set_value("global_config_path", global_config_path)

    def set_scenario_path(self):
        """Sets the scenario paths dynamically based on user selection."""
        selected_region = self.global_store.get_value("selected_region")
        selected_scenarios = self.global_store.get_value("selected_scenarios")

        scenario_paths = [os.path.join(self.root_path, selected_region, "Scenarios", scenario) for scenario in selected_scenarios]
        return scenario_paths

    def start_channel_vice_execution(self, scenario_path, channel_name):
        """Executes scenarios for a specific channel with isolated state management."""
        # Create a fresh LocalStore instance for each scenario execution
        local_store = LocalStore()
        scenario_name = Path(scenario_path).name
        local_store.set_value("scenario_path", scenario_path)
        local_store.set_value("scenario_name", scenario_name)
        local_store.set_value("current_channel", channel_name)

        merged_config_path = os.path.join(
            self.root_path,
            self.global_store.get_value("selected_region"),
            "config",
            "merged_config.json"
        )
        local_store.set_value("merged_config_path", merged_config_path)

        dependency_path = os.path.join(scenario_path, "dependency.json")

        try:
            # Create and merge configs
            create_and_merge_configs(
                self.global_store.get_value("global_config_path"),
                dependency_path,
                merged_config_path
            )

            print(f"🚀 Starting execution for: {scenario_path} on channel: {channel_name}")

            # Execute the scenario
            executor = Executor(scenario_path)
            executor.run()
            # print("local->",local_store.get_all_values())
            print(f"✅ Execution completed for: {scenario_path} on channel: {channel_name}")

        except Exception as e:
            print(f"❌ Error executing scenario {scenario_path} on channel {channel_name}: {str(e)}")

        finally:
            # Cleanup: always delete the merged config file
            cleanup_merged_config(merged_config_path)
            print(f"🔄 Resetting local store for next scenario...\n")

    def start_execution(self, scenario_paths):
        """Executes scenarios across selected channels."""
        env_data = self.global_store.get_value("env_data")
        selected_channels = env_data.get("channels")
        for channel_name, is_selected in selected_channels.items():
            if is_selected:
                for scenario_path in scenario_paths:
                    self.start_channel_vice_execution(scenario_path, channel_name)
                    # print("global->",self.global_store.get_all_values())  #print all stored values -- to debug

    def run(self):
        """Runs the full execution pipeline."""
        self.root_path = self.setup_region_and_scenarios()
        self.load_api_paths()
        scenario_paths = self.set_scenario_path()
        self.start_execution(scenario_paths)


if __name__ == "__main__":
    executor = ScenarioExecutor()
    executor.run()
