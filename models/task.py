from uuid import uuid1
from tempfile import mkdtemp
from os import path, remove
from queue import Queue
from threading import Thread

from kivy.network.urlrequest import UrlRequest

CHUNK_SIZE = 4098


class DownloadTask(object):
    def __init__(self, url: str, threads: int, download_report: Queue, download_path):
        self.url = url
        self.threads = threads
        self.content_length = 0
        self.total_downloaded = 0
        self.download_path = download_path
        self.download_report = download_report
        self.bytes_downloaded_per_thread = {}
        self.requests = {}
        self._get_headers()

    def _get_headers(self):
        UrlRequest(url=self.url, on_success=self._on_headers_fetched, method='HEAD')

    def _on_headers_fetched(self, req, resp):
        self.content_length = int(req.resp_headers.get('Content-Length'))
        self._start_requests()

    def _start_requests(self):
        """
        Each requests takes responsibility for a part of the file by passing range to its header.
        Storing the requests to self.requests; key: thread.ident, value: temp_path 
        """
        shares = self.content_length / self.threads
        for i in range(self.threads):
            bytes_range = 'bytes={}-{}'.format(i * shares, (shares + (i * shares)))
            temp_path = self.temp_path()
            thread = UrlRequest(
                self.url,
                file_path=temp_path,
                req_headers={'Range': bytes_range},
                on_progress=self._on_requests_progress,
                on_success=self._on_request_success,
            )
            self.requests[thread] = temp_path

    def _on_requests_progress(self, req, current, total):
        self.bytes_downloaded_per_thread[req.ident] = current
        self._calculate_total_downloaded()

    def _on_request_success(self, req, resp):
        """Append the downloaded files"""
        # Check to see if all threads are done
        for thread, tmp_path in self.requests.items():
            if not thread.is_finished:
                return
        finalize = Thread(target=self._wrap_them_up, daemon=True)
        finalize.start()

    def _wrap_them_up(self):
        """Read files one by one and put them all together"""
        with open(self.final_path, 'wb') as final:
            for thread, tmp_path in self.requests.items():
                with open(tmp_path, 'rb') as tmp:
                    while True:
                        chunk = tmp.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        final.write(chunk)
        self.clean_up()

    def _calculate_total_downloaded(self):
        for k, v in self.bytes_downloaded_per_thread.items():
            self.total_downloaded += v
        self.download_report.put((self.total_downloaded, self.content_length))

    def clean_up(self):
        """Clean the temp files"""
        for thread, tmp_path in self.requests.items():
            remove(tmp_path)

    @staticmethod
    def temp_path():
        """Suggesting a temporary file for storing the downloaded chunk"""
        return path.join(mkdtemp(), str(uuid1()))

    @property
    def final_path(self):
        return path.join(self.download_path, self.filename)

    @property
    def filename(self):
        return self.url.split('/')[-1]
