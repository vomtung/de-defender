# main/utils.py
import threading
import time

from django.conf import settings

def scanWebsite():
    print("== scanWebsite called ==")
    # TODO: 

def start_scheduler():
    def job():
        scanWebsite()
        interval = settings.SCAN_INTERVAL_SECONDS
        t = threading.Timer(interval, job)
        t.daemon = True
        t.start()

    print("== Scheduler started ==")
    job()