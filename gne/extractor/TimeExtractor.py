import re
from ..utils import config
from lxml.html import HtmlElement
from ..defaults import DATETIME_PATTERN, PUBLISH_TIME_META


class TimeExtractor:
    def __init__(self):
        self.time_pattern = DATETIME_PATTERN

    def unify_publish_time(self, publish_time):
        '''
        功能:处理时间为统一格式
        :param data: str 时间字符串
        :return:
        '''
        if not publish_time:
            return None
        publish_time = re.sub(r'年|月|/|\.', '-', publish_time)
        publish_time = re.sub(r'时|分', ':', publish_time)
        date = re.sub(r'日|秒', ' ', publish_time)
        return date

    def extract_from_user_xpath(self, publish_time_xpath: str, element: HtmlElement) -> str:
        if publish_time_xpath:
            publish_time = ''.join(element.xpath(publish_time_xpath))
            return publish_time
        return ''

    def extract_from_text(self, element: HtmlElement) -> str:
        # 修改text的xpath, 变成提取body下的text,
        # 如果直接提取全文的text，会受某些网页meta/head下的script内容影响, 导致提到的第一个时间不是精确时间
        text = ''.join(element.xpath('//body//text()'))
        time_list = []
        for dt in self.time_pattern:
            dt_obj = re.search(dt, text)
            if dt_obj:
                time_list.append(dt_obj)

        if len(time_list) == 0:
            return ''
        # 将所有提取日期按照位置信息排序, 排序方式为按照字符起始位置升序，
        # 若起始位置相同, 则按照字符长度降序排序 即为 起始位置- 终止位置 的差值（负值）升序
        sorted_time = sorted(time_list, key=lambda x: (x.span()[0], x.span()[0]-x.span()[1]))
        # 发布时间一般会在详情页中所有时间的第一个 即为排序后的第一个值
        return sorted_time[0].group(1)

    def extract_from_meta(self, element: HtmlElement) -> str:
        """
        一些很规范的新闻网站，会把新闻的发布时间放在 META 中，因此应该优先检查 META 数据
        :param element: 网页源代码对应的Dom 树
        :return: str
        """
        for xpath in PUBLISH_TIME_META:
            publish_time = element.xpath(xpath)
            if publish_time:
                return ''.join(publish_time)
        return ''

    def extractor(self, element: HtmlElement, publish_time_xpath: str = '') -> str:
        publish_time_xpath = publish_time_xpath or config.get('publish_time', {}).get('xpath')
        publish_time = (self.extract_from_user_xpath(publish_time_xpath, element)  # 用户指定的 Xpath 是第一优先级
                        or self.extract_from_meta(element)   # 第二优先级从 Meta 中提取
                        or self.extract_from_text(element))  # 最坏的情况从正文中提取
        return self.unify_publish_time(publish_time)   # 将所有日期处理成统一格式
