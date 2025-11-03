from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import shutil
import uuid
import json

app = FastAPI()

class EvaluationRequest(BaseModel):
    repo_url: str
    model_type: str  # e.g., "classification", "regression"

@app.post("/evaluate")
def evaluate_model(req: EvaluationRequest):
    # Step 1: Setup temp directory
    repo_id = str(uuid.uuid4())
    clone_path = f"temp_repos/{repo_id}"
    os.makedirs(clone_path, exist_ok=True)

    try:
        # Step 2: Clone repo
        subprocess.run(
            ["git", "clone", req.repo_url, clone_path],
            check=True
        )

        # Step 3: Assume eval script exists: `python evaluate.py --output results.json`
        eval_script = os.path.join(clone_path, "evaluate.py")
        results_path = os.path.join(clone_path, "results.json")

        if not os.path.isfile(eval_script):
            raise HTTPException(status_code=404, detail="evaluate.py not found in repo")

        subprocess.run(
            ["python", eval_script, "--output", results_path],
            check=True,
            cwd=clone_path
        )

        # Step 4: Load evaluation results
        with open(results_path, "r") as f:
            results = json.load(f)

        return {
            "status": "success",
            "model_type": req.model_type,
            "metrics": results
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Step 5: Cleanup
        shutil.rmtree(clone_path, ignore_errors=True)

