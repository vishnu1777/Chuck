# API Testing Framework

## Overview
This API Testing Framework is designed to automate end-to-end API validation, enabling dynamic request handling, response validation, and dependency management. It supports **region-specific configurations**, **execution sequencing**, and **store & replace** functionality for data-driven testing.

## Features
- **Modular Code Structure:** Keep core logic separate from user-modified files.
- **Scenario-Specific Execution:** Define custom test cases for different regions.
- **Store & Replace Mechanism:** Extract and reuse response values in subsequent API requests.
- **Dynamic Execution Flow:** Control execution order using JSON-based configurations.
- **Multi-Depth JSON Parsing:** Efficiently store nested values using DFS.
- **Supports Conditional Data Extraction:** Extract values based on specific API response conditions.

## Project Structure
```plaintext
api-testing-framework
    ├── controller/               # Core logic (Do not modify)
    ├── regions/                  # Region-specific folder (LATAM, India, etc.)
    │   ├── latam/                # Example region folder
    │   │   ├── scenarios/        # Contains API testing scenarios
    │   │   │   ├── configs/      # Stores global and scenario-level configurations
    │   │   │   ├── scenarioName/ # Specific test scenario
    │   │   │   │   ├── requests/ # Stores API request curl files
    │   │   │   │   ├── dependency.json  # Scenario-specific configuration
    │   │   │   │   ├── execution_sequence.json  # Defines execution order
```

## Configuration Files
### Global Configuration (`configs/global_config.json`)
- Stores generic configurations across all scenarios.
- Includes **store-replace** mappings for API response handling.

### Scenario-Level Configuration (`scenarioName/dependency.json`)
- Defines scenario-specific settings.
- Overrides values from `global_config.json` when keys overlap.

## Execution Flow
1. **Setup Requests**
   - Store API requests as `.curl` files inside `requests/`.
   - Use **unique filenames** for different endpoints.

2. **Define Dependencies**
   - `dependency.json` specifies scenario-specific settings and dependencies.

3. **Specify Execution Order**
   - `execution_sequence.json` determines the order of API execution.

4. **Run Tests**
   - The framework merges configurations, executes requests, and processes results dynamically.

## Store & Replace Logic
### **Example API Response**
```json
{
  "inventories": [
    {
      "routeId": "R123",
      "operatorId": "O456",
      "busDetails": {
        "busType": "Sleeper"
      }
    },
    {
      "routeId": "R789",
      "operatorId": "O999",
      "busDetails": {
        "busType": "Semi-Sleeper"
      }
    }
  ]
}
```

### **Stored Values**
```json
{
  "inventory": {
    "route_ids": ["R123", "R789"],
    "operator_ids": ["O456", "O999"]
  },
  "bus_details": {
    "types": ["Sleeper", "Semi-Sleeper"]
  }
}
```

### **Apply Conditions**
If a condition exists, only matched values are stored:
```json
"conditions": [
  {
    "key": "$.inventories[*].busDetails.busType",
    "expected_values": ["Sleeper"]
  }
]
```

### **Dynamic Request Replacement**
#### Before Replacement
```json
{
  "orderId": "replace_with_stored_value",
  "trip": {
    "selectedSeats": "replace_with_stored_seatNos"
  }
}
```

#### After Replacement
```json
{
  "orderId": "UUID12345",
  "trip": {
    "selectedSeats": ["S1", "S2"]
  }
}
```

## How to Run Tests
1. **Clone the Repository:**
   ```sh
   git clone https://github.com/vishnu1777/Chuck.git
   cd ChainApi
   ```
2. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run Tests:**
   ```sh
   python run_tests.py --region latam --scenario scenarioName
   ```

## Contribution Guidelines
1. **Fork the Repository**
2. **Create a Feature Branch:**
   ```sh
   git checkout -b feature-branch
   ```
3. **Commit Changes:**
   ```sh
   git commit -m "Add new test scenario"
   ```
4. **Push to GitHub:**
   ```sh
   git push origin feature-branch
   ```
5. **Create a Pull Request**

---

This structured API Testing Framework ensures **scalability**, **reusability**, and **automation-friendly workflows** for API validation. 🚀

