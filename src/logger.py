import json
import subprocess
from datetime import datetime
from time import strftime, localtime


def get_current_time():
    return datetime.now().strftime("%H:%M:%S.%f")[:-4]

def log_basic(message):
    print("[{0}] {1}".format(get_current_time(), message))

def log_batch(batch_name, results):
    passed = "\033[0;31m0\033[0;0m" if results[0] < 1 else "\033[0;32m{0}\033[0;0m".format(results[0])
    failed = "\033[0;32m0\033[0;0m" if results[1] < 1 else "\033[0;31m{0}\033[0;0m".format(results[1])
    print("[{0}] Batch {1} | PASSED: {2} | FAILED: {3}".format(get_current_time(), batch_name, passed, failed))

def log_final(results):
    passed = "\033[0;31m0\033[0;0m" if results[0] < 1 else "\033[0;32m{0}\033[0;0m".format(results[0])
    failed = "\033[0;32m0\033[0;0m" if results[1] < 1 else "\033[0;31m{0}\033[0;0m".format(results[1])
    print("[{0}] TOTAL -> PASSED: {1} | FAILED: {2}".format(get_current_time(), passed, failed))
    return 1 if results[1] > 0 else 0

def log(batch_name, test_name, type, message):
    type_draw = ""
    if type == 1:
        type_draw = "\033[0;31mFAILED"
    elif type == 2:
        type_draw = "\033[0;31mCRASHED"
    elif type == 3:
        type_draw = "\033[0;32mPASSED"
    type_draw += "\033[0;0m"
    print("[{0}] Test | {1} -> {2} | {3} {4}".format(get_current_time(), batch_name, test_name, type_draw, message))