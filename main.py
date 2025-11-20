from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import shutil
import uuid
import json

app = FastAPI(
    title="SWE Model Evaluation Backend",
    description="Backend service for Phase 2 – evaluates GitHub model repos.",
    version="1.0.0"
)

# ============================
# Root Endpoint
# ============================
@app.get("/")
def root():
    return {"message": "FastAPI backend is running on EC2!"}

# ============================
# Health Check
# ============================
@app.get("/health")
def health():
    return {"status": "ok"}

# ============================
# Request Model
# ============================
class EvaluationRequest(BaseModel):
    repo_url: str          # GitHub repo URL
    model_type: str | None = None  # optional, for metadata

# ============================
# Evaluation Endpoint
# ============================
@app.post("/evaluate")
def evaluate(req: EvaluationRequest):

    # Create a unique temp folder
    repo_id = str(uuid.uuid4())
    clone_path = f"temp_repos/{repo_id}"
    os.makedirs(clone_path, exist_ok=True)

    try:
        # Step 1 — Clone Repository
        clone_cmd = ["git", "clone", req.repo_url, clone_path]
        result = subprocess.run(clone_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to clone repo: {result.stderr}"
            )

        # Step 2 — Verify evaluate.py exists
        eval_script = os.path.join(clone_path, "evaluate.py")
        if not os.path.isfile(eval_script):
            raise HTTPException(
                status_code=404,
                detail="evaluate.py was not found in the repo."
            )

        # Output file path
        results_path = os.path.join(clone_path, "results.json")

        # Step 3 — Run evaluation script
        eval_cmd = ["python3", eval_script, "--output", results_path]
        result = subprocess.run(
            eval_cmd, capture_output=True, text=True, cwd=clone_path
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Evaluation failed: {result.stderr}"
            )

        # Step 4 — Read results.json
        if not os.path.exists(results_path):
            raise HTTPException(
                status_code=500,
                detail="Evaluation script did not create results.json"
            )

        with open(results_path, "r") as f:
            metrics = json.load(f)

        return {
            "status": "success",
            "repo": req.repo_url,
            "model_type": req.model_type,
            "metrics": metrics
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Step 5 — Cleanup folder
        shutil.rmtree(clone_path, ignore_errors=True)
