# SpeedtestAutomation

This repository seeks to provide a simple speedtest automation for household use and is not affiliated, endorsed, or otherwise associated with Ookla.

## Introduction

<!-- Sources, References (See Also):
    https://www.fcc.gov/consumers/guides/fcc-speed-test-app-tip-sheet
    https://schedule.readthedocs.io/en/stable/examples.html#run-a-job-every-x-minute
-->

<!-- INTRODUCE: FCC regulation and why this repository exists + typical intended uses -->
In the United States

## Overview

In its present state, after dependencies are installed this project starts from the command line via a simple command:  `python main.py`

Launching the script app initializes a task/job scheduler which adds defined routines and executes a simple timer. When the defined interval elapses a job is placed in the process runner's task queue which then launches a dedicated thread for additional processing while the original thread maintains execution of the loop to avoid timer disruptions.

## Requirements

Use of this project has several requirements:
- A working Python installation and associated reference in the PATH environment variable
- the [speedtest-cli](https://www.speedtest.net/apps/cli#ubuntu) provided by Ookla
- an external third-party smtp service provider for handling emails
- various python libraries (installable either by Pipfile or requirements.txt)

## Deployment

Overall, the anticipated deployment strategy requires little hardware and only a few libraries which makes it a perfect candidate for running on raspberry pi.

1. Ensure that Python is installed and working
    - Though not expressly required, Python 3.10 was used for development
2. Install Ookla's speedtest-cli, review their terms, and accept to proceed
```bash
# curl is required to install speedtest; or use wget or whatever tool you prefer
sudo apt-get install curl
# add package manager repo sources for speedtest-cli with curl
# WARNING: it's not typically acceptable practice to pipe random commands/scripts to 
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash

sudo apt-get install speedtest
```
3. Install required python dependencies
```bash
    # if using pipenv and/or virtual environments
    pipenv install

    # if using requirements.txt
    pip install -r requirements.txt
```

