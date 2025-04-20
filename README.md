
## Intro

- This is a fork of [haylinmoore/nornir-pyavd][1]
- The project uses [nornir][3] and [pyavd][2] to generate Arista Validated Design (AVD) switch configuration files.
  - The [pyavd][2] version is called out in `pyproject.toml`
  - Ensure that you use the right version of [pyavd][2] for the AVD syntax in your yaml

### Installation

Just install the package dependencies and the package with `pip install .`

### generate.py

- `generate.py` uses [nornir][3] tasks to build Arista configuration files
- The current version of this script only builds configurations if they are different than the version checked into git

### Nornir details

- `nornir_config.yml`
   - Tells Nornir to use the Ansible plugin to read ansible-style inventories
   - Tells Nornir to run in threaded mode for enhanced performance.

  [1]: https://github.com/haylinmoore/nornir-pyavd
  [2]: https://github.com/aristanetworks/avd
  [3]: https://github.com/nornir-automation/nornir
