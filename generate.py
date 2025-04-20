"""
Generate device configurations using pyavd and Nornir.
"""

import difflib
import sys

import pyavd
from loguru import logger
from nornir import InitNornir
from nornir.core.task import Result, Task
from nornir_utils.plugins.functions import print_result


def build_config(task: Task, eos_designs: dict, avd_facts: dict) -> Result:
    """
    Build the Arista device configuration from the input dicts
    """
    structured_config = pyavd.get_device_structured_config(
        task.host.name, eos_designs[task.host.name], avd_facts=avd_facts
    )
    config = pyavd.get_device_config(structured_config)

    task.host.data["designed-config"] = config
    return Result(host=task.host)


def pull_config(task: Task) -> Result:
    """
    Read the current running config from the
    configs/ directory and store it on the Task() instance.
    """
    with open(f"configs/{task.host.name}.cfg", "r") as f:
        task.host.data["running-config"] = f.read()
    return Result(host=task.host)


def diff_config(task: Task) -> Result:
    """
    Diff the current running config against the designed config
    """
    changed = False
    diff = ""
    for line in difflib.unified_diff(
        task.host.data["running-config"].split("\n"),
        task.host.data["designed-config"].split("\n"),
        fromfile="running-config",
        tofile="designed-config",
        lineterm="",
    ):
        diff += f"{line}\n"
        changed = True
    return Result(host=task.host, diff=diff, changed=changed)


def deploy_config(task: Task) -> Result:
    """
    Write configurations to the configs/ directory
    """
    with open(f"configs/{task.host.name}.cfg", "w") as f:
        f.write(task.host.data["designed-config"])
    return Result(host=task.host, changed=True)


def config_management(task: Task, eos_designs: dict, avd_facts: dict) -> None:
    """
    Accept a nornir.Task() instance, which is specific to an Arista switch.

    - build the new device config.
    - read the current running config
    - Diff the two configs
    - Write a new config if the diff is not empty
    """
    task.run(task=build_config, eos_designs=eos_designs, avd_facts=avd_facts)
    task.run(task=pull_config)  # Read the current running config
    result = task.run(task=diff_config)[0]
    if result.changed:
        task.run(task=deploy_config)


def build_configs():
    """
    Read the device inventory and generate new device configs.
    """
    # Initialize Nornir object from config_file
    nr = InitNornir(config_file="nornir_config.yml")

    # All router / switch AVD dicts are stored in eos_designs
    #    eos_designs is keyed by hostname...
    eos_designs = {}

    for hostname in nr.inventory.hosts:
        host = nr.inventory.hosts[hostname]

        eos_hostvars = {}
        for k, v in host.items():
            eos_hostvars[k] = v

        eos_designs[hostname] = eos_hostvars

    # Validate input and convert types as needed
    failures = False
    for eos_hostvars in eos_designs.values():
        # Validate the hostvars per switch...
        results = pyavd.validate_inputs(eos_hostvars)
        if results.failed:
            for result in results.validation_errors:
                logger.error(result)
            failures = True
    if failures:
        sys.exit(1)

    # Generate facts
    #  Ref:
    #    https://avd.arista.com/5.1/docs/pyavd.html#pyavd.get_avd_facts.get_avd_facts
    avd_facts = pyavd.get_avd_facts(eos_designs)

    # use nornir to run config_management() to build the config...
    #     nornir.run() will run the function on all hosts in the inventory...
    output = nr.run(
        task=config_management, eos_designs=eos_designs, avd_facts=avd_facts
    )
    print_result(output)


if __name__=="__main__":
    build_configs()
