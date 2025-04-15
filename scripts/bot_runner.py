import threading
import time
import subprocess
import asyncio
import websockets
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from fastapi import Request
import tempfile
import os

from generator import generate_agent_code

proc_list = []

def run_script(script_path, base_path):
    """Function to run a Python script."""
    try:
        stdout_file = open(f"{base_path}/stdout.log", "w")
        stderr_file = open(f"{base_path}/stderr.log", "w")
        if not os.path.exists(f"{base_path}/stdin.log"):
            open(f"{base_path}/stdin.log", "w").close()
        stdin_file = open(f"{base_path}/stdin.log", "r")
        process = subprocess.Popen(
            ['python', script_path],
            stdout=stdout_file,
            stderr=stderr_file,
            stdin=stdin_file
        )
        proc_list.append((process, base_path))
    except Exception as e:
        print(f"Failed to run script: {e}")

def monitor_script(script_path, base_path):
    """Function to start and monitor a Python script in a separate thread."""
    thread = threading.Thread(target=run_script, args=(script_path, base_path))
    thread.start()

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScriptInput(BaseModel):
    script_path: str

@app.get("/stdout/{id}")
async def script_output(id: int):
    if id >= len(proc_list):
        raise HTTPException(status_code=404, detail="Process not found")
    try:
        pdir = proc_list[id][1]
        with open(f"{pdir}/stdout.log", "r") as stdout_file:
            stdout_val = stdout_file.read()
        return {"stdout": stdout_val.encode()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run script: {e}")

@app.post("/stdin/{id}")
async def script_input(id: int, input_data: str):
    if id >= len(proc_list):
        raise HTTPException(status_code=404, detail="Process not found")
    try:
        pdir = proc_list[id][1]
        with open(f"{pdir}/stdin.log", "a") as stdin_file:
            stdin_file.write(input_data)
        return {"message": "Input written to stdin.log successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write input: {e}")

@app.post("/stop-all/")
async def stop_script():
    try:
        for proc, bp in proc_list:
            proc.terminate()
            proc.wait()  # Wait for the process to terminate
        proc_list.clear()  # Clear the list of processes
        return {"message": "Script stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop script: {e}")

@app.post("/start/")
async def stop_script():
    try:
        monitor_script("src/agent.py", "src")
        return {"message": "Script started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop script: {e}")

@app.post("/generate/{cidr}")
async def stop_script(cidr: str, request: Request):
    """Start a script with the given CIDR."""
    print(f"Starting script with CIDR: {cidr}")
    try:
        payload = await request.json()
        temp_dir = tempfile.mkdtemp(dir="/tmp")
        script_path = f"{temp_dir}/orchestrator.py"
        print(f"Script path: {script_path}")

        generate_agent_code(payload, base_path=temp_dir)
        monitor_script(script_path, temp_dir)

        return {"message": "Script started successfully", "id": len(proc_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
        for proc, bp in proc_list:
            proc.terminate()
            proc.wait()
        uvicorn_server = threading.enumerate()
        for thread in uvicorn_server:
            if thread.name == "MainThread":
                thread.join(timeout=1)
        print("All processes terminated.")
