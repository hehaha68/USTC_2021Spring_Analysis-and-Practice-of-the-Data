# -*- coding:utf-8 -*-
# author:和泳毅
# time:2021/3/22
# topic:实验2-数据爬取
# file:exp2.py


import os
import time
import requests
from lxml import etree
import PySimpleGUI as sg
from urllib.request import urlretrieve


url = []  # 待访问链接列表
flag = 0  # 全局变量，控制文件夹的创建
# 地区列表
area = ['全国III', '全国II', '全国I', '北京', '天津', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南', '四川', '贵州',
        '云南', '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽', '福建', '陕西', '甘肃', '青海', '广西',
        '内蒙古', '宁夏', '重庆', '上海', '福建', '西藏', '新疆']
# 科目列表
subject = ['理综', '文综', '语文', '数学（文科）', '数学（理科）', '数学', '英语', '政治', '地理', '历史', '物理', '化学', '生物']


# 下载至本地
def load_url(url, num):
    global flag
    k = 0
    j = -1
    r = requests.get(url)
    content = etree.HTML(r.content)
    topic = content.xpath('/html/body/div[2]/div/div[2]/div[2]/span/text()[4]')[0]  # 读取标题
    topic = topic.replace('>', '')  # 观察读取结果发现存在'>'和' '冗余字符
    topic = topic.replace(' ', '')  # 去除标题字符串的冗余字符
    while j < 0:
        j = topic.find(area[k])
        k += 1
    this_area = area[k - 1]  # 与地区列表匹配得到考卷地区
    k = 0
    j = -1
    while j < 0:
        j = topic.find(subject[k])
        k += 1
    this_subject = subject[k - 1]  # 与科目列表匹配得到考卷科目
    name = topic[0:4] + '_' + this_area + '_' + this_subject  # 文件名格式
    folder_name = 'gaokao\\' + topic[0:4] + '_' + this_area + '_' + this_subject  # 文件夹名格式
    if flag == 0:  # 每套题只建一次文件夹
        flag = 1
        os.makedirs(folder_name, exist_ok=True)  # 建立文件夹，若文件夹名已存在则不报错
    # 待下载文件为.docx文件
    if topic.find('word') != -1:  # 观察标题发现文档版试题在标题里有'word'字符串
        href = content.xpath('/html/body/div[2]/div/div[2]/div[3]/div[2]/div/div[2]/p[3]/a/@href')
        if href != 0 and len(href) > 0:
            path = folder_name + '\\' + name + '.docx'  # 文档命名规范
            urlretrieve(href[0], path)  # 下载至本地
            print(name + '.docx', '下载完成！')
    # 待下载文件为.jpg文件
    else:
        src = content.xpath('/html/body/div[2]/div/div[2]/div[3]/div[2]/div/div[2]/p/img/@src')
        path = folder_name + '\\' + name + '_' + str(num) + '.jpg'  # 图片命名规范
        urlretrieve(src[0], path)   # 下载至本地
        print(name + '_' + str(num) + '.jpg', '下载完成！')
    return name     # 返回套卷名

# 读取一套题的全部链接列表
def next_url(url):
    url_list = []
    url_list += [url]  # 添加第一页的链接
    page = 2  # 从第二页开始循环获取链接
    r = requests.get(url)
    content = etree.HTML(r.content)
    href = 'true'   # 赋初值以开始循环
    while href != 0 and len(href) > 0:
        #  str(page)控制页数
        href = content.xpath('/html/body/div[2]/div/div[2]/div[3]/div[2]/div/div[2]/div[2]/a[' + str(page) + ']/@href')
        if href != 0 and len(href) > 0:
            url_list += href   # 添加链接至列表
        page += 1
    return url_list     # 返回每套题的全部链接列表


# 将试题索引页面body标签代码存入一个txt文件，获取足够的套卷首页链接列表
def get_url():
    i = 2
    n = 0
    global url
    parser = etree.HTMLParser(encoding="utf-8")
    content = etree.parse('html.txt', parser=parser)
    # 观察网页，最大深度约为100，最大宽度为4，要求套数为30
    while i < 100 and n < 30:
        j = 1
        while j <= 4:
            href = content.xpath(
                '/html/body/div[3]/div/div[1]/div[5]/div[5]/div/div[1]/table/tbody/tr[' + str(i) + ']/td[' + str(
                    j) + ']/a[1]/@href')  # 不断读取下一个链接
            if href != [''] and len(href) > 0 and href[0][-1] == 'l':  # 将错误的链接剔除
                url += href
                n += 1
            j += 1
        i += 1


if __name__ == "__main__":
    url = []
    get_url()  # 获取足够的链接
    for i in range(30):
        num = 0     # 图片类型试卷的编号
        flag = 0
        this_url = next_url(url[i])  # 获取每套试卷的全部链接，列表长度为试卷张数
        this_url.pop()  # 删除多余的链接（最后一页的下一页为无效链接）
        print('第%d套：' % (i + 1))
        j = 0
        while j < len(this_url) and len(this_url[j]) > 0:
            num += 1
            #   下载并生成进度条界面
            topic = '第'+str(i+1)+'套： '+load_url(this_url[j], num).replace('_',' ')  # 规范化进度条标题
            sg.one_line_progress_meter(topic, j + 1, len(this_url), '-key-')
            time.sleep(1)
            j += 1
    sg.popup_ok_cancel('Finish!')  # 完成爬取
    print('30套高考试卷下载完毕')