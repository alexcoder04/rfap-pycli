
# rfap-pycli

[![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/alexcoder04/rfap-pycli?include_prereleases)](https://github.com/alexcoder04/rfap-pycli/releases/latest)
[![GitHub top language](https://img.shields.io/github/languages/top/alexcoder04/rfap-pycli)](https://github.com/alexcoder04/rfap-pycli/search?l=go)
[![GitHub](https://img.shields.io/github/license/alexcoder04/rfap-pycli)](https://github.com/alexcoder04/rfap-pycli/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/alexcoder04/rfap-pycli)](https://github.com/alexcoder04/rfap-pycli/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/alexcoder04/rfap-pycli)](https://github.com/alexcoder04/rfap-pycli/pulls)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/alexcoder04/rfap-pycli)](https://github.com/alexcoder04/rfap-pycli/commits/main)
[![GitHub contributors](https://img.shields.io/github/contributors-anon/alexcoder04/rfap-pycli)](https://github.com/alexcoder04/rfap-pycli/graphs/contributors)

CLI Client for rfap. See [related projects](#related-projects) for compatible
applications and protocol specification.

## Requirements

 - Python 3.6+
 - [librfap](https://github.com/alexcoder04/librfap)

As we are in an early development stage, big changes come often and not
everything is backward- and forward-compatible. So always check the required
librfap version in the release notes. The bleeding-edge version from this repo
should be compatible with the bleeding-edge version of librfap, although it
might not always the case.

## Installation

```sh
git clone https://github.com/alexcoder04/rfap-pycli
cd rfap-pycli
make install # not working right now, in progress
```

## Usage

```
./rfap_pycli.py [-s server-address] [-c]
```

### Documentation

**Coming soon**

### Commands

| commands                                       | description                              |
|------------------------------------------------|------------------------------------------|
| `help`                                         | print help                               |
| `pwd`                                          | print working directory                  |
| `cd <folder>`                                  | change working directory                 |
| `ls <folder>`, `list <folder>`, `dir <folder>` | list directory                           |
| `clear`, `cls`                                 | clear screen                             |
| `exit`, `quit`, `:q`                           | disconnect and exit                      |
| `exec`                                         | execute python command (debug mode only) |

## Related projects

 - https://github.com/alexcoder04/rfap - protocol specification
 - https://github.com/alexcoder04/rfap-go-server - reference server implementation
 - https://github.com/alexcoder04/librfap - Python library
 - https://github.com/BoettcherDasOriginal/rfap-cs-lib - C# library

