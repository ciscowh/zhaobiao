'''
拿到网址后观察页面，发现随着页数的变化地址栏中的网址并没有变化，此网站可能是动态加载的，随之F12进行检查，在network--》xhr中找到.do文件发现其中的响应就是我们要的数据，数据是json格式，然后看到该接口网址为post请求，提交的参数中有三个关键参数（后期发现参数要全部都进行提交），然后就可以编写程序了，将解析的数据以CSV格式进行保存。
程序运行后发现网站在爬取30多页数据后就会出现封ip等反扒行为，然后进行配置代理ip，随机请求头，设置休眠时间延迟爬虫请求速度等措施。
'''
import requests,random,json,csv
from ProxyPool_master.get_proxy import get_proxy
from fake_useragent import UserAgent


class Spider(object):
    def __init__(self):
        self.url = 'http://www.cebpubservice.com/ctpsp_iiss/searchbusinesstypebeforedooraction/getStringMethod.do'
        self.ip_list = get_proxy()
        self.headers = {"User-Agent": UserAgent().random}
        self.big_list = []

    def get_response(self, page):
        for i in range(1, page+1):
            data = {
                'searchName': '',
                'searchArea': '',
                'searchIndustry': '',
                'centerPlat': '',
                'searchTimeStart': '',
                'searchTimeStop': '',
                'timeTypeParam': '',
                'bulletinIssnTime': '',
                'bulletinIssnTimeStart': '',
                'bulletinIssnTimeStop': '',
                'businessType': '招标公告',
                'pageNo': i,
                'row': '15',
            }
            try:
                response = requests.post(self.url, proxies=self.ip_list, headers=self.headers, data=data)
                if response.status_code == 200:
                    print("请求{}地址成功".format(response.url))
            except Exception as e:
                print("The reason for the failure is", e)
            else:
                # print(response.text)
                self.get_data(response)

    def get_data(self, response):
        object = json.loads(response.text)['object']
        json_d = object['returnlist']
        # print(json_d)
        for i in range(len(json_d)):
            name = json_d[i]['businessObjectName']
            time = json_d[i]['receiveTime']
            transactionname = json_d[i]['transactionPlatfName']
            industriestype = json_d[i]['industriesType']
            bulletinendtime = json_d[i]['bulletinEndTime']
            # print(name,time,transactionname,industriestype,bulletinendtime)
            dict = {'招标项目名称': name, '公告发布时间': time, '所属平台': transactionname, '所属专业': industriestype, '公告结束时间': bulletinendtime}
            self.big_list.append(dict)

    def save_data(self):
        with open('tc.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["招标项目名称", "公告发布时间", "所属平台", '所属专业', '公告结束时间'])
            writer.writeheader()
            writer.writerows(self.big_list)


if __name__ == '__main__':
    tc = Spider()
    page = int(input('请输入要爬去的页数：'))
    tc.get_response(page)
    tc.save_data()
