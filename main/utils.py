# main/utils.py
import logging
import threading
import time
import requests
from django.utils import timezone

from django.conf import settings

from main.models import HistoryScan, WebsiteHTML

logger = logging.getLogger(__name__)

def scanWebsite():
    websites = WebsiteHTML.objects.all()

    for site in websites:

        url = site.app_url
        old_html = site.html_content
        print(f"== scanWebsite Scanning URL: {url}")
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

            # Save scan result
            

            logger.info(f"Scanned {url} - {status}")
        except Exception as e:
            logger.exception(f"Failed to scan {url}: {e}")

            # Optional: Lưu scan lỗi
            

def start_scheduler():
    def job():
        scanWebsite()
        interval = settings.SCAN_INTERVAL_SECONDS
        t = threading.Timer(interval, job)
        t.daemon = True
        t.start()

    print("== Scheduler started ==")
    job()