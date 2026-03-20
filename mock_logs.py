import random
from datetime import datetime, timedelta

def generate_logs(scenario="cpu_spike"):
    base_time = datetime.now() - timedelta(minutes=30)
    
    scenarios = {
        "cpu_spike": [
            "[INFO]  2024-01-15 02:11:03 Application started successfully",
            "[INFO]  2024-01-15 02:11:45 Handling 450 concurrent requests",
            "[WARN]  2024-01-15 02:13:12 Response time 4200ms exceeds threshold",
            "[ERROR] 2024-01-15 02:14:33 java.lang.OutOfMemoryError: Java heap space",
            "[ERROR] 2024-01-15 02:14:34 GC overhead limit exceeded - JVM spending 97% in GC",
            "[ERROR] 2024-01-15 02:14:35 Health check failed for i-0abc123",
            "[ERROR] 2024-01-15 02:14:36 Health check failed for i-0abc123",
            "[ERROR] 2024-01-15 02:14:37 Target removed from load balancer",
            "[ERROR] 2024-01-15 02:14:38 java.lang.OutOfMemoryError: Java heap space",
            "[WARN]  2024-01-15 02:14:39 CPU utilization at 95% on i-0abc123",
        ],
        "rds_connection": [
            "[INFO]  2024-01-15 03:00:01 Processing order batch job started",
            "[INFO]  2024-01-15 03:00:45 Connected to RDS successfully",
            "[WARN]  2024-01-15 03:02:11 Connection pool at 85% capacity",
            "[WARN]  2024-01-15 03:03:22 Connection pool at 95% capacity",
            "[ERROR] 2024-01-15 03:04:01 Too many connections - pool exhausted (max=100)",
            "[ERROR] 2024-01-15 03:04:02 Connection refused: RDS endpoint unreachable",
            "[ERROR] 2024-01-15 03:04:03 Failed to process order #45821 - DB unavailable",
            "[ERROR] 2024-01-15 03:04:04 Failed to process order #45822 - DB unavailable",
            "[ERROR] 2024-01-15 03:04:05 500 error rate at 35% - payment service degraded",
            "[WARN]  2024-01-15 03:04:06 Retry attempt 3/3 failed for order processing",
        ],
        "disk_full": [
            "[INFO]  2024-01-15 04:00:00 Log rotation skipped - already running",
            "[WARN]  2024-01-15 04:15:00 Disk usage at 80% on /dev/xvda1",
            "[WARN]  2024-01-15 04:30:00 Disk usage at 88% on /dev/xvda1",
            "[ERROR] 2024-01-15 04:45:00 Disk usage at 95% on /dev/xvda1",
            "[ERROR] 2024-01-15 04:46:00 Failed to write log file - no space left on device",
            "[ERROR] 2024-01-15 04:46:01 Database write failed - no space left on device",
            "[ERROR] 2024-01-15 04:46:02 Application crash - unable to write temp files",
            "[ERROR] 2024-01-15 04:46:03 Health check failed - application unresponsive",
        ]
    }
    
    logs = scenarios.get(scenario, scenarios["cpu_spike"])
    error_warn_only = [l for l in logs if "[ERROR]" in l or "[WARN]" in l]
    return error_warn_only[-50:]

def get_log_string(scenario="cpu_spike"):
    logs = generate_logs(scenario)
    return "\n".join(logs)