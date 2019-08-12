#!/usr/bin/env python3

import sys
import htcondor
from os import makedirs
from os.path import join
from uuid import uuid4

from snakemake.utils import read_job_properties


jobscript = sys.argv[1]
job_properties = read_job_properties(jobscript)

UUID = uuid4()  # random UUID
jobDir = '{{cookiecutter.htcondor_log_dir}}/{}_{}'.format(job_properties['jobid'], UUID)
makedirs(jobDir, exist_ok=True)

sub = htcondor.Submit({
    'executable':  '/bin/bash',
    'arguments':   jobscript,
    'max_retries': '5',
    'log':         join(jobDir, 'condor.log'),
    'error':       join(jobDir, 'condor.err'),
    'getenv':      'True',
})

schedd = htcondor.Schedd()
with schedd.transaction() as txn:
    clusterID = sub.queue(txn)

# print jobid for use in Snakemake
print('{}_{}_{}'.format(job_properties['jobid'], UUID, clusterID))
