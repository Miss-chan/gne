import re
from typing import List

from ..utils import config
from lxml.html import HtmlElement
from ..defaults import TITLE_HTAG_XPATH, TITLE_SPLIT_CHAR_PATTERN
import difflib

class Title():
    text = ''
    tag = ''
    similar = 0

    TAG_TITLE = 0
    TAG_H = 1
    TAG_TABLE = 2

    def __init__(self, text, tag, similar):
        self.text = text
        self.tag = tag
        self.similar = similar


class TitleExtractor:
    def extract_by_xpath(self, element, title_xpath):
        if title_xpath:
            title_list = element.xpath(title_xpath)
            if title_list:
                return title_list[0]
            else:
                return ''
        return ''

    def extract_by_title(self, element) -> List["Title"]:
        title_list = element.xpath('//title/text()')
        if len(title_list) == 0:
            return []
        # title标签下的标题一般会有 - 或者 | 等符号，首先进行分割
        split_titles = re.split(TITLE_SPLIT_CHAR_PATTERN, title_list[0])
        return self.filter_titles(split_titles, tag=Title.TAG_TITLE)

    def extract_by_htag(self, element) -> List["Title"]:
        title_list = element.xpath(TITLE_HTAG_XPATH)
        return self.filter_titles(title_list, tag=Title.TAG_H)

    def extract_by_table(self, element) -> List["Title"]:
        """  Taoz添加 一些老式网站会用table中的，class或者id带有title的元素作为标题 """
        class_titles = element.xpath('*//table//*[contains(@class, "title")]/text()')
        id_titles = element.xpath('*//table//*[contains(@id, "title")]/text()')
        return self.filter_titles(class_titles + id_titles, tag=Title.TAG_TABLE)

    @staticmethod
    def filter_titles(title_list: list, tag: int) -> List["Title"]:
        """ Taoz 添加，丢弃小于6个字的title，并按照字数长度排序 """
        titles = []
        for title in title_list:
            _t = title.strip()
            if len(_t) > 5:
                titles.append(Title(text=_t, tag=tag, similar=0))
        return sorted(titles, key=lambda x: len(x.text), reverse=True)

    def extract(self, element: HtmlElement, title_xpath: str = ''):
        # 如果配置了精确的xpath并提取到数据，直接返回xpath
        xpath_title = self.extract_by_xpath(element, title_xpath)
        if xpath_title:
            return xpath_title

        title_titles = self.extract_by_title(element)
        h_titles = self.extract_by_htag(element)
        table_titles = self.extract_by_table(element)

        # 如果title数组全部都没有值 返回空字符串
        if not any([title_titles, h_titles, table_titles]):
            return ''

        # 将三个数组合成一个，不同类型之间两两计算相似度，取相似度最大的作为返回值
        titles_dim1 = title_titles + h_titles + table_titles
        for i in range(len(titles_dim1) - 1):
            for j in range(i + 1, len(titles_dim1)):
                ti = titles_dim1[i]
                tj = titles_dim1[j]

                if ti.tag != tj.tag:
                    sim = difflib.SequenceMatcher(None, ti.text, tj.text).quick_ratio()
                    if sim > ti.similar:
                        ti.similar = sim

                    if sim > tj.similar:
                        tj.similar = sim

        sorted_titles = sorted(titles_dim1, key=lambda x: x.similar, reverse=True)
        result = sorted_titles[0].text

        # 标题中有 -| 这样的分隔符时，在title标签中被分割了，只能提取到一半的内容
        # 如果h或table标签中 也提到了相关度较高的标题，返回按照字数较多的那一个标题
        # example:
        #   https://politics.gmw.cn/2020-06/02/content_33881458.htm
        #   标题：抗美援朝金曲|《中国人民志愿军战歌》是怎样炼成的
        #   可以正确返回标题，而不是返回 《中国人民志愿军战歌》是怎样炼成的
        if len(sorted_titles) > 1:
            for k in range(1, len(sorted_titles)):
                sim = sorted_titles[k].similar
                if sim == sorted_titles[0].similar and sim > 0.5:
                    next_title = sorted_titles[k].text
                    if len(next_title) > len(result):
                        result = next_title
        return result