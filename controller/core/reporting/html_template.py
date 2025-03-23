HTML_TEMPLATE="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ scenario_name }} - Test Execution Report</title>
    <style>
        :root {
            --primary-color: #3498db;
            --success-color: #2ecc71;
            --warning-color: #f39c12;
            --error-color: #e74c3c;
            --info-color: #3498db;
            --debug-color: #27ae60;
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-color: #333333;
            --border-color: #e0e0e0;
        }

        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: var(--bg-color);
            margin: 0;
            padding: 20px;
            color: var(--text-color);
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: auto;
            background: var(--card-bg);
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 15px;
            margin-bottom: 20px;
        }

        .title {
            margin: 0;
            color: var(--primary-color);
            font-size: 24px;
        }

        .metadata {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid var(--primary-color);
        }

        .metadata-item {
            margin: 0;
        }

        .summary {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }

        .stat-card {
            flex: 1;
            min-width: 150px;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            background-color: white;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .stat-card h3 {
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 16px;
            color: #666;
        }

        .stat-value {
            font-size: 24px;
            font-weight: bold;
        }

        .total-cases {
            background-color: #f8f9fa;
            border-left: 4px solid var(--primary-color);
        }

        .passed-cases {
            background-color: #f8f9fa;
            border-left: 4px solid var(--success-color);
        }

        .failed-cases {
            background-color: #f8f9fa;
            border-left: 4px solid var(--error-color);
        }

        .pass-percentage {
            background-color: #f8f9fa;
            border-left: 4px solid var(--warning-color);
        }

        .total-logs {
            background-color: #f8f9fa;
            border-left: 4px solid var(--primary-color);
        }

        .info-logs {
            background-color: #f8f9fa;
            border-left: 4px solid var(--info-color);
        }

        .debug-logs {
            background-color: #f8f9fa;
            border-left: 4px solid var(--debug-color);
        }

        .error-logs {
            background-color: #f8f9fa;
            border-left: 4px solid var(--error-color);
        }

        .success-text { color: var(--success-color); }
        .warning-text { color: var(--warning-color); }
        .error-text { color: var(--error-color); }
        .info-text { color: var(--info-color); }
        .debug-text { color: var(--debug-color); }
        .primary-text { color: var(--primary-color); }

        .log-table-container {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
        }

        th, td {
            border: 1px solid var(--border-color);
            padding: 12px;
            text-align: left;
            word-wrap: break-word;
        }

        th {
            background: var(--primary-color);
            color: white;
            position: sticky;
            top: 0;
        }

        tr:nth-child(even) {
            background-color: #f9f9f9;
        }

        tr:hover {
            background-color: #f1f1f1;
        }

        .timestamp-col { width: 20%; }
        .level-col { width: 10%; }
        .message-col { width: 70%; }

        .info { color: var(--info-color); font-weight: 500; }
        .debug { color: var(--debug-color); font-weight: 500; }
        .error { 
            color: var(--error-color); 
            font-weight: bold;
        }

        .footer {
            margin-top: 25px;
            text-align: center;
            color: #666;
            font-size: 14px;
            padding-top: 15px;
            border-top: 1px solid var(--border-color);
        }

        /* Navigation */
        .nav-tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
        }

        .nav-tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }

        .nav-tab:hover {
            background-color: #f5f5f5;
        }

        .nav-tab.active {
            border-bottom: 3px solid var(--primary-color);
            font-weight: bold;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
            color: white;
            margin-left: 5px;
        }

        .badge-info {
            background-color: var(--info-color);
        }

        .badge-debug {
            background-color: var(--debug-color);
        }

        .badge-error {
            background-color: var(--error-color);
        }

        /* Accordion/Drawer for API and Channel details */
        .accordion {
            margin-bottom: 20px;
        }

        .accordion-item {
            margin-bottom: 10px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
        }

        .accordion-header {
            background-color: #f5f5f5;
            padding: 10px 15px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid transparent;
        }

        .accordion-header:hover {
            background-color: #e9e9e9;
        }

        .accordion-header.active {
            border-bottom: 1px solid var(--border-color);
        }

        .accordion-content {
            padding: 0;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }

        .accordion-content.active {
            padding: 15px;
            max-height: 500px;
        }

        .accordion-title {
            font-weight: bold;
            margin: 0;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .api-stat-card {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            text-align: center;
        }

        .api-stat-card h4 {
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 14px;
            color: #666;
        }

        .api-stat-value {
            font-size: 20px;
            font-weight: bold;
        }

        /* Status indicators */
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }

        .status-success {
            background-color: var(--success-color);
        }

        .status-warning {
            background-color: var(--warning-color);
        }

        .status-danger {
            background-color: var(--error-color);
        }

        @media (max-width: 768px) {
            .summary {
                flex-direction: column;
            }
            .stat-card {
                min-width: 100%;
            }
            .nav-tabs {
                flex-direction: column;
            }
            .nav-tab {
                border-bottom: none;
                border-left: 3px solid transparent;
            }
            .nav-tab.active {
                border-bottom: none;
                border-left: 3px solid var(--primary-color);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">Test Execution Report</h1>
            <div class="timestamp">Generated: {{ generation_timestamp }}</div>
        </div>

        <div class="metadata">
            <p class="metadata-item"><strong>Region:</strong> {{ region }}</p>
            <p class="metadata-item"><strong>Scenario:</strong> {{ scenario_name }}</p>
            <p class="metadata-item"><strong>Log File:</strong> {{ log_file }}</p>
        </div>

        <!-- Overall Test Results -->
        <h2>Overall Test Results</h2>
        <div class="summary">
            <div class="stat-card total-cases">
                <h3>Total Cases</h3>
                <div class="stat-value primary-text">{{ overall_stats.totalCases }}</div>
            </div>
            <div class="stat-card passed-cases">
                <h3>Passed Cases</h3>
                <div class="stat-value success-text">{{ overall_stats.totalPassed }}</div>
            </div>
            <div class="stat-card failed-cases">
                <h3>Failed Cases</h3>
                <div class="stat-value error-text">{{ overall_stats.failedCases }}</div>
            </div>
            <div class="stat-card pass-percentage">
                <h3>Pass Percentage</h3>
                <div class="stat-value warning-text">{{ "%.1f"|format(overall_stats.passPercentage) }}%</div>
            </div>
        </div>

        <!-- API/Channel Details Accordion -->
        {% if test_results %}
        <h2>API and Channel Details</h2>
        <div class="accordion">
            {% for api_channel, results in test_results.items() %}
            <div class="accordion-item">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <h3 class="accordion-title">
                        {% if results.passPercentage == 100 %}
                        <span class="status-indicator status-success"></span>
                        {% elif results.passPercentage >= 80 %}
                        <span class="status-indicator status-warning"></span>
                        {% else %}
                        <span class="status-indicator status-danger"></span>
                        {% endif %}
                        {{ api_channel }}
                    </h3>
                    <span>{{ "%.1f"|format(results.passPercentage) }}% Passed</span>
                </div>
                <div class="accordion-content">
                    <div class="stats-grid">
                        <div class="api-stat-card">
                            <h4>Total Cases</h4>
                            <div class="api-stat-value primary-text">{{ results.totalCases }}</div>
                        </div>
                        <div class="api-stat-card">
                            <h4>Passed Cases</h4>
                            <div class="api-stat-value success-text">{{ results.totalPassed }}</div>
                        </div>
                        <div class="api-stat-card">
                            <h4>Failed Cases</h4>
                            <div class="api-stat-value error-text">{{ results.failedCases }}</div>
                        </div>
                        <div class="api-stat-card">
                            <h4>Pass Percentage</h4>
                            <div class="api-stat-value warning-text">{{ "%.1f"|format(results.passPercentage) }}%</div>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Error Summary if errors exist -->
        {% if error_count > 0 %}
        <div class="error-summary" style="margin-bottom: 20px; padding: 15px; background-color: rgba(231, 76, 60, 0.1); border-left: 4px solid var(--error-color); border-radius: 4px;">
            <h3 style="margin-top: 0; color: var(--error-color);">⚠️ Errors Detected</h3>
            <ul style="margin-bottom: 0;">
                {% set error_shown = 0 %}
                {% for log in logs %}
                    {% if log.level == 'error' and error_shown < 3 %}
                        <li>{{ log.message }}</li>
                        {% set error_shown = error_shown + 1 %}
                    {% endif %}
                {% endfor %}
                {% if error_count > 3 %}
                    <li>... and {{ error_count - 3 }} more errors</li>
                {% endif %}
            </ul>
        </div>
        {% endif %}

        <!-- Log Summary -->
        <h2>Log Summary</h2>
        <div class="summary">
            <div class="stat-card total-logs" onclick="showTab('all-logs')">
                <h3>Total Logs</h3>
                <div class="stat-value">{{ log_count }}</div>
            </div>
            <div class="stat-card info-logs" onclick="showTab('info-logs')">
                <h3>Info Logs</h3>
                <div class="stat-value info-text">{{ info_count }}</div>
            </div>
            <div class="stat-card debug-logs" onclick="showTab('debug-logs')">
                <h3>Debug Logs</h3>
                <div class="stat-value debug-text">{{ debug_count }}</div>
            </div>
            <div class="stat-card error-logs" onclick="showTab('error-logs')">
                <h3>Error Logs</h3>
                <div class="stat-value error-text">{{ error_count }}</div>
            </div>
        </div>

        <div class="nav-tabs">
            <div id="all-tab" class="nav-tab active" onclick="showTab('all-logs')">All Logs <span class="badge badge-info">{{ log_count }}</span></div>
            <div id="info-tab" class="nav-tab" onclick="showTab('info-logs')">Info <span class="badge badge-info">{{ info_count }}</span></div>
            <div id="debug-tab" class="nav-tab" onclick="showTab('debug-logs')">Debug <span class="badge badge-debug">{{ debug_count }}</span></div>
            <div id="error-tab" class="nav-tab" onclick="showTab('error-logs')">Error <span class="badge badge-error">{{ error_count }}</span></div>
        </div>

        <!-- All Logs Tab -->
        <div id="all-logs" class="tab-content active">
            <div class="log-table-container">
                <table>
                    <thead>
                        <tr>
                            <th class="timestamp-col">Timestamp</th>
                            <th class="level-col">Level</th>
                            <th class="message-col">Message</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for log in logs %}
                        <tr>
                            <td>{{ log.timestamp }}</td>
                            <td class="{{ log.level }}">{{ log.level.upper() }}</td>
                            <td>{{ log.message }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Info Logs Tab -->
        <div id="info-logs" class="tab-content">
            <div class="log-table-container">
                <table>
                    <thead>
                        <tr>
                            <th class="timestamp-col">Timestamp</th>
                            <th class="level-col">Level</th>
                            <th class="message-col">Message</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for log in logs %}
                            {% if log.level == 'info' %}
                            <tr>
                                <td>{{ log.timestamp }}</td>
                                <td class="info">INFO</td>
                                <td>{{ log.message }}</td>
                            </tr>
                            {% endif %}
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Debug Logs Tab -->
        <div id="debug-logs" class="tab-content">
            <div class="log-table-container">
                <table>
                    <thead>
                        <tr>
                            <th class="timestamp-col">Timestamp</th>
                            <th class="level-col">Level</th>
                            <th class="message-col">Message</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for log in logs %}
                            {% if log.level == 'debug' %}
                            <tr>
                                <td>{{ log.timestamp }}</td>
                                <td class="debug">DEBUG</td>
                                <td>{{ log.message }}</td>
                            </tr>
                            {% endif %}
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Error Logs Tab -->
        <div id="error-logs" class="tab-content">
            <div class="log-table-container">
                <table>
                    <thead>
                        <tr>
                            <th class="timestamp-col">Timestamp</th>
                            <th class="level-col">Level</th>
                            <th class="message-col">Message</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for log in logs %}
                            {% if log.level == 'error' %}
                            <tr>
                                <td>{{ log.timestamp }}</td>
                                <td class="error">ERROR</td>
                                <td>{{ log.message }}</td>
                            </tr>
                            {% endif %}
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="footer">
            <p>© {{ generation_timestamp.split('-')[0] }} Test Automation Framework  | Generated for {{ scenario_name }} Test Runner</p>
        </div>
    </div>

    <script>
        function showTab(tabId) {
            // Hide all tab contents
            var tabContents = document.getElementsByClassName('tab-content');
            for (var i = 0; i < tabContents.length; i++) {
                tabContents[i].classList.remove('active');
            }
            
            // Deactivate all tabs
            var tabs = document.getElementsByClassName('nav-tab');
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            
            // Activate the selected tab and content
            document.getElementById(tabId).classList.add('active');
            
            // Activate corresponding tab button
            if (tabId === 'all-logs') {
                document.getElementById('all-tab').classList.add('active');
            } else if (tabId === 'info-logs') {
                document.getElementById('info-tab').classList.add('active');
            } else if (tabId === 'debug-logs') {
                document.getElementById('debug-tab').classList.add('active');
            } else if (tabId === 'error-logs') {
                document.getElementById('error-tab').classList.add('active');
            }
        }

        function toggleAccordion(header) {
            header.classList.toggle('active');
            var content = header.nextElementSibling;
            content.classList.toggle('active');
        }
    </script>
</body>
</html>"""