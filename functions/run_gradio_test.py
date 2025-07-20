
import os
import subprocess

my_env = os.environ.copy()
my_env["PYTHONIOENCODING"] = "utf-8"

subprocess.run(["python", "gradio_test.py"], env=my_env)
