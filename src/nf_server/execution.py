import logging
import subprocess

k = ""


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def async_run(command):
    global k
    c = command
    logging.info(f"Command to run {c}")
    for path in execute(c):
        logging.info(f"Stdout: {path}")
        k += path
