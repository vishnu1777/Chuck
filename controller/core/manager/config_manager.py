import json
from utils.file_utils import *  # Assuming you have this utility

class ConfigLoader:
    """Handles loading configuration and prompting the user for inputs."""

    _instance = None  # Singleton instance

    def __new__(cls,global_store):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
            cls._instance._post_init(global_store)
        return cls._instance

    def _post_init(self,global_store,exclude_keys={"regions"}):
        """Stores only the required configuration in global_store, excluding specified keys."""
        for key,value in self.config_data.items():
            if key not in exclude_keys:
                global_store.set_value(key, value)
        print("✅ Configuration stored in global_store (excluding unwanted keys).")


    def _load_config(self):
        """Loads configuration from config.json using get_config_path."""
        config_path = get_config_path()  # Using your existing function
        
        try:
            self.config_data = read_json_file(config_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"⚠️ Config file not found: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"⚠️ Invalid JSON format in: {config_path}")

    def prompt_region(self, global_store):
        """
        Prompts the user to select a region and updates global_store.
        :param global_store: Existing global store dictionary to update.
        """
        regions = self.config_data.get("regions", [])
        if not regions:
            raise ValueError("⚠️ No regions found in the config file!")

        print("\nAvailable Regions:")
        for idx, region in enumerate(regions, 1):
            print(f"{idx}. {region}")

        while True:
            try:
                choice = int(input("\nSelect a region by number: "))
                if 1 <= choice <= len(regions):
                    selected_region = regions[choice - 1]
                    global_store.set_value("selected_region", selected_region)
                    print(f"\n✅ Selected Region: {selected_region}")
                    return selected_region
                else:
                    print("⚠️ Invalid selection. Please choose a valid number.")
            except ValueError:
                print("⚠️ Please enter a valid number.")
    def select_channels(self,global_store):
        """Allows the user to select one, multiple, or all channels, ensuring Android is true by default."""
        env_data=global_store.get_value("env_data")
        channels = list(env_data["channels"].keys())  # ['mweb', 'web', 'android', 'ios']
        default_channel = "android"

         # Display available channels
        print("\nAvailable Channels:")
        for i, ch in enumerate(channels, 1):
            print(f" {i}. {ch.capitalize()}")

        while True:
            choices = input("\nSelect channel(s) (Comma-separated numbers or 'all', default is Android): ").strip().lower()

            if not choices:  # If the user presses Enter without input, use default Android
                selected_channels = {ch: (ch == default_channel) for ch in channels}
                print(f"✅ No selection made, using default: Android")
            elif choices == "all":
                selected_channels = {ch: True for ch in channels}  # Select all channels
            else:
                try:
                    indexes = [int(idx.strip()) for idx in choices.split(",") if idx.strip().isdigit()]
                    
                    # Validate indexes
                    if not indexes or any(idx < 1 or idx > len(channels) for idx in indexes):
                        raise ValueError("Invalid selection")

                    selected_keys = [channels[idx - 1] for idx in indexes]
                    
                    # Set selected channels to True, others to False
                    selected_channels = {ch: (ch in selected_keys) for ch in channels}
                    
                    # If Android was not selected, set it to False
                    if default_channel not in selected_keys:
                        selected_channels[default_channel] = False
                except ValueError:
                    print("❌ Invalid selection. Please enter valid numbers from the list.")
                    continue  # Restart selection

            # Update env_data with selected channels
            env_data["channels"] = selected_channels
            print(f"✅ Selected Channels: {', '.join([ch for ch, v in selected_channels.items() if v])}\n")
            return  # Exit after successful selection

    def prompt_scenarios(self, global_store, root_path):
        """Lists available scenarios in the selected region and allows the user to select."""
        selected_region = global_store.get_value("selected_region")
        scenario_dir = os.path.join(root_path, selected_region, "Scenarios")

        if not os.path.exists(scenario_dir):
            raise FileNotFoundError(f"Scenarios folder not found in {scenario_dir}")

        scenarios = [d for d in os.listdir(scenario_dir) if os.path.isdir(os.path.join(scenario_dir, d))]

        if not scenarios:
            raise ValueError("⚠️ No scenarios found.")

        print("\n📂 Available Scenarios:")
        for idx, scenario in enumerate(scenarios, 1):
            print(f"{idx}. {scenario}")
        print(f"{len(scenarios) + 1}. Select All")

        while True:
            try:
                choices = input("\nSelect scenario(s) (Comma-separated numbers or 'all'): ").strip().lower()

                if choices == "all" or choices == str(len(scenarios) + 1):
                    selected_scenarios = scenarios  # Select all scenarios
                else:
                    try:
                        indexes = [int(idx.strip()) for idx in choices.split(",") if idx.strip().isdigit()]
                        
                        # Validate indexes
                        if not indexes or any(idx < 1 or idx > len(scenarios) for idx in indexes):
                            raise ValueError("Invalid selection")

                        selected_scenarios = [scenarios[idx - 1] for idx in indexes]

                    except ValueError:
                        print("❌ Invalid selection. Please enter valid numbers from the list.")
                        continue  # Restart selection

                global_store.set_value("selected_scenarios", selected_scenarios)
                print(f"✅ Selected Scenarios: {', '.join(selected_scenarios)}\n")
                return  # Exit the loop after successful selection

            except ValueError:
                print("❌ Invalid input. Please enter numbers separated by commas or 'all'.")
    def get_config(self):
        """Returns the loaded configuration data."""
        return self.config_data
