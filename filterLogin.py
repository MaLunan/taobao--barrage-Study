import asyncio
from datetime import datetime
import json
import hashlib
from pyppeteer import launch
import requests

import tkinter
import base64
import sys
import requestFn
import logging
# 配置日志记录器，设置日志级别和输出文件
logging.basicConfig(filename='output.log', level=logging.INFO,encoding='utf-8')
# 公共时间戳
t=''
# cookeies
cookies=''
page=''
num=1
browser=''
# 直播间id
liveId=''
jsv='2.6.2'
appKey='12574478'
api='mtop.taobao.iliad.comment.query.anchorlatest'
preventFallback= 'true',
v= '2.0',
type= 'jsonp',
dataType= 'jsonp',
callback= 'mtopjsonp7' + str(num),
accountId=''
topic=''
# 动态时间戳
timestamps='' #普通用户
adminTimestamp='' #主播
# 动态评论id
commentId=''
adminCommentId=''
_m_h5_tk=''
updateTime=''
url = 'https://login.taobao.com/member/login.jhtml?sub=true&redirectURL=https%3A%2F%2Fliveplatform.taobao.com%2Frestful%2Findex%2Fhome%2Fdashboard' # 淘宝登录地址
historyData = []

async def main(Livesid,this,status):
    global directSeedingId
    directSeedingId=Livesid
    global browser
    global that
    global updateTime

    updateTime=int(datetime.now().timestamp())
    that=this
    loop = asyncio.get_event_loop()
    browser = await launch({
        'headless': False,
        'args': [
            '--start-maximized',
            '--disable-gpu',
            '--disable-infobars',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--enable-automation',
            '--no-sandbox',  
            '--disable-blink-features=AutomationControlled',  
        ],
        'executablePath' : r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        'dumpio': True,
        'ignoreHTTPSErrors':True,
       
    },
        loop=loop,
        handleSIGINT=False,  # 禁用 pyppeteer 设置信号处理程序
        handleSIGTERM=False,
        handleSIGHUP=False,)
    tk = tkinter.Tk()
    global width
    global height
    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()
    tk.quit()
    try :
        global page
        global historyData
        page = await browser.newPage()
        # await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36')
        await page.setExtraHTTPHeaders({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
        await page.goto(url)
        old_page = (await browser.pages())[0]
        await old_page.close()
        await page.setViewport({'width': width, 'height': height})
        await page.evaluate('''() => {
            window.moveTo(0, 0);
            window.resizeTo(window.screen.availWidth, window.screen.availHeight);
        }''')
        elements = await page.querySelectorAll('.iconfont.icon-qrcode')
        for element in elements:
            # 对每个匹配的元素执行特定操作
            # 例如，可以获取元素的文本内容或属性值
            await page.evaluate('(element) => element.click()', element)
        # await page.screenshot({'path': './headless-test-result.png'})  # 截图测试
        await page.waitForSelector('.qrcode-img', {'visible': True})
        
        while True:
            try:
                # 检查是否出现登录成功的标识，例如用户名或头像
                await page.waitForSelector('.ld-info-main', {'timeout': 5000})
                await asyncio.sleep(4)
                print('登录成功。。。')
                this.label.setText('登录成功...')   
                break  # 登录成功，跳出循环
            except:
                print('未登录成功，继续检查')
                if page.isClosed():
                    print('浏览器已关闭')
                    await browser.close()
                    sys.exit(0)
                pass  # 未登录成功，继续检查
            
        # 抓取 cookies
        await initCookies()
        tokens=await getToken()
        getLiveIds=await getLiveId()
        if getLiveIds==False:
            this.label.setText('未找到正在直播的直播间')   
            print('未找到正在直播的直播间')
            return
        this.label.setText('正在抓取中...')   
        await page.goto('https://liveplatform.taobao.com/restful/index/live/control?liveId='+liveId)
        # comments = page.querySelectorAll('//div[@class="alpw-comment-item"]')
       # history_comments = []
        await getTopic()
        while True:
            newUpdateTime=int(datetime.now().timestamp())
            if (newUpdateTime-updateTime)>=5400:
                updateTime=newUpdateTime
                await updatePage()
            # 捕捉弹幕元素方式
            elements22 = await page.querySelectorAll('.tc-comment-item')
            if elements22:
                paramsData = []
                try:
                    for element2 in elements22:
                        text = await page.evaluate('(element) => element.textContent', element2)
                        if text is not None:
                            print(text)
                            last_position = text.rfind(':')
                            if last_position == -1:
                                continue

                        comment_info = {
                            'userName': text[:last_position - 3],
                            'content': text[last_position + 3:],
                            'platformLiveId': liveId,
                            'platformType': 1,
                            'directSeedingId': directSeedingId
                        }
                        if comment_info in historyData:
                            continue
                        historyData.append(comment_info)
                        historyData = historyData[-100:]
                        paramsData.append(comment_info)
                    if len(paramsData) > 0 :
                        requestFn.addLivebullet(paramsData,'元素请求')
                except:
                    pass
            # 请求接口方式
            await getMessage()
            await getDataList('false',1)
            await getDataList('false',2)
            await asyncio.sleep(4)
    except Exception as e:
        if page.isClosed():
            print('浏览器已关闭')
            this.label.setText('浏览器已关闭...') 
            logging.info(f'浏览器已关闭{e}' )
            sys.exit(1)
        await updatePage()
    else:
        await browser.close()
async def updatePage():
    global page
    page = await browser.newPage()
    await page.goto('https://liveplatform.taobao.com/restful/index/live/control?liveId='+liveId,{'timeout': 60000})
    await page.setViewport({'width': width, 'height': height})
    await page.evaluate('''() => {
        window.moveTo(0, 0);
        window.resizeTo(window.screen.availWidth, window.screen.availHeight);
    }''')
    old_page = (await browser.pages())[0]
    await old_page.close()
    await asyncio.sleep(4)
#获取正在直播的id
async def getLiveId():
    await initCookies()
    tdate=str(int(datetime.now().timestamp() * 1000))
    data= json.dumps({"platform":"web","version":1,"api":"live"})
    signs=await sign(_m_h5_tk,tdate,data)
    # data= '%7B%22limit%22%3A200%2C%22topic%22%3A%22794e98b2-ef32-458d-9d8f-26dd5b157fff%22%2C%22tab%22%3A2%2C%22order%22%3A%22asc%22%2C%22paginationContext%22%3A%22%7B%5C%22commentId%5C%22%3A0%2C%5C%22refreshTime%5C%22%3A0%2C%5C%22timestamp%5C%22%3A0%7D%22%2C%22from%22%3A%22zhongkong%22%2C%22excludeTypes%22%3A%22%22%7D'
    url = "https://h5api.m.taobao.com/h5/mtop.taobao.tblive.portal.homepage.async.get/1.0/"
    params={
        'jsv':jsv,
        'appKey': appKey,
        't': tdate,
        'sign': signs,
        'api': 'mtop.taobao.tblive.portal.homepage.async.get',
        'v': '1.0',
        'preventFallback': preventFallback,
        'type': type,
        'dataType': dataType,
        'callback': callback,
        'data':data
    }
    response = session.get(url, params=params)
    response=str(response.content, 'utf-8') 
    start_index = response.index('(') + 1
    end_index = response.rindex(')')
    extracted_content = response[start_index:end_index]
    dataList=json.loads(extracted_content)
    dataList=dataList['data']['data'][0]['card']['data']['list']
    global liveId
    global browser
    isTrue='false'
    for item in dataList:
        if item['status']=='3':
            liveId=item['liveId']
            isTrue=True
    if isTrue=='false':
        browser.close()
        return False
    return True
#获取 topic
async def getTopic():
    await initCookies()
    tdate=str(int(datetime.now().timestamp() * 1000))
    data= json.dumps({"liveId":liveId})
    signs=await sign(_m_h5_tk,tdate,data)
    # data= '%7B%22limit%22%3A200%2C%22topic%22%3A%22794e98b2-ef32-458d-9d8f-26dd5b157fff%22%2C%22tab%22%3A2%2C%22order%22%3A%22asc%22%2C%22paginationContext%22%3A%22%7B%5C%22commentId%5C%22%3A0%2C%5C%22refreshTime%5C%22%3A0%2C%5C%22timestamp%5C%22%3A0%7D%22%2C%22from%22%3A%22zhongkong%22%2C%22excludeTypes%22%3A%22%22%7D'
    url = "https://h5api.m.taobao.com/h5/mtop.taobao.dreamweb.live.detail/2.0/"
    params={
        'jsv':jsv,
        'appKey': appKey,
        't': tdate,
        'sign': signs,
        'api': api,
        'v': v,
        'preventFallback': preventFallback,
        'type': type,
        'dataType': dataType,
        'callback': callback,
        'data':data
    }
    response = session.get(url, params=params)
    response=str(response.content, 'utf-8') 
    start_index = response.index('(') + 1
    end_index = response.rindex(')')
    extracted_content = response[start_index:end_index]
    dataList=json.loads(extracted_content)
    liveInfoDOString=json.loads(dataList['data']['liveInfoDOString'])
    global accountId
    global topic
    accountId=liveInfoDOString['accountId']
    topic=liveInfoDOString['topic']
    print(accountId,'accountId')
    print(topic,'topic')
    print(liveInfoDOString,'topic信息')
    await getDataList('true',1)
    await getDataList('true',2)
# 获取消息
async def getMessage():
    global historyData
    await initCookies()
    newdate=int(datetime.now().timestamp())
    tdate=str(newdate)
    oldDate=str(newdate-4)
    # global t
    url = f"https://impaas.alicdn.com/live/message/{topic}/{oldDate}/{tdate}"
    response = session.get(url)
    response=str(response.content, 'utf-8') 
    # start_index = response.index('(') + 1
    # end_index = response.rindex(')')
    # extracted_content = response[start_index:end_index]
    dataList=json.loads(response)['payloads']
    if len(dataList)==0:
        print('没有消息')
    else :
        paramsData=[]
        for item in dataList:
            objs=item
            decoded_string = base64.b64decode(item['data'])
            json_data = json.loads(decoded_string)
            objs['data']=json_data
            userName=objs['data']['publisherNick']
            content=objs['data']['content']
          #  liveBulletTime=objs['data']['timestamp']
            item_info = {
                'userName':userName,
                'content':content,
                'platformLiveId':liveId,
                'platformType':1,
                'directSeedingId':directSeedingId
                }
            if item_info in historyData:
                continue
            paramsData.append(item_info)
            historyData.append(item_info)
            historyData = historyData[-100:]
        if len(paramsData) > 0 :
            requestFn.addLivebullet(paramsData,'普通消息接口')
# 获取id
async def getId():
    await initCookies()
    num+1
    strNum=str(num)
    # global t
    newdate=int(datetime.now().timestamp() * 1000)
    tdate=str(newdate)
    oldDate=str(newdate-400000)
    data= json.dumps({"liveId":liveId,"types":"anchorWarning","startTime":oldDate,"endTime":tdate,"timeType":5,"searchType":"1","extParams":"{\"strategyDomain\":\"live-detail\"}"},separators=(',', ':'))
    signs=await sign(_m_h5_tk,tdate,data)
    jsonpIncPrefix= 'dc_lsad',
    callback= 'mtopjsonpdc_lsad'+strNum,
    # data= '%7B%22limit%22%3A200%2C%22topic%22%3A%22794e98b2-ef32-458d-9d8f-26dd5b157fff%22%2C%22tab%22%3A2%2C%22order%22%3A%22asc%22%2C%22paginationContext%22%3A%22%7B%5C%22commentId%5C%22%3A0%2C%5C%22refreshTime%5C%22%3A0%2C%5C%22timestamp%5C%22%3A0%7D%22%2C%22from%22%3A%22zhongkong%22%2C%22excludeTypes%22%3A%22%22%7D'
    url = "https://h5api.m.taobao.com/h5/mtop.taobao.iliad.live.user.assistant.data.get/1.0/"
    params={
        'jsv':jsv,
        'appKey': appKey,
        't': tdate,
        'sign': signs,
        'api': api,
        'v': v,
        'preventFallback': preventFallback,
        'type': type,
        'dataType': dataType,
        'callback': callback,
        'jsonpIncPrefix': jsonpIncPrefix,
        'data':data
    }
    response = session.get(url, params=params)
    response=str(response.content, 'utf-8') 
    start_index = response.index('(') + 1
    end_index = response.rindex(')')
    extracted_content = response[start_index:end_index]
    # dataList=json.loads(extracted_content)['data']['result']
# 获取弹幕
async def getDataList(all,tab):
    timestampErr=int(datetime.now().timestamp())
    dt_object = datetime.fromtimestamp(timestampErr)
    formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    try:
        await initCookies()
        global commentId
        global adminCommentId
        global timestamps
        global adminTimestamp
        global historyData
        num+1
        strNum=str(num)
        # global t
        tdate=int(datetime.now().timestamp())
        tdate=str(tdate*1000)
        timestampsStr=''
        commentIdStr=''
        if tab==1:
            commentIdStr=str(adminCommentId)
            timestampsStr=str(adminTimestamp)
        if tab==2:
            commentIdStr=str(commentId)
            timestampsStr=str(timestamps)
        # accountIds=str(accountId)
        data= json.dumps({"limit":200,"topic":topic,"tab":tab,"order":"asc","paginationContext":"{\"commentId\":"+commentIdStr+",\"refreshTime\":0,\"timestamp\":"+timestampsStr+"}","from":"zhongkong","excludeTypes":""},separators=(',', ':'))
        allData= json.dumps({"limit":200,"topic":topic,"tab":tab,"order":"asc","paginationContext":None,"from":"zhongkong","excludeTypes":""},separators=(',', ':'))
        if all=='true':
            data=allData
        print(_m_h5_tk,tdate,'_m_h5_tk,t')
        signs=await sign(_m_h5_tk,tdate,data)
        api='mtop.taobao.iliad.comment.query.anchorlatest',
        callback= 'mtopjsonp'+strNum,
        # data= '%7B%22limit%22%3A200%2C%22topic%22%3A%22794e98b2-ef32-458d-9d8f-26dd5b157fff%22%2C%22tab%22%3A2%2C%22order%22%3A%22asc%22%2C%22paginationContext%22%3A%22%7B%5C%22commentId%5C%22%3A0%2C%5C%22refreshTime%5C%22%3A0%2C%5C%22timestamp%5C%22%3A0%7D%22%2C%22from%22%3A%22zhongkong%22%2C%22excludeTypes%22%3A%22%22%7D'
        url = "https://h5api.m.taobao.com/h5/mtop.taobao.iliad.comment.query.anchorlatest/2.0/"
        params={
            'jsv':jsv,
            'appKey': appKey,
            't': tdate,
            'sign': signs,
            'api': api,
            'v': v,
            'preventFallback': preventFallback,
            'type': type,
            'dataType': dataType,
            'callback': callback,
            'data':data
        }
        response = session.get(url, params=params)
        response=str(response.content, 'utf-8') 
        start_index = response.index('(') + 1
        end_index = response.rindex(')')
        extracted_content = response[start_index:end_index]
        dataList=json.loads(extracted_content)['data']
        allList=[]
        paramsData=[]

        if 'comments' in dataList:
            allList=dataList['comments']
        if any(allList):
            for item in allList:
                userName=item['publisherNick']
                content=item['content']
                item_info = {
                    'userName': userName,
                    'content': content,
                    'platformLiveId': liveId,
                    'platformType': 1,
                    'directSeedingId': directSeedingId
                }
                if item_info in historyData:
                    continue
                paramsData.append(item_info)
                historyData.append(item_info)
                historyData = historyData[-100:]
            requestFn.addLivebullet(paramsData,'不稳定接口')
        if 'paginationContext' in dataList:
            paginationContext=json.loads(dataList['paginationContext'])
            if tab==1:
                adminCommentId=paginationContext['commentId']
                adminTimestamp=paginationContext['timestamp']
            if tab==2:
                commentId=paginationContext['commentId']
                timestamps=paginationContext['timestamp']
    except Exception as e:
        print(e,'异常')
        logging.info(f'adminCommentId:{adminCommentId}时间:{formatted_date}' )
        logging.info(f'adminTimestamp:{adminTimestamp}时间:{formatted_date}' )
        logging.info(f'commentId:{commentId}时间:{formatted_date}' )
        logging.info(f'timestamps:{timestamps}时间:{formatted_date}' )
        logging.info(f'allList:{allList}时间:{formatted_date}' )
        logging.info(f'dataList:{dataList}时间:{formatted_date}' )
        logging.info(f'错误信息：{e}extracted_content:{extracted_content}cookies:{cookies}时间:{formatted_date}')
        await updatePage()
    # return dataList
async def initCookies():
    global page
    global cookies
    cookies = await page.cookies()
    global session
    session = requests.session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    global _m_h5_tk
    for item in cookies:
        if item['name']=='_m_h5_tk':
            value=item['value']
            print(value,'没处理前mh5tk')
            if value:
                _m_h5_tk=value[:value.index("_")]
                print(_m_h5_tk,'m_h5_tk的值m_h5_tk的值m_h5_tk的值m_h5_tk的值m_h5_tk的值')
            break       
async def getToken():#获取token
    global t
    data=json.dumps({'appKey':'H5_25278248'},separators=(',', ':'))
    t=str(int(datetime.now().timestamp() * 1000))    
    signCode=await sign(_m_h5_tk,t,data)
    global cookies
    jsv='2.6.2'
    appKey= '12574478'
    api= 'mtop.taobao.dreamweb.anchor.h5token',
    v= '1.0',
    preventFallback= 'true',
    type= 'jsonp',
    dataType= 'jsonp',
    callback= 'mtopjsonp28',
    url = "https://h5api.m.taobao.com/h5/mtop.taobao.dreamweb.anchor.h5token/1.0"
    data={
        'jsv':jsv,
        'appKey': appKey,
        't': t,
        'sign': signCode,
        'api': api,
        'v': v,
        'preventFallback': preventFallback,
        'type': type,
        'dataType': dataType,
        'callback': callback,
        'data':data
    }
    response = session.post(url, data=data)
    response=str(response.content, 'utf-8') 
    start_index = response.index('(') + 1
    end_index = response.rindex(')')
    extracted_content = response[start_index:end_index]
    token=json.loads(extracted_content)['data']['result']
    return token

async def sign(token,t,data):
    print(t,'时间戳')
    key='12574478' 
    code=token+'&'+t+'&'+key+'&'+data
    md5 = hashlib.md5(code.encode("utf-8"))
    return md5.hexdigest()
async def initMain(directSeedingId,this,status):
    await main(directSeedingId,this,status)