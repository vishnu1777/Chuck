from utils.global_store import GlobalStore,LocalStore
from validators.legacy_test_validator.legacy_response_validator import LegacyAPIResponseValidator
from validators.response_validator import SchemaValidator
from utils.legacy_util_functions.legacy_validation_checker import genericValidations
import os


class TestAPIValidation:
    def __init__(self, orchestrator, schema_path):
        self.orchestrator = orchestrator
        self.global_store = GlobalStore()
        self.schema_path = schema_path
        self.local_store = LocalStore()
        self.validationObj=genericValidations()

    # need to get file names from the validations 

    def test(self, response, api_name):
        # legacy validation test with config enabled 
        if self.global_store.get_value("env_data").get("legacy_test_enabled"):
            self.orchestrator.register_class(LegacyAPIResponseValidator(self.validationObj,api_name))
            self.orchestrator.execute_method(
                "LegacyAPIResponseValidator", "validate_responses", response,
                api_name
            )
        
        if not self.global_store.get_value("env_data").get("enable_schema"):
            return
        
        self.orchestrator.register_class(SchemaValidator())
        self.orchestrator.execute_method(
            "SchemaValidator", "validate_schema", response,
            os.path.join(self.schema_path, self.local_store.get_value("current_channel"), api_name + ".py"),
            api_name.upper()
        )