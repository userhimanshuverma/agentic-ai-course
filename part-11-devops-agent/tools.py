"""
Part 11: DevOps Monitoring Agent - Tools Module
===============================================

This module contains all the system monitoring tools using psutil.
Each tool is:
- Well-documented with docstrings
- Includes error handling
- Returns structured data
- Has retry logic support

Tools available:
- get_cpu_metrics(): Monitor CPU usage and frequency
- get_memory_metrics(): Monitor RAM usage
- get_disk_metrics(): Monitor disk usage
- get_network_metrics(): Monitor network I/O
- get_process_metrics(): Monitor top processes
- detect_anomalies(): Detect abnormal spikes
"""

import psutil
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CPUMetrics:
    """Structured CPU metrics data"""
    percent: float
    frequency_mhz: float
    core_count: int
    per_cpu_percent: List[float]
    timestamp: str
    status: str  # 'normal', 'warning', 'critical'


@dataclass
class MemoryMetrics:
    """Structured memory metrics data"""
    total_gb: float
    available_gb: float
    used_gb: float
    percent: float
    timestamp: str
    status: str


@dataclass
class DiskMetrics:
    """Structured disk metrics data"""
    total_gb: float
    used_gb: float
    free_gb: float
    percent: float
    mount_point: str
    timestamp: str
    status: str


@dataclass
class AnomalyResult:
    """Anomaly detection result"""
    is_anomaly: bool
    severity: str  # 'low', 'medium', 'high', 'critical'
    metric_type: str
    current_value: float
    threshold: float
    message: str
    suggestions: List[str]


