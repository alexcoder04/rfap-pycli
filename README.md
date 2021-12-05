
# rfap-pycli

CLI Client for rfap. See [related projects](#related-projects) for compatible
applications and protocol specification.

## Requirements

 - Python 3.6+
 - [librfap](https://github.com/alexcoder04/librfap)

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

| commands                                       | description              |
|------------------------------------------------|--------------------------|
| `help`                                         | print help               |
| `pwd`                                          | print working directory  |
| `cd <folder>`                                  | change working directory |
| `ls <folder>`, `list <folder>`, `dir <folder>` | list directory           |
| `exit`, `quit`, `:q`                           | disconnect and exit      |

## Related projects

 - https://github.com/alexcoder04/rfap - protocol specification
 - https://github.com/alexcoder04/rfap-go-server - reference server implementation
 - https://github.com/alexcoder04/librfap - Python library
 - https://github.com/BoettcherDasOriginal/rfap-cs-lib - C# library

