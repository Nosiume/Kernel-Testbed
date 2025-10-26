import os
import requests
import tempfile
import subprocess
from tqdm import trange
from io import SEEK_END
from colorama import Fore, Style
from bs4 import BeautifulSoup

from kernel_testbed.utils import get_editor

BLOCK_SIZE = 1024 # for writing and reading
KERNEL_SOURCE = "https://github.com/torvalds/linux"

# Represents a kernel exploit dev environment
class Environment(object):
    def __init__(path: str):
        pass

# Utilities

# Copies a kernel image from source to a destination path, with nice prompt and loading bar
def copy_kernel_image(src, dst):
    kernel_fd = open(src, "rb")
    out_fd = open(dst, "wb")

    kernel_fd.seek(0, SEEK_END)
    size = kernel_fd.tell()
    kernel_fd.seek(0) # go back to 0

    print(f"{Fore.CYAN}[*] Copying kernel to env at {dst}...{Style.RESET_ALL}")

    try:
        for i in trange(0, size, BLOCK_SIZE):
            data = kernel_fd.read(BLOCK_SIZE)
            out_fd.write(data)
    except:
        print(f"{Fore.RED}[-] Failed to copy kernel... canceling{Style.RESET_ALL}")
        exit(-2)

    kernel_fd.close()
    out_fd.close()

# Prompts the user for a kernel version they want to use
def kernel_prompt(dst):
    # first we fetch the available versions
    print(f"{Fore.CYAN}[*] Querying source for information: {KERNEL_SOURCE}{Style.RESET_ALL}")

    res = requests.get(KERNEL_SOURCE + "/tags")
    if res.status_code != 200:
        print(f"{Fore.RED}[-] Failed to query kernel versions...{Style.RESET_ALL}")
        exit(-3)
    
    soup = BeautifulSoup(res.text, features="html.parser")
    versions = []
    for element in soup.select('a[href$=".zip"]'):
        versions.append(element.get('href'))

    print(f"{Fore.GREEN}[+] Successfully fetched versions from source.{Style.RESET_ALL}")

    # Now that we have the versions, let's prompt for a choice !

    for i, version in enumerate(versions):
        name = version.split("/")[-1][:-4] # get last element's version name
        print(f"\t[{Fore.GREEN}{i+1}{Style.RESET_ALL}] - {Fore.LIGHTMAGENTA_EX}{name}{Style.RESET_ALL}")

    choice = 0
    while 1 > choice or 10 < choice:
        choice = int(input(f"{Fore.CYAN}Choose a version> {Style.RESET_ALL}"))
    
    zip_file_url = "https://github.com" + versions[choice-1]
    print(f"{Fore.CYAN}[*] You chose the following version : {zip_file_url}{Style.RESET_ALL}")

    # Now that we have our remote URL for the zip file, we must download it 
    # we'll store it a temporary file
    tmp = tempfile.mkdtemp()
    print(f"{Fore.CYAN}[*] Temporary build dir at {tmp}{Style.RESET_ALL}")

    res = requests.get(zip_file_url)
    if res.status_code != 200:
        print(f"{Fore.RED}[-] Failed to get zip from remote source. Cancelling...{Style.RESET_ALL}")
        exit(-4)

    # Get zip and extract it
    with open(tmp + "/kernel.zip", "wb") as out:
        out.write(res.content)

    print(f"{Fore.CYAN}[*] Downloaded zip into kernel.zip file, unzipping...{Style.RESET_ALL}")
    # Old code doesn't work since zipfile doesn't take in account symlinks
    #with zipfile.ZipFile(tmp + "/kernel.zip", 'r') as zip_ref:
    #    zip_ref.extractall(tmp)

    result = subprocess.run(
        ['unzip', tmp + '/kernel.zip'],
        cwd=tmp,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"{Fore.RED}[-] Failed to unzip downloaded kernel source. Cancelling...{Style.RESET_ALL}")
        exit(-5)

    print(f"{Fore.GREEN}[+] Successfully extracted kernel source in {tmp}{Style.RESET_ALL}")
    build_path = tmp + "/" + os.listdir(tmp)[0]

    # Now build config before building the kernel
    print(f"{Fore.CYAN}[*] Building config at {build_path}...{Style.RESET_ALL}")
    result = subprocess.run(
        ['make', 'x86_64_defconfig'],
        cwd=build_path,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"{Fore.RED}[-] Failed to create config. Cancelling...{Style.RESET_ALL}")
        exit(-6)

    # Editing config
    choice = "foobar"
    while len(choice) >= 1 and choice[0] not in ("y", "n"):
        choice = input("Do you wish to edit the build config (y/n) ?").lower()
    
    if choice[0] == "y":
        # Open editor
        editor = get_editor()
        subprocess.run(
            [editor, ".config"],
            cwd=build_path,
            check=True
        )

    # Now we build !
    cpu_count = str(os.cpu_count() or 1)
    print(f"{Fore.CYAN}[*] Starting kernel build using {cpu_count} cores.{Style.RESET_ALL}")

    result = subprocess.run(
        ["make", "-j", cpu_count],
        cwd=build_path,
        check=True
    )  

    if result.returncode != 0:
        print(f"{Fore.RED}[-] Failed to build kernel. Cancelling...{Style.RESET_ALL}")
        exit(-7)
    else:
        print(f"{Fore.GREEN}[+] Successfully built kernel !{Style.RESET_ALL}")

    copy_kernel_image(src=build_path + "/arch/x86_64/boot/bzImage", dst=dst)

# Command Parsing

def run():
    pass

def make(args):
    config = {
        "path": "./kenv",
        "kernel": "latest",
        "filesystem": "./kenv/initramfs.cpio.gz"
    }

    # Update config depending on arguments
    i = 0
    while i < len(args):
        if args[i] in ("-p", "--path"):
            config["path"] = args[i+1]
            i += 2
        elif args[i] in ("-k", "--kernel"):
            config["kernel"] = args[i+1]
            i += 2
        elif args[i] in ("-fs", "--filesystem"):
            config["filesystem"] = args[i+1]
            i += 2
    
    # Create path to kenv, handles errors
    if not os.path.exists(config["path"]):
        try:
            os.mkdir(config["path"])
            print(f"{Fore.GREEN}[+] Created {config["path"]} kernel environment{Style.RESET_ALL}")
        except:
            print(f"{Fore.RED}[-] Couldn't create folder for kernel env. Check permissions !{Style.RESET_ALL}")
            return

    # Copy kernel image if given, build one if not
    if os.path.exists(config["kernel"]):
        copy_kernel_image(src=config["kernel"], dst=config["path"] + "/bzImage")
    else:
        kernel_prompt(dst=config["path"])
        

def debug():
    pass
