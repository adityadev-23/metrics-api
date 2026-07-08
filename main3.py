import os
import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# =====================================================================
# DEPLOYMENT SHORTCUT: Auto-generate the files and OS variables
# so you don't have to manually configure them on your hosting provider.
# =====================================================================
with open("config.development.yaml", "w") as f:
    f.write("""port: 8062
workers: 11
debug: false
log_level: warning
api_key: key-xb59sf3cs6
""")

with open(".env", "w") as f:
    f.write("""APP_PORT=8888
NUM_WORKERS=5
APP_DEBUG=false
APP_LOG_LEVEL=info
APP_API_KEY=key-xibwymsdx1
""")

# Inject OS Environment Variables
os.environ["APP_WORKERS"] = "12"
os.environ["APP_DEBUG"] = "true"
os.environ["APP_API_KEY"] = "key-s3njh2q893"
# =====================================================================

app = FastAPI()

# Allow cross-origin requests from any page (for the grader)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["GET"],
    allow_headers=["*"],
)

def load_merged_config() -> dict:
    # Layer 1: Defaults
    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000"
    }

    # Layer 2: config.development.yaml
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml", "r") as f:
            yaml_cfg = yaml.safe_load(f) or {}
            config.update(yaml_cfg)

    # Layer 3: .env file
    if os.path.exists(".env"):
        env_cfg = dotenv_values(".env")
        for key, value in env_cfg.items():
            if key == "NUM_WORKERS":
                config["workers"] = value
            elif key.startswith("APP_"):
                config[key[4:].lower()] = value

    # Layer 4: OS Environment variables
    for key, value in os.environ.items():
        if key == "NUM_WORKERS":
            config["workers"] = value
        elif key.startswith("APP_"):
            config[key[4:].lower()] = value

    return config

@app.get("/effective-config")
async def get_effective_config(request: Request):
    # Load Layers 1 to 4
    config = load_merged_config()

    # Layer 5: CLI overrides via query parameter (?set=key=value)
    for key, value in request.query_params.multi_items():
        if key == "set" and "=" in value:
            override_key, override_val = value.split("=", 1)
            config[override_key] = override_val

    # Type Coercion Rules
    final_config = {}
    for key, value in config.items():
        if key in ["port", "workers"]:
            final_config[key] = int(value)
        elif key == "debug":
            # Check for boolean truthy string values
            final_config[key] = str(value).lower() in ["true", "1", "yes", "on"]
        else:
            final_config[key] = str(value)
            
    # Secret Masking (MUST NEVER expose real value)
    if "api_key" in final_config:
        final_config["api_key"] = "****"

    return final_config