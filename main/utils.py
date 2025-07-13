# main/utils.py
import logging
import threading
import time
import hashlib
import requests
from django.utils import timezone

from django.conf import settings

from main.models import HistoryScan, WebsiteHTML

logger = logging.getLogger(__name__)

def scanWebsite():
    websites = WebsiteHTML.objects.all()

    compare_html(websites)

    compare_checksum(websites)



            

            
def compare_html(websites):
    for site in websites:

        url = site.app_url
        old_html = site.html_content
        print(f"== scanWebsite Scanning HTML{url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            new_html = response.text

            if new_html.strip() == old_html.strip():
                status = 'normal'
                HistoryScan.objects.create(
                app_id=site.id,
                app_name=site.app_name,
                app_url=site.app_url,
                method='compare-html',
                status='normal',
                scan_time=timezone.now()
            )
            else:
                status = 'attacked'
                HistoryScan.objects.create(
                app_id=site.id,
                app_name=site.app_name,
                app_url=site.app_url,
                method='compare-html',
                status='attacked',
                scan_time=timezone.now()
                )
            logger.info(f"Scanned {url} - {status}")
        except Exception as e:
            logger.exception(f"Failed to scan {url}: {e}")

def compare_checksum(websites):
    for site in websites:
        url = site.app_url
        old_html = site.html_content.strip()

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            new_html = response.text.strip()

            old_checksum = hashlib.md5(old_html.encode('utf-8')).hexdigest()
            new_checksum = hashlib.md5(new_html.encode('utf-8')).hexdigest()

            if old_checksum == new_checksum:
                status = 'normal'
            else:
                status = 'attacked'

            # Lưu kết quả vào HistoryScan
            HistoryScan.objects.create(
                app_id=site.id,
                app_name=site.app_name,
                app_url=site.app_url,
                method='checksum-md5',
                status=status,
                scan_time=timezone.now()
            )

            print(f"[checksum] Scanned {url} - {status}")
        except Exception as e:
            print(f"[checksum] Failed to scan {url}: {e}")


def start_scheduler():
    def job():
        scanWebsite()
        interval = settings.SCAN_INTERVAL_SECONDS
        t = threading.Timer(interval, job)
        t.daemon = True
        t.start()

    print("== Scheduler started ==")
    job()