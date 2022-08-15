#!/usr/bin/env python3

PROFILENAME = "helloworld"
LOGDIR = "helloworld"


def test_bake(cookies):
    """Test for 'cookiecutter-template'."""
    result = cookies.bake(
        extra_context={"profile_name": PROFILENAME, "htcondor_log_dir": LOGDIR}
    )

    assert result.exit_code == 0
    assert result.exception is None

    assert result.project_path.name == PROFILENAME
    assert result.project_path.is_dir()
