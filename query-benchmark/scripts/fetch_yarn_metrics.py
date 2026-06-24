import requests
import sys
import json

def get_latest_yarn_app():
    try:
        response = requests.get('http://localhost:8088/ws/v1/cluster/apps')
        apps = response.json().get('apps', {}).get('app', [])
        if not apps:
            return None
            
        # Filter for finished apps and sort by finished time descending
        finished_apps = [a for a in apps if a['state'] == 'FINISHED']
        finished_apps.sort(key=lambda x: x['finishedTime'], reverse=True)
        
        return finished_apps[0] if finished_apps else None
    except Exception as e:
        print(f"Error fetching YARN metrics: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_yarn_metrics.py <output_file>")
        sys.exit(1)
        
    outfile = sys.argv[1]
    app = get_latest_yarn_app()
    
    with open(outfile, 'a') as f:
        f.write("\n\n=== AUTOMATED YARN DISTRIBUTED METRICS ===\n")
        if app:
            f.write("These metrics represent the actual CPU and Memory consumed by the worker nodes across the cluster.\n\n")
            f.write(f"Application ID: {app.get('id', 'N/A')}\n")
            f.write(f"Application Type: {app.get('applicationType', 'N/A')}\n")
            f.write(f"State: {app.get('state', 'N/A')} / {app.get('finalStatus', 'N/A')}\n")
            f.write(f"Elapsed Time (ms): {app.get('elapsedTime', 0)}\n")
            f.write(f"Distributed Memory Seconds (MB-sec): {app.get('memorySeconds', 0)}\n")
            f.write(f"Distributed VCore Seconds (vcore-sec): {app.get('vcoreSeconds', 0)}\n")
            f.write(f"Allocated Containers: {app.get('allocatedContainers', 0)}\n")
        else:
            f.write("No finished YARN application found.\n")
