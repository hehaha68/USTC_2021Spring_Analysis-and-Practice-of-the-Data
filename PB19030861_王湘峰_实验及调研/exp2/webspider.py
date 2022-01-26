1# 本程序用于爬取高考网（www.gaokao.com/zyk/qkst）的历年真题，爬取数量为30套
from requests_html import HTMLSession
import requests
import os


def get_all_links():  #此函数用于获得“题库”页面下的所有卷子的网址（基地址）
    url = "http://www.gaokao.com/zyk/gkst/"
    response = session.get(url=url)
    response.encoding = 'utf-8'
    element = response.html.xpath("//tr[@class='tag_con_st']/td/a")
    Links = {}
    for e in element:
        if len(e.attrs) > 3:  #需要忽略不是网址的网页元素
            if '答案' in e.attrs['title'] or '评析' in e.attrs['title'] or '开始' in e.attrs['title']:
                pass
            elif e.attrs['href'] == '':
                pass
            else:
                x = {e.attrs['title']: e.attrs['href']}
                Links.update(x)
        else:
            pass
    return Links   #Links是一个字典，它的key是“X年X省XX科目”，value是对应的网站


def get_src(url):  #得到网址为url的网站所包含第一张图片的src
    response = session.get(url=url)
    response.encoding = 'utf-8'
    img_src = response.html.xpath("//div[@class='content_txt']/p/img", first=True)
    if img_src:
        src = img_src.attrs['src']
    else:
        src = None
    return src     #src是字符串型变量，它代表着XX.jpg


def get_filename(basename):  #为了使命名统一规范，需要引入函数对文件名做处理
    year = basename[:4]
    pro = sub = ''
    for pro in province:
        if pro in basename:
            break
                            #这两步得到该试卷的省份（pro）以及科目（sub）信息
    for sub in subject:
        if sub in basename:
            break

    filename = year+'_'+pro+'_'+sub+'_'
    return filename


def download_picture(filename, counter, src):
    if src:
        print('正在爬第', counter, '页')
        picture = requests.get(src)   #此处url应当是src属性的字符串
        if not os.path.exists('webspider\\'+basename): #将每个科目打包成文件夹，并生成一个文件夹
            os.makedirs('webspider\\'+basename)
        if not os.path.exists('webspider\\'+basename+'\\'+filename+str(counter)+'.jpg'):
            with open('webspider\\'+basename+'\\'+filename+str(counter)+'.jpg', 'wb+') as f:
                f.write(picture.content)
                f.close()                   #有时某个文件已经被爬过了，为了提高效率增加了检测机制
        return True
    else:
        return False


def get_next_pages(url):  #由于试题用了很多个页面来装载，所以需要得到所有的页面
    while True:
        response = session.get(url=url)
        response.encoding = 'utf-8'
        page_list = response.html.xpath("//div[@class='pages']/a")
        next_page = page_list[-1]   #nextpage代表“下一页”按钮
        if len(next_page.attrs) < 1:  #判断是否是最后一页了
            return None
        else:
            return next_page.attrs['href']       #pages是由所有页面的网址组成的列表


if __name__ == '__main__':
    session = HTMLSession()
    province = ['北京', '上海', '广东', '天津', '重庆', '江苏', '山东', '浙江', '湖北', '四川', '广西',
                '湖南', '辽宁', '海南', '宁夏', '福建', '甘肃', '河北', '江西', '吉林', '云南', '河南',
                '陕西', '山西', '安徽', '新疆', '西藏', '贵州', '青海', '黑龙江', '内蒙古'
                '全国卷', '全国卷2', '全国卷3']
    subject = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理', '文综', '理综']
    i = 0
    num = int(input('请问爬几套？\n'))
    sigema = 0   #sigema用于记录总共的卷子数
    dictionary = get_all_links()  #将所有的指向卷子的链接和名称存到一个字典中
    for basename, baseurl in dictionary.items():
        if i < num:    #要求爬取30 套 题目
            print('正在爬第', i+1, '套：', basename)
            counter = 1     #counter用来计数目前正在爬取一套卷子的第几页
            next_page = baseurl
            filename = get_filename(basename) #filename包含年份省份科目信息3
            while True:
                true_src = get_src(next_page)
                if download_picture(filename, counter, true_src):
                    next_page = get_next_pages(next_page)
                else:
                    break
                if not next_page:
                    break
                counter += 1
            sigema += counter
            i += 1
        else:
            pass
    print('爬完了，好耶！')
    print('共计爬取试卷'+str(i)+'套'+str(sigema)+'页')
    #完成目标
