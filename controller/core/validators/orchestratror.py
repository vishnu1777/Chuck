from validators.sort_manager import SortManager
from validators.response_validator import SchemaValidator
class Orchestrator:
    """
    Orchestrates method calls across different classes dynamically.
    """

    def __init__(self):
        """
        Initializes an empty registry to store instances of different classes.
        """
        self.class_registry = {}

    def register_class(self, class_instance):
        """
        Registers a class instance in the orchestrator.
        :param class_instance: Instance of the class.
        """
        class_name = class_instance.__class__.__name__  # Get actual class name
        self.class_registry[class_name] = class_instance


    def execute_method(self, class_name, method_name, *args, **kwargs):
        """
        Executes a method on a registered class instance.
        :param class_name: Name of the registered class.
        :param method_name: Method to execute.
        """
        instance = self.class_registry.get(class_name)
        if not instance:
            raise ValueError(f"Class '{class_name}' is not registered.")
        
        method = getattr(instance, method_name, None)
        if not method:
            raise ValueError(f"Method '{method_name}' not found in '{class_name}'.")

        return method(*args, **kwargs)  # Call the method dynamically

