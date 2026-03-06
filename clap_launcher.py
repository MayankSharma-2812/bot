import sounddevice as sd
import numpy as np
import time
import os

threshold = 0.7
clap_times = []

def open_workspace():

    os.system("code")

    time.sleep(2)

    os.system("start chrome https://kalvium.community")

    os.system("start brave https://youtube.com")

    os.system("start brave https://instagram.com")

    os.system("start brave https://linkedin.com")

def detect_clap(indata, frames, time_info, status):

    global clap_times

    volume_norm = np.linalg.norm(indata) * 10

    if volume_norm > threshold:

        now = time.time()

        clap_times.append(now)

        clap_times = [t for t in clap_times if now - t < 1]

        if len(clap_times) >= 2:

            print("Clap detected — opening workspace")

            open_workspace()

            clap_times = []

with sd.InputStream(callback=detect_clap):

    print("Listening for claps...")

    while True:

        time.sleep(0.1)