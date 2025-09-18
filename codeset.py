import subprocess
import os
import tempfile
import shutil
import time

def count_python_lines(repo_path: str) -> int:
    total_lines = 0
    for root, _, files in os.walk(repo_path):
        for f in files:
            if f.endswith(".py"):
                file_path = os.path.join(root, f)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                        total_lines += sum(1 for _ in fh)
                except Exception:
                    continue
    return total_lines

def grade_repo(repo_url: str):
    start = time.perf_counter()
    temp_dir = tempfile.mkdtemp()
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(temp_dir, repo_name)

    try:
        subprocess.run(["git", "clone", repo_url, repo_path], check=True)
        result = subprocess.run(
            ["flake8", repo_path, "--count", "--exit-zero"],
            capture_output=True,
            text=True
        )
        
        try:
            violations = int(result.stdout.strip().split()[-1])
        except Exception:
            violations = 0

        loc = count_python_lines(repo_path)
        if loc == 0:
            return 0.0, time.perf_counter() - start

        violations_per_kloc = violations / (loc / 1000)

        max_tolerable = 50
        score = max(0.0, 1 - (violations_per_kloc / max_tolerable))
        score = round(min(score, 1.0), 3)

    finally:
        shutil.rmtree(temp_dir)

    latency = time.perf_counter() - start
    return score, latency

repo_url = "https://github.com/SkyworkAI/Matrix-Game.git"
score, latency = grade_repo(repo_url)
weighted_score = score * 0.15

print(f"Code quality score: {score}")
print(f"Weighted Score (0.15): {weighted_score}")
print(f"Latency: {latency:.2f} seconds")
