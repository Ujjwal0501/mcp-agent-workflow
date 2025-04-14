import threading
import time
import subprocess
import asyncio
import websockets
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

proc_list = []

def run_script(script_path):
    """Function to run a Python script."""
    try:
        stdout_file = open("stdout.log", "w")
        stderr_file = open("stderr.log", "w")
        stdin_file = open("stdin.log", "r+")
        stdin_file.truncate(0)  # Erase contents of stdin.log
        stdout_file.truncate(0)  # Erase contents of stdout.log
        stderr_file.truncate(0)  # Erase contents of stderr.log
        process = subprocess.Popen(
            ['python', script_path],
            stdout=stdout_file,
            stderr=stderr_file,
            stdin=stdin_file
        )
        proc_list.append(process)
    except Exception as e:
        print(f"Failed to run script: {e}")

def monitor_script(script_path):
    """Function to start and monitor a Python script in a separate thread."""
    thread = threading.Thread(target=run_script, args=(script_path,))
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

@app.get("/stdout/")
async def script_output():
    try:
        with open("stdout.log", "r") as stdout_file:
            stdout_val = stdout_file.read()
        return {"stdout": stdout_val.encode()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run script: {e}")

@app.post("/stdin/")
async def script_input(input_data: str):
    try:
        with open("stdin.log", "a") as stdin_file:
            stdin_file.write(input_data)
        return {"message": "Input written to stdin.log successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write input: {e}")


if __name__ == "__main__":
    script_to_run = "src/agent.py"  # Replace with the path to your script
    monitor_script(script_to_run)
    uvicorn.run(app, host="0.0.0.0", port=8000)
