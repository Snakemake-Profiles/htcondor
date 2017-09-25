#!/usr/bin/env python3

import tempfile
import textwrap
import sys
import subprocess
import os
import getpass
import json
import shutil

from snakemake.utils import read_job_properties


def wait_for_proxy():
    stdout = sys.stdout
    sys.stdout = sys.stderr
    input("UI proxy expired. Please create a new proxy (see README) and press ENTER to continue.")
    sys.stdout = stdout


jobscript = sys.argv[1]
job_properties = read_job_properties(jobscript)

commit = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, check=True).stdout.decode().strip()


with tempfile.TemporaryDirectory() as jobdir:
    jdlpath = os.path.join(jobdir, "job.jdl")
    with open(jdlpath, "w") as jdl:
        jdl.write(textwrap.dedent("""
        Type = "Job";
        JobType = "Normal";
        Executable = "/bin/bash";
        Arguments = "jobscript.sh {commit} {user}";
        PerusalFileEnable = true;
        PerusalTimeInterval = 120;
        StdOutput = "stdout.txt";
        StdError = "stderr.txt";
        SmpGranularity = {threads};
        CPUNumber = {threads};
        Requirements = other.GlueCEPolicyMaxWallClockTime >= {minutes} &&
                       other.GlueHostArchitectureSMPSize >= {cores};
        InputSandbox = {{"jobscript.sh", "grid-source.tar"}};
        OutputSandbox = {{"stdout.txt","stderr.txt"}};
        """).format(commit=commit,
                    user=getpass.getuser(),
                    threads=job_properties["threads"],
                    cores=job_properties["threads"] + 2,
                    minutes=job_properties["resources"].get("minutes", 240)))

    shutil.copyfile(jdlpath, "last-job.jdl")
    shutil.copyfile(jobscript, "last-jobscript.sh")
    shutil.copyfile(jobscript, os.path.join(jobdir, "jobscript.sh"))
    shutil.copyfile("grid-source.tar", os.path.join(jobdir, "grid-source.tar"))

    workdir = os.getcwd()
    os.chdir(jobdir)
    cmd = ["glite-wms-job-submit", "--json", "-d", getpass.getuser(), jdl.name]
    for i in range(10):
        try:
            res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            if "UI_PROXY_EXPIRED" in e.stdout.decode():
                wait_for_proxy()
                continue
            if i >= 9:
                raise e

    res = json.loads(res.stdout.decode())
    os.chdir(workdir)

with open("grid-jobids.txt", "a") as f:
    print(res["jobid"], *job_properties["output"], sep="\t", file=f)

# print jobid for use in Snakemake
print(res["jobid"])
