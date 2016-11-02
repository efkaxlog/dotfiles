#!/usr/bin/env python3

import i3ipc
import sys
import time
import psutil
import _thread
import subprocess
from datetime import datetime

paths = {"battery" : "/sys/class/power_supply/BAT1/capacity"}
commands = {
        "cpu" : "ps -eo pcpu | awk 'BEGIN {sum=0.0f} {sum+=$1} END {print sum}'",
        "wifi_signal" : r"iwconfig wlp3s0 | sed 's/  /\n/g' | grep Quality | sed 's/Link Quality://' | sed 's/Link Quality=//' | sed 's/ //g'",
        "volume" : r"amixer get Master | sed -n 's/^.*\[\([0-9]\+\)%.*$/\1/p'| uniq"
        }

colours = {
            "focused_workspace" : "#4cc90e",
            "inactive_workspace" : "#999999",
            "label" : "#929292",
            "value" : "#dbdbdb"
            
          }

def read_file(path, one_liner=False):
    """
    Read file and return it's contents.
    one_liner argument specifies whether only the first line is wanted.
    """
    with open(path, 'r') as f:
        contents = f.read()
    if one_liner:
        contents = contents.splitlines()[0]
    return contents

def padding(pixels):
    return "%{O" + str(pixels) + "}"

def fg(colour, text):
    return "%{F" + colour + "}" + text

def label(label, value):
    return fg(colours["label"], label) + fg(colours["value"], value)

class Bar(object):

    def __init__(self):
        self.i3 = i3ipc.Connection()
        self.run_all()

    def set_battery(self):
        percent = read_file(paths["battery"], one_liner=True)
        self.battery = label("battery ", percent + "%")

    def set_datetime(self):
        now = datetime.now()
        self.datetime = (now.strftime("%a") + " " +  now.strftime("%b") 
                         + " " + now.strftime("%d")
                         + " " + "{:02d}".format(now.hour) + ":" + "{:02d}".format(now.minute))

    def set_home_free(self):
        free = psutil.disk_usage("/home").free / 1024 / 1024 / 1024
        self.home_free = label("home ", "{0:.1f}".format(free) + " GiB")

    def set_memory(self):
        free = psutil.virtual_memory().available / 1024 / 1024 / 1024
        self.memory = label("mem ", "{0:.1f}".format(free))

    def set_cpu(self):
        proc = subprocess.Popen(commands["cpu"], stdout=subprocess.PIPE, shell=True)
        percent = proc.stdout.read().decode("utf-8").splitlines()[0]
        self.cpu = label("cpu ", percent)

    def set_root_free(self):
        free = psutil.disk_usage("/").free / 1024 / 1024 / 1024
        self.root_free = label("root ", "{0:.1f}".format(free) + " GiB")

    def set_wifi_signal(self):
        proc = subprocess.Popen(commands["wifi_signal"], stdout=subprocess.PIPE, shell=True)
        signal = proc.stdout.read().decode("utf-8").splitlines()[0]
        self.wifi = label("wifi ", signal)

    def set_workspaces(self):
        current = self.i3.get_tree().find_focused().workspace().name
        active_tree = self.i3.get_tree().workspaces()
        actives = []
        for tree in active_tree:
            actives.append(tree.name)
        for i, workspace in enumerate(actives):
            if workspace == current:
                colour = colours["focused_workspace"]
            else:
                colour = colours["inactive_workspace"]
            
            actives[i] = fg(colour, workspace)

        self.active_workspaces = " ".join(actives)

    def set_volume(self):
        proc = subprocess.Popen(commands["volume"], stdout=subprocess.PIPE, shell=True)
        volume = proc.stdout.read().decode("utf-8").splitlines()[0]
        self.volume = label("volume ", volume + "%")

    def run_all(self):
        """
        Runs all set methods to set all values for the bar.
        """
        self.set_battery()
        self.set_datetime()
        self.set_home_free()
        self.set_root_free()
        self.set_memory()
        self.set_cpu()
        self.set_volume()
        self.set_wifi_signal()
        self.set_workspaces()

    def print_bar(self):
        print(
            "%{l}" + padding(3) + self.home_free + padding(10) + self.root_free,
            self.memory, self.cpu + "%{c}" + self.active_workspaces,
            "%{r}" + self.wifi + padding(10) + self.volume + padding(10),
            self.battery + padding(10), self.datetime + padding(3))
        sys.stdout.flush()

    def update(self, interval, function):
        while True:
            function()
            self.print_bar()
            time.sleep(interval)

    def start(self):
        self.run_all()
        self.print_bar()
        _thread.start_new_thread(self.update, (3, self.set_cpu))
        _thread.start_new_thread(self.update, (5, self.set_wifi_signal))
        _thread.start_new_thread(self.update, (15, self.set_volume))
        _thread.start_new_thread(self.update, (10, self.set_memory))
        _thread.start_new_thread(self.update, (60, self.set_root_free))
        _thread.start_new_thread(self.update, (60, self.set_home_free))
        _thread.start_new_thread(self.update, (60, self.set_battery))
        _thread.start_new_thread(self.update, (60, self.set_datetime))
        


bar = Bar()
bar.print_bar()
bar.start()

def on_workspace_change(self, e):
    bar.set_workspaces()
    bar.print_bar()

bar.i3.on("workspace::focus", on_workspace_change)
bar.i3.main()
