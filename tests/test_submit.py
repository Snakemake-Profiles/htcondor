#!/usr/bin/env python3

import pytest
import os


@pytest.fixture
def profile(cookie_factory, data, request):
    cookie_factory()


def test_htcondor_submit(smk_runner, profile):
    fn = "test_submit.txt"
    smk_runner.make_target(fn)
    assert "Finished job" in smk_runner.output
    path = os.path.join(smk_runner._data, fn)
    assert os.path.isfile(path)


@pytest.mark.timeout(30)
def test_resources_mem(smk_runner, profile):
    fn = "resources_mem.txt"
    smk_runner.make_target(fn, asynchronous=True)
    smk_runner.wait_until_job_exists()
    for ji in smk_runner.external_jobinfo:
        assert ji["RequestMemory"] == 99
    smk_runner.kill_job()


@pytest.mark.timeout(30)
def test_resources_disk(smk_runner, profile):
    fn = "resources_disk.txt"
    smk_runner.make_target(fn, asynchronous=True)
    smk_runner.wait_until_job_exists()
    for ji in smk_runner.external_jobinfo:
        assert ji["RequestDisk"] == 99
    smk_runner.kill_job()
