from subprocess import run, PIPE, STDOUT, Popen
import asyncio


def run_codex():
    # process = run(["codex"], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True, shell=True)
    # print(process)
    with Popen(["bash"], stdout=PIPE, stdin=PIPE, shell=True) as process:
        process.stdin.write(b"codex")
        process.stdin.flush()
        process.communicate(input=b"\n")

run_codex()
