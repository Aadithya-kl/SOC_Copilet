# Synthetic attack datasets for correlation tests

ssh_brute_force_events = [
    {"timestamp": "2023-10-01T08:00:00Z", "action": "login_failed", "user": "root", "ip": "10.0.0.50"},
    {"timestamp": "2023-10-01T08:00:05Z", "action": "login_failed", "user": "root", "ip": "10.0.0.50"},
    {"timestamp": "2023-10-01T08:00:10Z", "action": "login_failed", "user": "admin", "ip": "10.0.0.50"},
    {"timestamp": "2023-10-01T08:00:15Z", "action": "login_success", "user": "admin", "ip": "10.0.0.50"},
    {"timestamp": "2023-10-01T08:01:00Z", "action": "process_started", "user": "admin", "process": "bash", "ip": "10.0.0.50"},
]

web_exploitation_events = [
    {"timestamp": "2023-10-01T09:00:00Z", "action": "http_request", "url": "/admin/config.php", "ip": "192.168.1.100"},
    {"timestamp": "2023-10-01T09:00:05Z", "action": "http_request", "url": "/admin/upload.php", "ip": "192.168.1.100"},
    {"timestamp": "2023-10-01T09:01:00Z", "action": "file_created", "file": "/var/www/html/shell.php", "user": "www-data"},
]

# These fixtures can be loaded during tests to evaluate the deterministic correlation engine.
