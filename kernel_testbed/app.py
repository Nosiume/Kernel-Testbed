#!/usr/bin/env python3

import sys
from colorama import Fore, Style, init
from kernel_testbed.banner import banner_display
from kernel_testbed.env import run, make, debug

# Some global infos about the program
APP_NAME = "Kernel Testbed by Nosiume"
DESCRIPTION = """A program for testing and debugging of kernel level exploits
This program is solely intended for research and educative purposes only, please
do not use it to cause harm to any individual or entity.
"""
GITHUB_PAGE = "https://github.com/Nosiume/Kernel-Testbed"
EPILOG="See sources and contribute here : " + GITHUB_PAGE

# argument management

def show_help():
    pass

DISPATCH = {
    "run": run,
    "make": make,
    "debug": debug,
    "help": show_help
}

def main():
    init(autoreset=True) 

    banner_display() 

    if len(sys.argv) <= 1 or sys.argv[1] not in DISPATCH.keys():
        print(Fore.RED, "[ERROR] You need to use one of the following commands : ", Style.RESET_ALL)
        print("\t- make : Builds a new kernel exploitation environment")
        print("\t- run : runs the current environment from a given path or from the current directory")
        print("\t- debug : same as run excepts opens a GDB debugging session linked to the running kernel")
        print("\t- help : shows an in-depth help menu")
        exit(-1)

    DISPATCH[sys.argv[1]](sys.argv[2:])
