#!/usr/bin/env python

import sys
import htcondor
from htcondor import JobEventType
from os.path import join


def print_and_exit(s):
    print(s)
    exit()


jobID, UUID, clusterID = sys.argv[1].split('_')

jobDir = '/net/data_lhcb1b/user/jheuel/.condor_jobs/{}_{}'.format(jobID, UUID)
jobLog = join(jobDir, 'condor.log')

try:
    jel = htcondor.JobEventLog(join(jobLog))
    for event in jel.events(stop_after=5):
        if event.type is JobEventType.JOB_ABORTED:
            print_and_exit('failed')
        if event.type is JobEventType.JOB_TERMINATED:
            if event['ReturnValue'] == 0:
                print_and_exit('success')
            print_and_exit('failed')
except OSError as e:
    print_and_exit('failed')

print_and_exit('running')
