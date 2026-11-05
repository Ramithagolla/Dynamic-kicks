import subprocess
import time
import sys
import httpx

def main():
    print("Testing frontend startup with Vite on port 5173...")
    proc = subprocess.Popen(
        ["npm.cmd", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"],
        cwd="frontend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    frontend_ready = False
    for attempt in range(15):
        time.sleep(1)
        try:
            r = httpx.get("http://127.0.0.1:5173", timeout=2.0)
            if r.status_code == 200:
                print("Frontend healthy! HTTP Status:", r.status_code)
                print("Title check in HTML:", "ThreatLens AI" in r.text or "vite" in r.text)
                frontend_ready = True
                break
        except Exception:
            continue

    if not frontend_ready:
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=3)
            print("Frontend failed to start. STDOUT:", stdout, "STDERR:", stderr)
        except Exception:
            pass
        sys.exit(1)

    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
    print("Frontend startup verification succeeded!")

if __name__ == "__main__":
    main()
