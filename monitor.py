import psutil
import platform
import wmi  # Standard on Windows for hardware querying
import os
import time

# Try importing vendor-specific libraries
try:
    import GPUtil
except ImportError:
    GPUtil = None

try:
    from pyadl import ADLManager
except ImportError:
    ADLManager = None

class HardwareMonitor:
    def __init__(self):
        self.w = wmi.WMI()
        self.gpu_brand = self._detect_gpu_brand()
        print(f"Monitor Initialized. Detected GPU: {self.gpu_brand}")

    def _detect_gpu_brand(self):
        """Checks the Windows Management Instrumentation for GPU name."""
        try:
            gpu_info = self.w.Win32_VideoController()[0].Name.upper()
            if "NVIDIA" in gpu_info: return "NVIDIA"
            if "AMD" in gpu_info or "RADEON" in gpu_info: return "AMD"
        except Exception:
            return "Generic"
        return "Generic"

    def get_cpu_stats(self):
        """Returns CPU usage percentage."""
        # interval=None is best for recurring calls in a loop
        return psutil.cpu_percent(interval=None)

    def get_ram_stats(self):
        """Returns RAM usage % and available GB."""
        mem = psutil.virtual_memory()
        return mem.percent, round(mem.available / (1024**3), 2)

    def get_gpu_stats(self):
        """Returns (Load %, Temp) using WMI for AMD/Generic and GPUtil for NVIDIA."""
        if self.gpu_brand == "NVIDIA" and GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return round(gpus[0].load * 100, 1), gpus[0].temperature
            except Exception:
                pass

        # Stable fallback for AMD or if NVIDIA/GPUtil fails
        try:
            # Query Windows Performance Counters for GPU Usage
            # This works for almost all modern GPUs on Windows
            for usage in self.w.Win32_PerfFormattedData_GPUPerformanceAnalyzer_GPUEngine():
                if "Utilization Percentage" in usage.Properties_:
                    load = usage.UtilizationPercentage
                    # WMI doesn't always provide temp easily for AMD, 
                    # so we'll return 0 for temp if it's not found
                    return float(load), 0 
        except Exception:
            pass
        
        return 0, 0

    def get_disk_info(self):
        """Returns a list of dictionaries for all fixed drives."""
        disks = []
        for part in psutil.disk_partitions():
            if 'fixed' in part.opts:
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disks.append({
                        "device": part.device,
                        "percent": usage.percent,
                        "free": round(usage.free / (1024**3), 1)
                    })
                except PermissionError:
                    continue
        return disks

    def get_system_vitals(self):
        """Calculates stats, prints them to console, and returns data dict."""
        # Cache values to ensure print and return use the same data point
        cpu = self.get_cpu_stats()
        ram_pct, ram_free = self.get_ram_stats()
        gpu_load, gpu_temp = self.get_gpu_stats()
        disks = self.get_disk_info()

        # Console Output
        print(f"CPU: {cpu}% | RAM: {ram_pct}% ({ram_free}GB Free) | GPU: {gpu_load}% @ {gpu_temp}°C")
        
        return {
            "cpu": cpu,
            "ram_pct": ram_pct,
            "ram_free": ram_free,
            "gpu_load": gpu_load,
            "gpu_temp": gpu_temp,
            "disks": disks
        }

