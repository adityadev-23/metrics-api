import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 1. Strict CORS Policy
# Only the assigned origin is allowed. No wildcards.
ALLOWED_ORIGIN = "https://dash-0ezgwq.example.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"], # Preflight OPTIONS will succeed for the allowed origin
    allow_headers=["*"],
)

# 2. Required Middleware Headers (X-Request-ID and X-Process-Time)
@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())
    
    # Process the request
    response = await call_next(request)
    
    # Calculate process time
    process_time = time.perf_counter() - start_time
    
    # Inject headers into the response
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    return response

# 3. The /stats Endpoint
@app.get("/stats")
def get_stats(values: str):
    # Parse the comma-separated integers
    try:
        nums = [int(v.strip()) for v in values.split(",") if v.strip()]
    except ValueError:
        return {"error": "Invalid input. Expected comma-separated integers."}

    if not nums:
        return {"error": "No values provided."}

    # Compute descriptive statistics
    n_count = len(nums)
    total_sum = sum(nums)
    min_val = min(nums)
    max_val = max(nums)
    mean_val = total_sum / n_count

    return {
        "email": "25f2001158@ds.study.iitm.ac.in",  # REMEMBER TO CHANGE THIS
        "count": n_count,
        "sum": total_sum,
        "min": min_val,
        "max": max_val,
        "mean": mean_val
    } 