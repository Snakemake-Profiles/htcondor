# surfsara-grid

This profile configures Snakemake to run on the [SURFsara Grid](https://www.surf.nl/en/services-and-products/grid/index.html).

## Setup

### Prerequisites

#### Step 1: Login to softdrive

    ssh username@softdrive.grid.sara.nl

#### Step 2:  Setup bioconda

Then, install Miniconda 2 (in order to not interfere with python 2 grid tools).

    wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
    chmod +x Miniconda2-latest-Linux-x86_64.sh
    ./Miniconda2-latest-Linux-x86_64.sh -b -p /cvmfs/softdrive.nl/$USER/Miniconda2

And add the installation to the PATH (put the following into your .bashrc):

    export PATH=/cvmfs/softdrive.nl/$USER/Miniconda2/bin:$PATH

Finally, setup the channel order for bioconda:

    conda config --add channels defaults
    conda config --add channels conda-forge
    conda config --add channels bioconda

#### Step 3: Create a Snakemake environment

    conda create -n snakemake snakemake python=3.6 pandas cookiecutter


### Deploy profile

To deploy this profile, login to your grid UI change to your desired **working directory** and run

    cookiecutter https://github.com/snakemake-profiles/surfsara-grid.git

Then, you can run Snakemake with

    snakemake --profile surfsara-grid ...

so that jobs are submitted to the grid. 
If a job fails, you will find the "external jobid" in the Snakemake error message.
You can investigate the job via this ID as shown [here](http://docs.surfsaralabs.nl/projects/grid/en/latest/Pages/Basics/first_grid_job.html?highlight=glite#track-the-job-status).
If Snakemake is killed and restarted afterwards, it will automatically resume still running jobs.

### Proxy certificates

Note that Snakemake needs valid proxy certificates throughout its runtime.
It is advisable to use maximum lifetimes for those, i.e., generate them with

    voms-proxy-init --voms <voms> --valid 168:00
    myproxy-init -d -n -c 744 -t 744
    glite-wms-job-delegate-proxy -d $USER

while replacing `<voms>` with your value (e.g. `lsgrid:/lsgrid/Project_MinE`).
