#!/usr/bin/env python3
import os
from os.path import join as pjoin
import re
import py
import pytest
import docker
import shutil
import logging
from pytest_cookies.plugin import Cookies
from wrapper import SnakemakeRunner, ShellContainer


def pytest_configure(config):
    pytest.local_user_id = os.getuid()
    pytest.dname = os.path.dirname(__file__)
    pytest.cookie_template = py.path.local(pytest.dname).join(os.pardir)
    setup_logging(config.getoption("--log-level"))
    if shutil.which("condor_q") is not None and config.getoption("--basetemp") is None:
        config.option.basetemp = "./.pytest"


def setup_logging(level):
    if level is None:
        level = logging.WARN
    elif re.match(r"\d+", level):
        level = int(level)
    logging.basicConfig(level=level)
    logging.getLogger("urllib3").setLevel(level)
    logging.getLogger("docker").setLevel(level)
    logging.getLogger("poyo").setLevel(level)
    logging.getLogger("binaryornot").setLevel(level)


@pytest.fixture
def datadir(tmpdir_factory):
    """Setup base data directory for a test"""
    p = tmpdir_factory.mktemp("data")
    return p


@pytest.fixture
def datafile(datadir):
    """Add a datafile to the datadir.

    By default, look for a source (src) input file located in the
    tests directory (pytest.dname). Custom data can be added by
    pointing a file 'dname / src'. The contents of src are copied to
    the file 'dst' in the test data directory

    Args:
      src (str): source file name
      dst (str): destination file name. Defaults to src.
      dname (str): directory where src is located.

    """

    def _datafile(src, dst=None, dname=pytest.dname):
        dst = src if dst is None else dst
        src = py.path.local(pjoin(dname, src))
        dst = datadir.join(dst)
        src.copy(dst)
        return dst

    return _datafile


@pytest.fixture
def cookie_factory(tmpdir_factory, _cookiecutter_config_file, datadir):
    """Cookie factory fixture.

    Cookie factory fixture to create a slurm profile in the test data
    directory.

    """

    logging.getLogger("cookiecutter").setLevel(logging.INFO)

    _yamlconfig_default = {"restart-times": 1}

    def _cookie_factory(
        log_dir="log",
        yamlconfig=_yamlconfig_default,
    ):
        cookie_template = pjoin(os.path.abspath(pytest.dname), os.pardir)
        output_factory = tmpdir_factory.mktemp
        c = Cookies(cookie_template, output_factory, _cookiecutter_config_file)
        c._new_output_dir = lambda: str(datadir)
        profile_name = "htcondor"
        extra_context = {
            "profile_name": profile_name,
            "htcondor_log_dir": log_dir,
        }
        c.bake(extra_context=extra_context)
        config = datadir.join(profile_name).join("config.yaml")
        config_d = dict(
            [
                tuple(line.split(":"))
                for line in config.read().split("\n")
                if re.search("^[a-z]", line)
            ]
        )
        config_d.update(**yamlconfig)
        config.write("\n".join(f"{k}: {v}" for k, v in config_d.items()))

    return _cookie_factory


@pytest.fixture
def data(tmpdir_factory, request, datafile):
    """Setup base data"""
    dfile = datafile("Snakefile")
    return py.path.local(dfile.dirname)


@pytest.fixture(scope="session")
def htcondor(request):
    """HTCondor fixture

    Return relevant container depending on environment. First look for
    condor_q command to determine whether we are on a system running the
    HTCondor scheduler. Second, try deploying a docker stack to run htcondor
    locally.

    Skip htcondor tests if the above actions fail.

    """
    if shutil.which("condor_q") is not None:
        return ShellContainer()
    else:
        client = docker.from_env()
        container_list = client.containers.list(
            filters={"name": "cookiecutter-htcondor_htcondor"}
        )
        container = container_list[0] if len(container_list) > 0 else None
        if container:
            return container

    msg = (
        "no condor_q or docker stack 'cookiecutter-htcondor_htcondor' running;"
        " skipping HTCondor-based tests."
        " Either run tests on a HTCondor HPC or deploy a docker stack with"
        f" {os.path.dirname(__file__)}/deploystack.sh"
    )

    pytest.skip(msg)


def teardown(request):
    """Shutdown snakemake processes that are waiting for HTCondor

    On nsf systems, stale snakemake log files may linger in the test
    directory, which prevents reruns of pytest. The teardown function
    calls 'lsof' to identify and terminate the processes using these
    files.

    """

    logging.info(f"\n\nTearing down test '{request.node.name}'")
    basetemp = request.config.getoption("basetemp")
    from subprocess import Popen, PIPE
    import psutil

    for root, _, files in os.walk(basetemp, topdown=False):
        for name in files:
            if not root.endswith(".snakemake/log"):
                continue
            try:
                fn = os.path.join(root, name)
                proc = Popen(["lsof", "-F", "p", fn], stdout=PIPE, stderr=PIPE)
                pid = proc.communicate()[0].decode().strip().strip("p")
                if pid:
                    p = psutil.Process(int(pid))
                    logging.info(f"Killing process {p.pid} related to {fn}")
                    p.kill()
            except psutil.NoSuchProcess as e:
                logging.warning(e)
            except ValueError as e:
                logging.warning(e)


@pytest.fixture
def smk_runner(htcondor, datadir, request):
    """smk_runner fixture

    Setup a wrapper.SnakemakeRunner instance that runs the snakemake
    tests. Skip tests where the partition doesn't exist on the system.
    Some tests also only run in docker.

    """

    yield SnakemakeRunner(htcondor, datadir, request.node.name)

    if isinstance(htcondor, ShellContainer):
        teardown(request)
