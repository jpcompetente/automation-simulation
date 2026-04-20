import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runner import run_system

if __name__ == "__main__":
    run_system()