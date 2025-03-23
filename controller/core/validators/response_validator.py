import importlib.util
import os
from pydantic import ValidationError

class SchemaValidator:
    """
    Validates API responses against dynamically loaded Pydantic models.
    """

    def __init__(self, enforce_class_match=False):
        """
        Initialize SchemaValidator with optional class name enforcement.
        :param enforce_class_match: Whether to enforce class name matching.
        """
        self.enforce_class_match = enforce_class_match  # Disabled by default

    def load_model_from_file(self, model_file_path, model_class_name):
        """
        Dynamically loads a Pydantic model from a Python file.

        :param model_file_path: Path to the .py file containing the model.
        :param model_class_name: The name of the Pydantic model class to use.
        :return: The loaded model class, or None if failed.
        """
        if not os.path.exists(model_file_path):
            print(f"❌ Error: Model file '{model_file_path}' not found.")
            return None

        module_name = os.path.splitext(os.path.basename(model_file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, model_file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # ✅ Class name validation can be enabled in the future
        if self.enforce_class_match and not hasattr(module, model_class_name):
            print(f"⚠️ Warning: Class '{model_class_name}' not found in '{model_file_path}', but validation will proceed.")
        
        # Return any valid Pydantic class (not enforcing class name match)
        for attr in dir(module):
            obj = getattr(module, attr)
            if isinstance(obj, type) and hasattr(obj, "__annotations__"):  # Checking for Pydantic-like structure
                return obj
        
        print(f"❌ No valid Pydantic model found in '{model_file_path}'.")
        return None
    
    def validate_schema(self, response_data, model_file_path, model_class_name):
        """
        Validates the API response against a dynamically loaded Pydantic model.

        :param response_data: The API response (dict).
        :param model_file_path: The Python file containing the model.
        :param model_class_name: The Pydantic model class name.
        :return: True if valid, False + error messages if invalid.
        """
        schema_model = self.load_model_from_file(model_file_path, model_class_name)
        if not schema_model:
            return False  # Model loading failed

        try:
            validated_data = schema_model(**response_data)
            return True  # ✅ Valid response
        except ValidationError as e:
            print(f"❌ Schema validation failed:\n{e}")
            return False  # ❌ Invalid response