class SystemMonitor:
    """
    System monitoring tool class.
    
    This class provides methods to monitor various system metrics
    using the psutil library. All methods include error handling
    and return structured data.
    
    Example:
        monitor = SystemMonitor()
        cpu = monitor.get_cpu_metrics()
        print(f"CPU: {cpu.percent}%")
    """
    
    def __init__(self):
        """Initialize the system monitor"""
        self.thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 80.0,
            'memory_critical': 95.0,
            'disk_warning': 80.0,
            'disk_critical': 95.0
        }
        logger.info("SystemMonitor initialized")
    
    def get_cpu_metrics(self, interval: float = 1.0) -> CPUMetrics:
        """
        Get current CPU metrics.
        
        Args:
            interval: Time to wait for CPU percent calculation (seconds)
        
        Returns:
            CPUMetrics object with CPU data
        
        Example:
            cpu = monitor.get_cpu_metrics()
            print(f"CPU Usage: {cpu.percent}%")
            print(f"Status: {cpu.status}")
        """
        try:
            # Get CPU percent (blocks for 'interval' seconds)
            cpu_percent = psutil.cpu_percent(interval=interval)
            per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # Get CPU frequency
            freq = psutil.cpu_freq()
            freq_mhz = freq.current if freq else 0.0
            
            # Get core count
            core_count = psutil.cpu_count()
            
            # Determine status
            if cpu_percent >= self.thresholds['cpu_critical']:
                status = 'critical'
            elif cpu_percent >= self.thresholds['cpu_warning']:
                status = 'warning'
            else:
                status = 'normal'
            
            metrics = CPUMetrics(
                percent=round(cpu_percent, 2),
                frequency_mhz=round(freq_mhz, 2),
                core_count=core_count,
                per_cpu_percent=[round(x, 2) for x in per_cpu],
                timestamp=datetime.now().isoformat(),
                status=status
            )
            
            logger.info(f"CPU metrics collected: {metrics.percent}% ({status})")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get CPU metrics: {e}")
            # Return safe defaults on error
            return CPUMetrics(
                percent=0.0,
                frequency_mhz=0.0,
                core_count=0,
                per_cpu_percent=[],
                timestamp=datetime.now().isoformat(),
                status='error'
            )
    
    def get_memory_metrics(self) -> MemoryMetrics:
        """
        Get current memory (RAM) metrics.
        
        Returns:
            MemoryMetrics object with memory data
        
        Example:
            mem = monitor.get_memory_metrics()
            print(f"Memory: {mem.percent}% used")
            print(f"Available: {mem.available_gb} GB")
        """
        try:
            mem = psutil.virtual_memory()
            
            # Convert bytes to GB
            total_gb = mem.total / (1024**3)
            available_gb = mem.available / (1024**3)
            used_gb = mem.used / (1024**3)
            
            # Determine status
            if mem.percent >= self.thresholds['memory_critical']:
                status = 'critical'
            elif mem.percent >= self.thresholds['memory_warning']:
                status = 'warning'
            else:
                status = 'normal'
            
            metrics = MemoryMetrics(
                total_gb=round(total_gb, 2),
                available_gb=round(available_gb, 2),
                used_gb=round(used_gb, 2),
                percent=round(mem.percent, 2),
                timestamp=datetime.now().isoformat(),
                status=status
            )
            
            logger.info(f"Memory metrics collected: {metrics.percent}% ({status})")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get memory metrics: {e}")
            return MemoryMetrics(
                total_gb=0.0,
                available_gb=0.0,
                used_gb=0.0,
                percent=0.0,
                timestamp=datetime.now().isoformat(),
                status='error'
            )
    
    def get_disk_metrics(self, path: str = '/') -> DiskMetrics:
        """
        Get disk usage metrics for a given path.
        
        Args:
            path: Path to check disk usage for (default: root)
        
        Returns:
            DiskMetrics object with disk data
        
        Example:
            disk = monitor.get_disk_metrics('/')
            print(f"Disk: {disk.percent}% used")
            print(f"Free: {disk.free_gb} GB")
        """
        try:
            # Handle Windows paths
            if psutil.WINDOWS and path == '/':
                path = 'C:\\'
            
            disk = psutil.disk_usage(path)
            
            # Convert bytes to GB
            total_gb = disk.total / (1024**3)
            used_gb = disk.used / (1024**3)
            free_gb = disk.free / (1024**3)
            
            # Determine status
            if disk.percent >= self.thresholds['disk_critical']:
                status = 'critical'
            elif disk.percent >= self.thresholds['disk_warning']:
                status = 'warning'
            else:
                status = 'normal'
            
            metrics = DiskMetrics(
                total_gb=round(total_gb, 2),
                used_gb=round(used_gb, 2),
                free_gb=round(free_gb, 2),
                percent=round(disk.percent, 2),
                mount_point=path,
                timestamp=datetime.now().isoformat(),
                status=status
            )
            
            logger.info(f"Disk metrics collected: {metrics.percent}% ({status})")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get disk metrics for {path}: {e}")
            return DiskMetrics(
                total_gb=0.0,
                used_gb=0.0,
                free_gb=0.0,
                percent=0.0,
                mount_point=path,
                timestamp=datetime.now().isoformat(),
                status='error'
            )
    
    def get_network_metrics(self) -> Dict[str, Any]:
        """
        Get network I/O metrics.
        
        Returns:
            Dictionary with network statistics
        
        Example:
            net = monitor.get_network_metrics()
            print(f"Bytes sent: {net['bytes_sent_mb']} MB")
        """
        try:
            net_io = psutil.net_io_counters()
            
            # Convert to MB for readability
            bytes_sent_mb = net_io.bytes_sent / (1024**2)
            bytes_recv_mb = net_io.bytes_recv / (1024**2)
            
            metrics = {
                'bytes_sent_mb': round(bytes_sent_mb, 2),
                'bytes_recv_mb': round(bytes_recv_mb, 2),
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errors_in': net_io.errin,
                'errors_out': net_io.errout,
                'timestamp': datetime.now().isoformat(),
                'status': 'normal'
            }
            
            logger.info(f"Network metrics collected")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get network metrics: {e}")
            return {
                'bytes_sent_mb': 0.0,
                'bytes_recv_mb': 0.0,
                'packets_sent': 0,
                'packets_recv': 0,
                'errors_in': 0,
                'errors_out': 0,
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }
    
    def get_process_metrics(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get top processes by CPU usage.
        
        Args:
            top_n: Number of top processes to return
        
        Returns:
            List of process dictionaries
        
        Example:
            processes = monitor.get_process_metrics(3)
            for p in processes:
                print(f"{p['name']}: {p['cpu_percent']}%")
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu_percent': round(pinfo['cpu_percent'], 2),
                        'memory_percent': round(pinfo['memory_percent'], 2) if pinfo['memory_percent'] else 0.0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and get top N
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            top_processes = processes[:top_n]
            
            logger.info(f"Process metrics collected: {len(top_processes)} processes")
            return top_processes
            
        except Exception as e:
            logger.error(f"Failed to get process metrics: {e}")
            return []
    
    def detect_anomalies(self, metrics_history: List[Dict[str, Any]]) -> List[AnomalyResult]:
        """
        Detect anomalies in metrics history.
        
        Args:
            metrics_history: List of metric snapshots over time
        
        Returns:
            List of detected anomalies
        
        Example:
            history = [{'cpu': 45}, {'cpu': 95}]  # Spike!
            anomalies = monitor.detect_anomalies(history)
        """
        anomalies = []
        
        if len(metrics_history) < 2:
            return anomalies
        
        try:
            # Get latest and previous metrics
            latest = metrics_history[-1]
            previous = metrics_history[-2]
            
            # Check CPU spike
            if 'cpu' in latest and 'cpu' in previous:
                cpu_diff = latest['cpu']['percent'] - previous['cpu']['percent']
                if cpu_diff > 30:  # 30% spike
                    anomalies.append(AnomalyResult(
                        is_anomaly=True,
                        severity='high' if cpu_diff > 50 else 'medium',
                        metric_type='cpu',
                        current_value=latest['cpu']['percent'],
                        threshold=previous['cpu']['percent'],
                        message=f"CPU spike detected: +{cpu_diff:.1f}%",
                        suggestions=[
                            "Check for runaway processes",
                            "Consider restarting high-CPU services",
                            "Scale up if sustained"
                        ]
                    ))
            
            # Check memory spike
            if 'memory' in latest and 'memory' in previous:
                mem_diff = latest['memory']['percent'] - previous['memory']['percent']
                if mem_diff > 20:  # 20% spike
                    anomalies.append(AnomalyResult(
                        is_anomaly=True,
                        severity='high' if mem_diff > 40 else 'medium',
                        metric_type='memory',
                        current_value=latest['memory']['percent'],
                        threshold=previous['memory']['percent'],
                        message=f"Memory spike detected: +{mem_diff:.1f}%",
                        suggestions=[
                            "Check for memory leaks",
                            "Restart memory-intensive applications",
                            "Consider adding more RAM"
                        ]
                    ))
            
            logger.info(f"Anomaly detection complete: {len(anomalies)} anomalies found")
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all system metrics in one call.
        
        Returns:
            Dictionary with all metrics
        
        Example:
            all_metrics = monitor.get_all_metrics()
            print(f"CPU: {all_metrics['cpu'].percent}%")
            print(f"Memory: {all_metrics['memory'].percent}%")
        """
        logger.info("Collecting all system metrics...")
        
        return {
            'cpu': self.get_cpu_metrics(interval=0.5),
            'memory': self.get_memory_metrics(),
            'disk': self.get_disk_metrics(),
            'network': self.get_network_metrics(),
            'processes': self.get_process_metrics(top_n=5),
            'timestamp': datetime.now().isoformat()
        }


# Convenience function for direct usage
def get_monitor() -> SystemMonitor:
    """Get a configured SystemMonitor instance"""
    return SystemMonitor()


if __name__ == "__main__":
    # Demo when running this file directly
    print("=" * 60)
    print("DevOps Monitoring Agent - Tools Demo")
    print("=" * 60)
    
    monitor = SystemMonitor()
    
    # Get all metrics
    print("\n1. CPU Metrics:")
    cpu = monitor.get_cpu_metrics()
    print(f"   Usage: {cpu.percent}%")
    print(f"   Cores: {cpu.core_count}")
    print(f"   Status: {cpu.status}")
    
    print("\n2. Memory Metrics:")
    mem = monitor.get_memory_metrics()
    print(f"   Used: {mem.used_gb} GB / {mem.total_gb} GB")
    print(f"   Usage: {mem.percent}%")
    print(f"   Status: {mem.status}")
    
    print("\n3. Disk Metrics:")
    disk = monitor.get_disk_metrics()
    print(f"   Used: {disk.used_gb} GB / {disk.total_gb} GB")
    print(f"   Free: {disk.free_gb} GB")
    print(f"   Usage: {disk.percent}%")
    print(f"   Status: {disk.status}")
    
    print("\n4. Top Processes:")
    processes = monitor.get_process_metrics(3)
    for p in processes:
        print(f"   {p['name']}: CPU {p['cpu_percent']}%")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
