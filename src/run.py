import subprocess
from master import Master
from GUI.runescapeApplication import create


if __name__ == '__main__':
    subprocess.call('clear')
    master = Master()
    create(master)