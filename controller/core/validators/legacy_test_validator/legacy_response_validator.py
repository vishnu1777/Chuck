import csv
import os
from utils.global_store import LocalStore,GlobalStore
from logmanager.logger_manager import LoggerManager
class LegacyAPIResponseValidator:
    def __init__(self, validation_obj,api_name):
        self.validation_obj = validation_obj
        self.local_store= LocalStore()
        self.global_store=GlobalStore()
        self.api_name=api_name
        self.logger = LoggerManager(self.__class__.__name__)
        self.scenario_path=self.local_store.get_value("scenario_path")
        self.current_channel=self.local_store.get_value("current_channel")

    def loadCSVFile(self,filename:str)->dict:
        # opening the CSV file
        with open(filename, mode ='r',encoding="utf8") as file:     
            csvFile = csv.DictReader(file)
            searchData={}
            index=1
            for data in csvFile:
                if index not in searchData:
                    if data['ReadRow'].rstrip().lower() =="yes":
                        searchData[index]=data
                index+=1
        if len(searchData)>0:
            return searchData
        else:
            return None
    def calculate_validation_summary(self, validated_values):
        """
        Calculates total test cases, passed cases, failed cases, and pass percentage.
        """
        total_cases = len(validated_values)
        failed_cases = 0
        structured_values = []

        for main_key in validated_values:
            sub_values = [validated_values[main_key][sub_key] for sub_key in validated_values[main_key]]
            structured_values.append(sub_values)

        for items in structured_values:
            if items:
                if False in items or None in items:
                    failed_cases += 1
            else:
                total_cases -= 1

        passed_cases = total_cases - failed_cases
        try:
            pass_percentage = (passed_cases / total_cases) * 100
        except ZeroDivisionError:
            pass_percentage = 0.0

        return {
            "totalCases": total_cases,
            "totalPassed": passed_cases,
            "failedCases": failed_cases,
            "passPercentage": pass_percentage,
        }
    def validate_responses(self, response,api_name):
        """
        Iterates through test files, extracts validation rules,
        and validates response data.
        """
        try:
            file_path=os.path.join(self.scenario_path,"validations",self.current_channel,self.api_name+".csv")
            if not os.path.exists(file_path):
                return True
            validation_rules = self.loadCSVFile(file_path)
            
            # Extract expected values from response
            validated_results = self.validation_obj.getValidatedFieldValue(
                validation_rules, response
            )
            
            # Validate extracted values against expected values
            validated_list = self.validation_obj.validateValues(validated_results)
            key = f"{api_name}_{self.local_store.get_value('current_channel')}"
            # Update the results dictionary with new validation summary
            # Retrieve the existing results, default to an empty dictionary if None
            existing_results = self.global_store.get_value("final_test_results") or {}

            # Update with new test results for the specific channel
            existing_results[key] = self.calculate_validation_summary(validated_results)

            # Store the updated results back
            self.global_store.set_value("final_test_results", existing_results)

            return validated_list 
        except Exception as e:
            self.logger.log_error(f"Oops something failed while validating response {e}")
            
        
