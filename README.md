# HTCondor Snakemake profile

This profile configures Snakemake to submit jobs to a HTCondor cluster.

### Prerequisites
The profile makes use of the HTCondor python bindings which can be installed with 

    pip install --user htcondor
    
or using Anaconda with

    conda install -c conda-forge python-htcondor

### Deploy profile

To deploy this profile run

    mkdir -p ~/.config/snakemake
    cd ~/.config/snakemake
    cookiecutter https://github.com/Snakemake-Profiles/htcondor.git

You will be asked for the name of the profile and for a path where the HTCondor logs will be stored. The logs will be used to update the status of submitted jobs (as recommended in the [documentation of the HTCondor python bindings](https://htcondor-python.readthedocs.io/en/latest/scalable_job_tracking.html#event-based-tracking)).

Then, you can run Snakemake with

    snakemake --profile htcondor ...

so that jobs are submitted to the cluster. If Snakemake is killed and restarted afterwards, it will automatically resume still running jobs.
