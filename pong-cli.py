import subprocess
import time
import httpx

PID_FILE = "server_pids.txt"
PAUSE_FILE = "pause_signal.txt"

def start_instances(pong_time_ms):
    # Define the environment for instance1
    instance1_env = {
        "INSTANCE_ID": "instance1",
        "TARGET_URL": "http://localhost:8001/ping",
        "PONG_TIME_MS": pong_time_ms,
        "PORT": "8000"
    }

    # Define the environment for instance2
    instance2_env = {
        "INSTANCE_ID": "instance2",
        "TARGET_URL": "http://localhost:8000/ping",
        "PONG_TIME_MS": pong_time_ms,
        "PORT": "8001"
    }

    # Start instance1
    instance1_process = subprocess.Popen(["python", "server.py"], env={**os.environ, **instance1_env})

    # Start instance2
    instance2_process = subprocess.Popen(["python", "server.py"], env={**os.environ, **instance2_env})
    
    # Save PIDs to a file
    with open(PID_FILE, "w") as f:
        f.write(f"{instance1_process.pid}\n")
        f.write(f"{instance2_process.pid}\n")

    return instance1_process, instance2_process

def stop_instances():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            pids = f.readlines()
        
        for pid in pids:
            try:
                os.kill(int(pid.strip()), 15)  # Gracefully stop the process
                print(f"Stopped process with PID {pid.strip()}")
            except ProcessLookupError:
                print(f"No process found with PID {pid.strip()}")
        
        os.remove(PID_FILE)
    else:
        print("No running instances found.")
        
def pause_instances():
    with open(PAUSE_FILE, "w") as f:
        f.write("paused")

def resume_instances():
    if os.path.exists(PAUSE_FILE):
        os.remove(PAUSE_FILE)

if __name__ == "__main__":
    import os
    import sys
        
    if sys.argv[1] == "start":
        pong_time_ms = str(sys.argv[2])

        instance1_process, instance2_process = start_instances(pong_time_ms)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping instances...")
            instance1_process.terminate()
            instance2_process.terminate()
            instance1_process.wait()
            instance2_process.wait()
            print("Instances stopped.")
    elif sys.argv[1] == "pause":
        pause_instances()
    elif sys.argv[1] == "resume":
        resume_instances()
    elif sys.argv[1] == "stop":
        stop_instances()
    else:
        print(f"Unhandled command '{sys.argv[1]}'")