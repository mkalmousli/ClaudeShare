import importlib.util
import pathlib

import pytest

SPEC = importlib.util.spec_from_file_location("ctl_args", pathlib.Path(__file__).parent.parent / "system/ctl_args.py")
ctl_args = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ctl_args)


def test_valid_commands_pass_through():
    assert ctl_args.admin_args(["add", "alice", "--key", "abcdefgh1234"]) == ["add", "alice", "--key", "abcdefgh1234"]
    assert ctl_args.admin_args(["limit", "bob", "25%", "--period", "week"]) == ["limit", "bob", "25%", "--period", "week"]
    assert ctl_args.admin_args(["status"]) == ["status"]


@pytest.mark.parametrize("bad", [["add", "Al;ice"], ["add", "a b"], ["add", "alice", "--key", "x"], ["limit", "bob", "lots"],
                                 ["rm", "bob"], ["add"], ["limit", "bob", "5m", "--period", "year"], ["del", "bob", "--exec"],
                                 ["add", "$(id)"], []])
def test_hostile_or_malformed_input_is_refused(bad):
    with pytest.raises(SystemExit):
        ctl_args.admin_args(bad)


def test_resources_command_grammar():
    ok = ["resources", "alice", "--mem", "2g", "--cpu", "1.5", "--procs", "300", "--disk", "20g"]
    assert ctl_args.admin_args(ok) == ok
    assert ctl_args.admin_args(["resources", "alice", "--mem", "default"]) == ["resources", "alice", "--mem", "default"]
    for bad in (["resources", "alice", "--mem", "lots"], ["resources", "alice", "--cpu", "-1"], ["resources", "alice", "--bogus", "1"],
                ["resources", "alice", "--mem"], ["resources", "a;b", "--mem", "1g"]):
        with pytest.raises(SystemExit):
            ctl_args.admin_args(bad)
