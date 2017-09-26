#!/bin/bash
# properties = {properties}

set -e

user=$2

export PATH=/cvmfs/softdrive.nl/$user/Miniconda2/bin:$PATH
echo "hostname:"
hostname -f
which activate
source activate snakemake

tar -xf grid-source.tar

{exec_job}
echo $?
