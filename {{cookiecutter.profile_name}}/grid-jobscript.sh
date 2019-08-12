#!/bin/bash
# properties = {properties}

set -e

echo "hostname:"
hostname -f

{exec_job}
