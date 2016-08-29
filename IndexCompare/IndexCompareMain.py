# -*- coding: utf-8 -*-
import IndexCompareURLManager
import IndexCompareDownloader
import IndexCompareOutputer
import IndexCompareParser

class IndexCompareMain:
    def __init__(self):
        self.url_manager = IndexCompareURLManager()
        self.html_downloader = IndexCompareDownloader()
        self.html_paser = IndexCompareParser()

    #先定接口，再做实现，其中首页特殊处理一下
    def craw(self, homeurl):

        #先处理首页
        home_content = self.html_downloader.download(homeurl)
        if home_content is None:
            return

        funds_info = self.html_paser.parse_home(home_content)
        if funds_info is None:
            return

        while (not self._url_manager.is_empty):
            pass


if __name__ == "__main__":
    icMain = IndexCompareMain()
    icMain.craw('http://fund.eastmoney.com/allfund.html')