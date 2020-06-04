#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : run.py
# @Time    : 2020-6-1 16:40
# @Software: PyCharm
# @Author  : Taoz
# @contact : xie-hong-tao@qq.com
import difflib
import requests
from gne import GeneralNewsExtractor
from test_urls import urls

extractor = GeneralNewsExtractor()
for url in urls:
    res = requests.get(url)
    html = res.content
    # html = html.decode(res.encoding)
    try:
        html = html.decode('gbk')
    except Exception:
        html = html.decode('utf8')
    result = extractor.extract(html, noise_node_list=['//div[@class="comment-list"]'])
    print(result)


