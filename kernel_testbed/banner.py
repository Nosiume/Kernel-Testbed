from colorama import init, Fore, Style

# COLORAMA SETUP
PALETTE = [Fore.CYAN, Fore.MAGENTA, Fore.BLUE]

BANNER = [
r"____  __.          ___________                                   ",
r"|    |/ _|__________\_   _____/__  _________     ____   _______  __",
r"|      <_/ __ \_  __ \    __)_\  \/  /\____ \  _/ __ \ /    \  \/ /",
r"|    |  \  ___/|  | \/        \>    < |  |_> > \  ___/|   |  \   / ",
r"|____|__ \___  >__| /_______  /__/\_ \|   __/   \___  >___|  /\_/  ",
r"        \/   \/             \/      \/|__|          \/     \/",
]

def colorize_line(line: str) -> str:
    # gradient across non-space characters
    vis = [c for c in line if c != " "]
    n = max(1, len(vis))
    out, i = [], 0
    for ch in line:
        if ch == " ":
            out.append(" ")
        else:
            out.append(PALETTE[(i * len(PALETTE)) // n] + ch)
            i += 1
    out.append(Style.RESET_ALL)
    return "".join(out)

def banner_display():
    for line in BANNER:
        print(colorize_line(line))

