# -*- coding: utf-8 -*-
import re
from lxml import etree
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
class FundInfo(object):
    #一些我比较感兴趣的资讯参数
    code = u''
    CODE_KEY = u'基金代码'

    short_name = u''
    SHORT_NAME_KEY = u'基金简称'

    full_name = u''
    FULL_NAME_KEY = u'基金全称'

    type = u''
    TYPE_KEY = u'基金类型'

    release_time = u''
    RELEASE_TIME_KEY = u'发行日期'

    capacity = u''
    CAPACITY_KEY = u'资产规模'

    company = u''
    COMPANY_KEY = u'基金管理人'

    manager = []
    MANAGER_KEY = u'基金经理人'

    compare_target = u''
    COMPARE_TARGET_KEY = u'业绩比较基准'

    trace_target = u''
    TARCE_TARGET_KEY = u'跟踪标的'

    policy = u''
    POLICY_KEY = u'投资策略'

    url = u""

    #所有资讯都放在里面,键也是直接使用资讯的中文了嘻嘻
    raw_info = dict()

    def __init__(self, content):
        html = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
        ths = html.xpath('//table//th')
        tds = html.xpath('//table//td')
        for index, th in enumerate(ths):
            key = th.text.strip()
            if len(key) == 0:
                continue
            if tds[index].text == None:
                alist = tds[index].xpath('./a')
                if alist != None and len(alist) > 0:
                    value = alist[0].text.strip()
                else:
                    #这里有些比如最高申购费什么的
                    spans = tds[index].xpath('./span')
                    if spans != None:
                        value = spans[len(spans)-1].text.strip()
                    else:
                        value = u""
            else:
                value = tds[index].text.strip()
            self.raw_info[key] = value

            if key == self.CODE_KEY:
                #code也分前后端等,懒得管了,就取第一个
                value = value[:6]
                self.code = value
                self.raw_info[key] = value
            elif key == self.SHORT_NAME_KEY:
                self.short_name = value
            elif key == self.FULL_NAME_KEY:
                self.full_name = value
            elif key == self.TYPE_KEY:
                self.type = value
            elif key == self.RELEASE_TIME_KEY:
                self.release_time = value
            #去掉后面单位和描述只保留数字
            elif key == self.CAPACITY_KEY:
                #某些基金新开或者其他原因没有规模
                if len(value.split(u'亿')) > 0:
                    value = value.split(u'亿')[0]
                self.capacity = value
                self.raw_info[key] = value
            #这里是个超链接
            elif key == self.COMPANY_KEY:
                self.company = value
            elif key == self.MANAGER_KEY:
                value = []
                #特别处理下基金经理这块,因为可能是多人,其实还可能有重名的情况,不过暂且相信一个基金公司下的基金经理不会重名吧
                managers = tds[index].xpath('./a')
                for managerName in managers:
                    value.append(managerName.text.strip())
                self.raw_info[key] = value
                self.manager = value
            elif key == self.COMPARE_TARGET_KEY:
                self.compare_target = value
            elif key == self.TARCE_TARGET_KEY:
                self.trace_target = value

        #然后是几个大的
        divs = html.xpath('//div[@class="boxitem w790"]//label[@class="left"]')
        ps = html.xpath('//div[@class="boxitem w790"]//p')
        for (index, div) in enumerate(divs):
            key = div.text.strip()
            #暂时跳过"基金分级信息"这块
            if key == u"基金分级信息":
                continue
            value = ps[index].text.strip()
            self.raw_info[key] = value
            if key == self.POLICY_KEY:
                self.policy = value
        # large_divs = soup.find_all('div', {"class" : "boxitem w790"})
        # for large_div in large_divs:
        #     key = large_div.find('label', {"class" : 'left'}).text.strip()
        #     #暂时跳过"基金分级信息"这块
        #     if key == u"基金分级信息":
        #         continue
        #     value = large_div.find('p').text.strip()
        #     self.raw_info[key] = value
        #     if key == self.POLICY_KEY:
        #         self.policy = value


class IndexCompareParser(object):

    #解析首页主要是获取每个基金的一些基础信息,如基金名,id
    def parse_home(self, home_content):
        if home_content is None:
            return None
        home_content = home_content.decode('gbk')
        html = etree.HTML(home_content, parser=etree.HTMLParser(encoding='utf-8'))
        alinks = html.xpath('//a[@href]')

        pattern_capture = re.compile(ur"（(\d{6})）(.+)")
        l = []
        for alink in alinks:
            aa = alink.text
            if aa != None:
                match = pattern_capture.match(aa)
                if match:
                    l.append((match.group(1), match.group(2)))

        return l

    #这里是解析每个基金的详情了,获得的东西很多,反正都在dict里,键可能会逐步增加,根据未来需要分析的东西扩展
    def parse_fund(self, fund_content, fund_url):
        if fund_content is None or fund_url is None:
            return None

        fund_info = FundInfo(fund_content)
        fund_info.url = fund_url
        return fund_info