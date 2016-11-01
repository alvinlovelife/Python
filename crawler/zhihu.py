import gzip
import re
import http.cookiejar
import urllib.request
import io
import sys
import os
# 爬取网页
__URL__ = 'https://www.zhihu.com/'
# 保存cookie路径
__cookiePATH__ = "F:\\cookie.txt"
# 保存网页内容
__savePATH__ = "F:\\test.html"
# 图片保存路径
__targetPATH__ = "F:\\test\\zhihu" 
# 创建MozillaCookieJar实例对象
_cookie = http.cookiejar.MozillaCookieJar()
def saveFile(data):
    f_obj = open(__savePATH__, 'wb') # wb 表示打开方式
    f_obj.write(data)
    f_obj.close()
#提取文件名，保存同名到本地路径
def destFile(path):
	if not os.path.isdir(__targetPATH__):
		os.mkdir(__targetPATH__)
	pos = path.rindex('/')  
	t = os.path.join(__targetPATH__, path[pos+1:])
	return t  
#解压函数
def unzip(data):
    try:        # 尝试解压
        print('正在解压.....')
        data = gzip.decompress(data)
        print('解压完毕!')
    except:
        print('未经压缩, 无需解压')
    return data
#获取_xsrf 
def getXSRF(data):
    cer = re.compile('name="_xsrf" value="(.*)"', flags = 0)
    strlist = cer.findall(data)
    print("strlist:",strlist)
    return strlist[0]
#构造文件头
def getOpener(head):
    #设置一个cookie处理器，它负责从服务器下载cookie到本地，并且在发送请求时带上本地的cookie
    handler = urllib.request.HTTPCookieProcessor(_cookie)
    opener = urllib.request.build_opener(handler)
    header = []
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    opener.addheaders = header
    return opener
#构造header，一般header至少要包含一下两项。这两项是从抓到的包里分析得出的。   
header = {
    'Connection': 'Keep-Alive',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    # 'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.zhihu.com',
    'DNT': '1'
}
# 改变标准输出的默认编码，因为pyhon本身Unicode对部分UTF-8不支持
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') 

def _init():
	global _cookie
    ###一、有cookie登陆，从文件中读取cookie内容到变量,用cookie登陆信息###
	# _cookie.load(__cookiePATH__, ignore_discard=True, ignore_expires=True)
	# opener = getOpener(header)

	###二、没有cookie登陆，发起三次请求###
	opener = getOpener(header)
	# 第一次请求，获取返回的_xsrf值
	response = opener.open(__URL__)
	data = response.read()
	data = unzip(data)     # 解压
	_xsrf = getXSRF(data.decode()) #
	#post数据接收和处理的(登陆)页面（我们要向这个页面发送我们构造的Post数据）
	loginUrl = 'https://www.zhihu.com/login/email'
	id = '邮箱账号'
	password = '邮箱密码'
	#构造Post数据，他也是从抓大的包里分析得出的。
	postDict = {
	        '_xsrf':_xsrf, #特有数据，不同网站可能不同  
	        'password': password,
	        'captcha_type':'cn',
	        'remember_me':'true',
	        'email': id
	}
	#需要给Post数据编码  
	postData = urllib.parse.urlencode(postDict).encode()
	# 第二次请求，登陆并获取登陆结果
	response = opener.open(loginUrl, postData)
	# 登陆成功后保存cookie
	_cookie.save(__cookiePATH__,ignore_discard = True,ignore_expires = True)
	# 显示登陆请求后的返回值
	data = response.read()
	data = unzip(data)
	print("response:",data.decode())

	# 第三次请求，登陆后再次发起实际请求
	response = opener.open(__URL__)
	data2 = response.read()
	saveFile(data2)
	data2 = unzip(data2)
	# print("result:",data2.decode())

	contentBytes = data2.decode("utf8")
    #正则表达式查找所有的图片
	for link,t in set(re.findall(r'(https:[^s]*?(jpg|png|gif))', str(contentBytes))):
		print(link)
		try: 
			urllib.request.urlretrieve(link, destFile(link)) #下载图片
		except Exception as e:
 			print('下载图片失败:',e)#异常抛出

_init()