# HTCondor Snakemake profile

This profile configures Snakemake to submit jobs to a HTCondor cluster.

### Prerequisites
The profile makes use of the HTCondor python bindings (and  `snakemake-executor-plugin-cluster-generic` for snakemake > 8) which can be installed with 

    pip install --user htcondor snakemake-executor-plugin-cluster-generic 
    
or using Anaconda with

    conda install -c conda-forge -c bioconda python-htcondor snakemake-executor-plugin-cluster-generic

### Deploy profile

To deploy this profile run

    mkdir -p ~/.config/snakemake
    cookiecutter --output-dir ~/.config/snakemake gh:Snakemake-Profiles/htcondor

You will be asked for the name of the profile and for a path where the HTCondor logs will be stored. 
The logs will be used to update the status of submitted jobs (as recommended in the [documentation of the HTCondor Python bindings](https://htcondor.readthedocs.io/en/latest/apis/python-bindings/tutorials/Scalable-Job-Tracking.html)).

Then, you can run Snakemake with

    snakemake --profile htcondor ...

so that jobs are submitted to the cluster. If Snakemake is killed and restarted afterwards, it will automatically resume still running jobs.


### Tests
The tests are heavily inspired by the tests for the slurm snakemake profile. They can be run from the base directory by 
```
pytest
```

Because the tests will try to submit jobs they need to be started from a HTCondor submit node. To run the tests from non-cluster machines or from github CI the [HTCondor/mini docker container](https://github.com/htcondor/htcondor/blob/master/build/docker/services/README.md) can be started by:
```
DOCKER_COMPOSE=tests/docker-compose.yaml ./tests/deploystack.sh
```

## Migration to snakemake v8
If using snakemake version 8 or higher, refer to [the migration guide](https://snakemake.readthedocs.io/en/stable/getting_started/migration.html). For this profile, use `config.v8+.yaml` instead of `config.yaml`
