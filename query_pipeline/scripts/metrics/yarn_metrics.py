"""
Metrics collector for the TPC-DS query benchmark.

Captures per-query metrics for both Spark and Hive engines:
  - wall-clock time (Python perf_counter)
  - peak RSS of the engine subprocess tree (psutil)
  - YARN application metrics via the ResourceManager REST API:
      vcoreSeconds, memorySeconds, allocatedMB, allocatedVCores, elapsedTime

The YARN "vcoreSeconds" / "memorySeconds" fields are only finalized once the
application reaches a FINISHED state, so we poll until the app finishes (or a
timeout) after the subprocess returns.

Usage (from run_queries.py):
    from yarn_metrics import YarnMetrics
    ym = YarnMetrics()
    proc = subprocess.Popen(...)
    ym.attach(proc.pid)            # start RSS monitoring while it runs
    out, _ = proc.communicate()
    metrics = ym.finalize(out)     # stop monitor + fetch YARN metrics
"""
import re
import time
import threading
import json
import urllib.request
import urllib.error

try:
    import psutil
except ImportError:
    psutil = None

_YARN_RM_URL = "http://localhost:8088/ws/v1/cluster/apps"
_APP_ID_RE = re.compile(r"application_\d+_\d+")
_POLL_INTERVAL = 2.0
_POLL_TIMEOUT = 300.0


class PeakRssMonitorThread(threading.Thread):
    """Polls the RSS of a process and its descendants, keeping the peak (bytes)."""

    def __init__(self, pid, interval=0.5):
        super().__init__(daemon=True)
        self.pid = pid
        self.interval = interval
        self.peak_bytes = 0
        self._stop_event = threading.Event()

    def run(self):
        if psutil is None:
            return
        try:
            root = psutil.Process(self.pid)
        except psutil.NoSuchProcess:
            return
        while not self._stop_event.is_set():
            total = 0
            try:
                total = root.memory_info().rss
                for child in root.children(recursive=True):
                    try:
                        total += child.memory_info().rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            if total > self.peak_bytes:
                self.peak_bytes = total
            self._stop_event.wait(self.interval)

    def stop(self):
        self._stop_event.set()

    def peak_mb(self):
        return self.peak_bytes / (1024.0 * 1024.0)


def extract_app_id(text):
    """Find the first YARN application id in process output."""
    if not text:
        return None
    m = _APP_ID_RE.search(text)
    return m.group(0) if m else None


def fetch_yarn_app(app_id, rm_url=_YARN_RM_URL, timeout=10):
    """Fetch a single app's metrics from the YARN RM REST API.

    Returns the 'app' dict or None if unavailable.
    """
    url = f"{rm_url}/{app_id}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return payload.get("app")
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError) as e:
        return {"_error": str(e)}


def wait_for_yarn_app(app_id, rm_url=_YARN_RM_URL,
                      timeout=_POLL_TIMEOUT, interval=_POLL_INTERVAL):
    """Poll YARN until the app is FINISHED/FAILED/KILLED, then return its metrics."""
    if not app_id:
        return None
    deadline = time.time() + timeout
    last = None
    terminal = {"FINISHED", "FAILED", "KILLED"}
    while time.time() < deadline:
        app = fetch_yarn_app(app_id, rm_url)
        if app and not app.get("_error"):
            last = app
            state = app.get("state", "")
            if state in terminal:
                return app
        time.sleep(interval)
    return last


class YarnMetrics:
    """High-level helper: monitors a subprocess and collects all metrics.

    Usage:
        ym = YarnMetrics()
        proc = subprocess.Popen(...)
        ym.attach(proc.pid)          # start RSS monitoring while it runs
        stdout, stderr = proc.communicate()
        metrics = ym.finalize(stdout.decode())
    """

    def __init__(self):
        self._monitor = None

    def attach(self, pid):
        """Start RSS monitoring on a live process. Call immediately after Popen."""
        self._monitor = PeakRssMonitorThread(pid)
        self._monitor.start()

    def finalize(self, stdout_text):
        """Stop the RSS monitor and fetch YARN application metrics.

        Returns a dict with peak_rss_mb and (if a YARN app id was found) the
        YARN resource metrics. YARN metrics are only finalized when the app
        reaches a terminal state, so this may poll for a while.
        """
        peak_mb = 0.0
        if self._monitor is not None:
            self._monitor.stop()
            self._monitor.join(timeout=2.0)
            peak_mb = self._monitor.peak_mb()
            self._monitor = None

        app_id = extract_app_id(stdout_text)
        yarn_app = wait_for_yarn_app(app_id) if app_id else None

        result = {
            "yarn_app_id": app_id or "",
            "yarn_elapsed_s": "",
            "vcore_seconds": "",
            "memory_mb_seconds": "",
            "allocated_mb": "",
            "allocated_vcores": "",
            "peak_rss_mb": round(peak_mb, 2),
        }
        if yarn_app:
            result.update({
                "yarn_elapsed_s": yarn_app.get("elapsedTime", ""),
                "vcore_seconds": yarn_app.get("vcoreSeconds", ""),
                "memory_mb_seconds": yarn_app.get("memorySeconds", ""),
                "allocated_mb": yarn_app.get("allocatedMB", ""),
                "allocated_vcores": yarn_app.get("allocatedVCores", ""),
            })
        return result
