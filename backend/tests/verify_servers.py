import subprocess
import time
import sys
import httpx

def main():
    print("Testing backend startup with uvicorn on 0.0.0.0:8000...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd="backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    server_ready = False
    for attempt in range(15):
        time.sleep(1)
        try:
            r = httpx.get("http://127.0.0.1:8000/health", timeout=2.0)
            if r.status_code == 200:
                print("Backend healthy! HTTP Status:", r.status_code)
                print("Response:", r.json())
                server_ready = True
                break
        except Exception:
            continue

    if not server_ready:
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=3)
        print("Backend failed to start. STDOUT:", stdout, "STDERR:", stderr)
        sys.exit(1)

    proc.terminate()
    proc.wait(timeout=3)
    print("Backend startup verification succeeded!")

if __name__ == "__main__":
    main()
