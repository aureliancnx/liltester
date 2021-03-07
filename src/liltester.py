import json
import subprocess
import time

import argparse
import requests
from logger import log, log_batch, log_basic, log_final
import os

results = [0, 0]

def run_process(args):
    try:
        out, err = None, None
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        excode = process.poll()

        return excode, out, err, None
    except OSError as e:
        return None, None, None, e

def launch_test(batch_name, exc, test):
    args = test['args']
    name = test['name']
    args.insert(0, exc)
    exp_ex = None
    ex, out, err, trace = run_process(args)
    if ex is None:
        log(batch_name, name, 1, "Got an unexpected error: {0}".format(trace))
        return
    if test['expected_stdout'] is not None:
        if out != test['expected_stdout']:
            log(batch_name, name, 1, "Difference: expected stdout: '{0}', but got: '{1}'".format(test['expected_stdout'], out))
            return False
    if test['expected_stderr'] is not None:
        if err != test['expected_stderr']:
            log(batch_name, name, 1, "Difference: expected stderr: {0}, but got: {1}".format(test['expected_stderr'], out))
            return False
    if test['expected_excode'] is None:
        log(batch_name, name, 1, "Config error: please provide a valid exit code")
        return False
    try:
        exp_ex = int(test['expected_excode'])
    except:
        log(batch_name, name, 1, "Config error: invalid exit code")
        return False
    if (ex == 11 or ex == 139) and exp_ex != ex:
        log(batch_name, name, 2, "Crashed. Expected exit code {0}, but got {1}".format(exp_ex, ex))
    elif exp_ex != ex:
        log(batch_name, name, 1, "Difference: expected exit code: {0}, but got {1}".format(exp_ex, ex))
        return False
    log(batch_name, name, 3, "")
    return True

def launch_tests(batch):
    global results
    batch_results = [0, 0]
    if not 'batch_name' in batch:
        print("Batch name not provided.")
        return 1
    if not 'tests' in batch:
        print("Tests not provided.")
        return 1
    if not 'exec' in batch:
        print("No executable provided.")
        return 1
    name = batch['batch_name']
    exc = batch['exec']
    tests = batch['tests']
    log_basic("Starting batch {0}... ({1} tests)".format(name, len(tests)))
    for test in tests:
        if not launch_test(name, exc, test):
            results[1] += 1
            batch_results[1] += 1
        else:
            results[0] += 1
            batch_results[0] += 1
        time.sleep(0.1)
    log_batch(name, batch_results)

def test_batch(obj):
    excode = 0
    for batch in obj:
        excode = launch_tests(batch)
    return log_final(results)

def start_tester(path, delete):
    file = open(path, 'r')
    if not file:
        print("Unable to open test file: tests.json.")
        return 1
    content = file.read()
    file.close()
    if delete and os.path.isfile(path):
        os.remove(path)
    obj = None
    try:
        obj = json.loads(content)
        return test_batch(obj)
    except Exception as e:
        print("Unable to load JSON file: {0}.".format(e))
    return 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", default=None, help="select a public test")
    args = parser.parse_args()
    if args.test:
        file = "{0}.json".format(args.test)
        log_basic("Fetching public test: {0}...".format(file))
        time.sleep(0.5)
        url = 'https://raw.githubusercontent.com/aureliancnx/liltester-config/master/{0}'.format(file)
        r = requests.get(url)
        if r.status_code != 200:
            log_basic("\033[0;31mUnable to fetch public test {0}: error {1}".format(file, r.status_code))
            return 1
        f = open(file, 'w')
        f.write(r.content.decode("utf-8"))
        f.close()
        log_basic("Test file {0} found. Starting tests.".format(file))
        return start_tester(file, True)
    return start_tester("tests.json", False)

if __name__ == "__main__":
    exit(main())
