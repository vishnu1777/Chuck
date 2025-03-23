import os
from jinja2 import Template
from logmanager.logger_manager import LoggerManager
from animations.spinner import Spinner
from bs4 import BeautifulSoup
from utils.file_utils import  delete_file
import datetime
from utils.global_store import GlobalStore
from reporting.html_template import HTML_TEMPLATE
class HTMLReportGenerator:
    def __init__(self, region, scenario_name, log_file="logs/test_logs.log"):
        self.region = region
        self.scenario_name = scenario_name
        self.HTML_TEMPLATE = HTML_TEMPLATE  # This is imported from reporting.html_template
        self.global_store = GlobalStore()
        self.LIBRARY_NAME = self.global_store.get_value("LIBRARY_NAME")
        self.chain_api_path = self._find_chainapi_dir()
        
        if not self.chain_api_path:
            raise FileNotFoundError("⚠️ Could not locate 'ChainApi' directory dynamically!")

        # Construct dynamic report path
        self.report_dir = os.path.join(self.chain_api_path, self.region, "reports", self.scenario_name)
        os.makedirs(self.report_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Add both versions of the report file path for compatibility
        self.report_file = os.path.join(self.report_dir, f"{self.scenario_name}_{timestamp}.html")
        self.report_file_path = self.report_file  # Add this for compatibility with the second version
        
        self.log_file = log_file
        self.logger = LoggerManager(self.__class__.__name__)
        self.spinner = Spinner()
        if os.path.exists(self.log_file):
            delete_file(self.log_file)
            self.spinner.console.print(f"✅ [bold green] Deleted previous log file [/bold green]: {self.report_file}")

    def _find_chainapi_dir(self):
        """Finds 'ChainApi' directory dynamically by walking up the tree."""
        current_path = os.path.abspath(__file__)  # Get current script path
        while current_path:
            parent_dir = os.path.dirname(current_path)
            if os.path.basename(parent_dir) == self.LIBRARY_NAME:
                return parent_dir
            if parent_dir == current_path:  # Stop if we reach root
                break
            current_path = parent_dir
        return None  # If not found

    def parse_logs(self):
        """Parses logs and extracts structured data safely."""
        logs = []
        info_count = debug_count = error_count = 0

        if not os.path.exists(self.log_file):
            self.logger.log_debug(f"⚠️ Log file not found: {self.log_file}")
            return logs, info_count, debug_count, error_count

        with open(self.log_file, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(" - ", maxsplit=3)  # Allow 4 parts

                if len(parts) < 4:
                    self.logger.log_debug(f"⚠️ Skipping malformed log line: {line.strip()}")
                    continue  # Skip badly formatted lines

                timestamp, logger_name, level, message = parts  # Extract correctly
                log_entry = {"timestamp": timestamp, "level": level.lower(), "message": message}
                logs.append(log_entry)

                if level.lower() == "info":
                    info_count += 1
                elif level.lower() == "debug":
                    debug_count += 1
                elif level.lower() == "error":
                    error_count += 1

        return logs, info_count, debug_count, error_count

    def calculate_overall_stats(self, test_results):
        """Calculate overall statistics from test results."""
        overall_stats = {
            'totalCases': 0,
            'totalPassed': 0,
            'failedCases': 0,
            'passPercentage': 0.0
        }
        
        # Sum up all statistics from each API/channel
        for api_channel, results in test_results.items():
            overall_stats['totalCases'] += results.get('totalCases', 0)
            overall_stats['totalPassed'] += results.get('totalPassed', 0)
            overall_stats['failedCases'] += results.get('failedCases', 0)
            
        # Calculate overall pass percentage
        if overall_stats['totalCases'] > 0:
            overall_stats['passPercentage'] = (overall_stats['totalPassed'] / overall_stats['totalCases']) * 100
        
        return overall_stats

    def generate_html_report(self, test_results=None):
        """Generates a styled HTML report from logs and test results."""
        logs, info_count, debug_count, error_count = self.parse_logs()
        
        # Calculate overall statistics from test results
        overall_stats = self.calculate_overall_stats(test_results) if test_results else {
            'totalCases': 0,
            'totalPassed': 0,
            'failedCases': 0,
            'passPercentage': 0.0
        }
        
        # Process test results by API and channel
        api_channel_results = test_results if test_results else {}
        
        generation_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        template = Template(self.HTML_TEMPLATE)
        report_content = template.render(
            logs=logs,
            log_count=len(logs),
            info_count=info_count,
            debug_count=debug_count,
            error_count=error_count,
            region=self.region,
            scenario_name=self.scenario_name,
            log_file=self.log_file,
            generation_timestamp=generation_timestamp,
            test_results=api_channel_results,
            overall_stats=overall_stats
        )

        with open(self.report_file, "w", encoding="utf-8") as file:
            file.write(report_content)

        self.spinner.console.print(f"✅ [bold green] HTML Report generated [/bold green]: {self.report_file}")
        return self.report_file_path

    def merge_reports(self, report_paths):
        """
        Merges multiple individual HTML reports into a single consolidated report.
        
        Args:
            report_paths (list): List of paths to individual HTML reports
            
        Returns:
            str: Path to the merged report file
        """
        if not report_paths:
            self.logger.log_error("No reports provided for merging")
            return None
            
        # Create merged report directory if needed
        merged_report_dir = os.path.join(self.chain_api_path, self.region, "reports", "merged_reports")
        os.makedirs(merged_report_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        merged_report_file = os.path.join(merged_report_dir, f"consolidated_report_{timestamp}.html")

        # Prepare merged data
        all_logs = []
        total_info = 0
        total_debug = 0
        total_error = 0
        merged_test_results = {}
        
        try:
            # Collect data from each report
            for report_path in report_paths:
                if os.path.exists(report_path):
                    with open(report_path, 'r', encoding='utf-8') as file:
                        html_content = file.read()
                    
                    # Use BeautifulSoup to parse HTML
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract scenario name
                    scenario_metadata = soup.select_one('.metadata')
                    scenario_name = "Unknown"
                    if scenario_metadata:
                        scenario_items = scenario_metadata.select('.metadata-item')
                        for item in scenario_items:
                            if 'Scenario:' in item.text:
                                scenario_name = item.text.replace('Scenario:', '').strip()
                    
                    # Extract API/channel results
                    api_items = soup.select('.accordion-item')
                    for api_item in api_items:
                        header = api_item.select_one('.accordion-header')
                        if header:
                            api_name = header.select_one('.accordion-title').text.strip()
                            api_stats = {}
                            
                            # Find stat values
                            stat_cards = api_item.select('.api-stat-card')
                            for card in stat_cards:
                                stat_title = card.select_one('h4').text.strip()
                                stat_value_el = card.select_one('.api-stat-value')
                                
                                if stat_value_el:
                                    # Extract numeric value
                                    stat_value = stat_value_el.text.strip()
                                    if '%' in stat_value:
                                        stat_value = float(stat_value.replace('%', ''))
                                    else:
                                        stat_value = int(stat_value)
                                        
                                    # Map to result key
                                    key_map = {
                                        'Total Cases': 'totalCases',
                                        'Passed Cases': 'totalPassed',
                                        'Failed Cases': 'failedCases',
                                        'Pass Percentage': 'passPercentage'
                                    }
                                    
                                    if stat_title in key_map:
                                        api_stats[key_map[stat_title]] = stat_value
                            
                            # Add to merged results
                            if api_name in merged_test_results:
                                # Merge with existing results
                                merged_test_results[api_name]['totalCases'] += api_stats.get('totalCases', 0)
                                merged_test_results[api_name]['totalPassed'] += api_stats.get('totalPassed', 0)
                                merged_test_results[api_name]['failedCases'] += api_stats.get('failedCases', 0)
                                
                                # Recalculate percentage
                                if merged_test_results[api_name]['totalCases'] > 0:
                                    merged_test_results[api_name]['passPercentage'] = (
                                        merged_test_results[api_name]['totalPassed'] / 
                                        merged_test_results[api_name]['totalCases'] * 100
                                    )
                            else:
                                merged_test_results[api_name] = api_stats
                    
                    # Extract logs
                    log_tables = soup.select('.log-table-container table')
                    for table in log_tables:
                        log_rows = table.select('tbody tr')
                        for row in log_rows:
                            cells = row.select('td')
                            if len(cells) >= 3:  # We expect at least timestamp, level, message
                                log_entry = {
                                    "timestamp": cells[0].text.strip(),
                                    "level": cells[1].text.strip().lower(),
                                    "message": cells[2].text.strip(),
                                    "scenario": scenario_name  # Add scenario name to identify source
                                }
                                all_logs.append(log_entry)
                                
                                # Count log levels
                                if log_entry["level"] == "info":
                                    total_info += 1
                                elif log_entry["level"] == "debug":
                                    total_debug += 1
                                elif log_entry["level"] == "error":
                                    total_error += 1
                else:
                    self.logger.log_error(f"Report file not found: {report_path}")
        except Exception as e:
            self.logger.log_error(f"Error merging reports: {str(e)}")
            
        # Sort logs by timestamp
        all_logs.sort(key=lambda x: x.get('timestamp', ''))
        
        # Calculate overall statistics
        overall_stats = self.calculate_overall_stats(merged_test_results)
        
        # Render the merged report
        generation_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        merged_template = Template(self.HTML_TEMPLATE)
        merged_report_content = merged_template.render(
            logs=all_logs,
            log_count=len(all_logs),
            info_count=total_info,
            debug_count=total_debug,
            error_count=total_error,
            region=self.region,
            scenario_name="Consolidated Report",
            log_file="Multiple Files",
            generation_timestamp=generation_timestamp,
            test_results=merged_test_results,
            overall_stats=overall_stats
        )
        
        # Write merged report to file
        with open(merged_report_file, "w", encoding="utf-8") as file:
            file.write(merged_report_content)
            
        self.spinner.console.print(f"✅ [bold green] Consolidated Report generated [/bold green]: {merged_report_file}")
        return merged_report_file