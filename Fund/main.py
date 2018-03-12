# -*- coding: utf-8 -*-
from url_manager import *
from downloader import *
from parser import *
from collector import *
from url_manager import FundURLIndex

class FundMain(object):

    def __init__(self):
        self.url_manager = FundURLManager()
        self.html_downloader = FundDownloader()
        self.html_paser = FundParser()
        self.collector = FundCollector()

    #先定接口，再做实现，其中首页特殊处理一下,基金三个月才出一次一次季报,如果不是数据结构改了大部分时间没必要全量更新
    def crawl(self, homeurl, incremental=True):
        # 先处理首页
        home_content = self.html_downloader.download(homeurl)
        if home_content is None:
            return

        funds_info = self.html_paser.parse_home(home_content)
        if funds_info is None:
            return

        count = 0
        finished_count = [0]

        for fund_info_code in funds_info:
            #全量更新或者新的基金才下载
            if not incremental or not self.collector.fundexist(fund_info_code):
                self.url_manager.add_url(fund_info_code)
                count += 1

        print '共需爬取基金详情 ' + str(count) + " 个"

        def inner_crawl(isretry=False):
            if isretry:
                self.url_manager.transfer_url()

            while (not self.url_manager.is_empyt() and not self.url_manager.is_overflow()):
                urls = self.url_manager.pop_url()
                fundcode = urls[FundURLIndex.CODE.value]
                try:
                    #简化一下问题,只有所有相关页面都下载完毕才算ok
                    print 'start parse ' + urls[FundURLIndex.MAIN.value]
                    basecontent = self.html_downloader.download(urls[FundURLIndex.BASE.value])
                    ratiocontent = self.html_downloader.download(urls[FundURLIndex.RATIO.value])
                    statisticcontent = self.html_downloader.download(urls[FundURLIndex.STATISTIC.value])
                    stockscontent = self.html_downloader.download(urls[FundURLIndex.STOCKS.value])
                    annualcontent = self.html_downloader.download(urls[FundURLIndex.ANNUAL.value])
                    #只要有一个失败就都重试哦,其实也有个别网页是真的不存在,但懒得管了
                    if basecontent is None or len(basecontent) == 0 or ratiocontent is None or len(ratiocontent) == 0\
                            or statisticcontent is None or len(statisticcontent) == 0 or stockscontent is None or len(stockscontent) == 0 \
                            or annualcontent is None or len(annualcontent) == 0:
                        print 'download fund ' + fundcode + ' failed'
                        self.url_manager.fail_url(fundcode)
                        continue
                    self.url_manager.finish_url(fundcode)
                    result = self.html_paser.parse_fund(basecontent, ratiocontent, statisticcontent, stockscontent, annualcontent, urls[FundURLIndex.MAIN.value])
                    self.collector.addFund(result)
                    finished_count[0] += 1
                    print 'finish parse fund ' + fundcode + " " + str(finished_count[0]) + '/' + str(count)
                except Exception as e:
                    print 'parse fund ' + fundcode + ' fail, cause ' + str(e)
                    self.url_manager.fail_url(fundcode)

        #尝试重试两次吧,因为第一时间就重试其实很可能还是出错
        inner_crawl()
        inner_crawl(True)
        inner_crawl(True)

        print 'success finish parse url sum ' + str(finished_count[0])
        print 'failed urls is'
        self.url_manager.output_faileds()


if __name__ == "__main__":
    icMain = FundMain()
    icMain.crawl('http://fund.eastmoney.com/allfund.html', False)

    # url_manager = SBURLManager()
    # # http://m.zhcw.com/clienth5.do?lottery=FC_SSQ&kjissue=2005001&transactionType=300302&src=0000100001%7C6000003060
    # for year in range(2005, 2018):
    #     for index in range(1, 160):
    #         url_manager.add_url("http://m.zhcw.com/clienth5.do?lottery=FC_SSQ&kjissue=" + str(year) + '{0:03}'.format(index) + "&transactionType=300302&src=0000100001%7C6000003060")
    #
    # import json
    # downloader = SBDownloader()
    # parse_count = 0
    # areaDic = dict()
    # while (not url_manager.is_empyt()):
    #     url = url_manager.pop_url()
    #     content = downloader.download(url)
    #     # 懒得重试了哦
    #     if content is not None and len(content) > 0:
    #         d = json.loads(content)
    #         l = d.get("dataList", None)
    #         if l is not None:
    #             parse_count += 1
    #             for info in l:
    #                 area = info['dqname']
    #                 ones = int(info["onez"])
    #                 money = int(info['tzmoney'])
    #                 sum = areaDic.get(area, None)
    #                 if sum is None:
    #                     areaDic[area] = (ones, money)
    #                 else:
    #                     areaDic[area] = (sum[0] + ones, sum[1] + money)
    #
    # # 最后输出结果
    # print "统计双色球地域特性共" + str(parse_count) + "期"
    #
    # areaResult = dict()
    # for area in areaDic:
    #     count = areaDic[area][0]
    #     money = areaDic[area][1]
    #     if count > 0:
    #         average = money / count
    #     else :
    #         average = 10000000000
    #     # print area + '购买彩票共' + str(money) + '元, 共', str(count) + "人中头奖, 平均每花" + average + "出一个头奖嘻嘻"
    #     areaResult[area] = average
    #
    # print '按照平均花费中头奖金额排序:'
    # for key, value in sorted(areaResult.iteritems(), key=lambda (k,v): (v,k)):
    #     print "%s每花%d万可出一个头奖" % (key, value/10000)
