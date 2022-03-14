import os
import time
from dotenv import load_dotenv


if os.environ.get("RUN_LOCAL") is None:
    print("Retrieving additional environment variables")
    load_dotenv("../db.env")

print("Starting main thread")
time.sleep(2)

# Delay import until after environment variables have been well-established
from app.sub import main

main()
