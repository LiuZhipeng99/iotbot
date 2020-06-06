import socketio
import json
import requests
import socket
import time
import logging
# import pdb
import getpicurl
sio = socketio.Client()
webapi = 'http://127.0.0.1:8888' #"http://121.36.6.132:2233"
robotqq = '2810072376' #第一个bug大概是这个没用字符串
# Global R18 = 0

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',level=0,filename='new.log',filemode='a')
class GMess:
	#QQ群消息类型
	def __init__(self,message1):
		#print(message1)
		self.FromQQG = message1['FromGroupId'] #来源QQ群
		self.QQGName = message1['FromGroupName'] #来源QQ群昵称
		self.FromQQ = message1['FromUserId'] #来源QQ
		self.FromQQName = message1['FromNickName'] #来源QQ名称
		self.Content = message1['Content'] #消息内容
class Mess:
	def __init__(self,message1):
		self.FromQQ = message1['FromUin']
		self.ToQQ = message1['ToUin']
		self.Content = message1['Content']
#把bug找到，群发参数sendtype为2固定了，发消息的四个函数（图文）
def sendg(ToQQ,Content,sendToType=1,atuser=0,sendMsgType='TextMsg',groupid=0):
	send(ToQQ,Content,sendToType=2,atuser=0,sendMsgType='TextMsg',groupid=0)
def sendPicg(ToQQ,Content,imageUrl,sendToType=1):
	sendPic(ToQQ,Content,imageUrl,sendToType=2)
def send(ToQQ,Content,sendToType=1,atuser=0,sendMsgType='TextMsg',groupid=0):
	tmp={}
	tmp['sendToType'] = sendToType
	tmp['toUser']= ToQQ
	tmp['sendMsgType']=sendMsgType
	tmp['content']=Content
	tmp['groupid']=0
	tmp['atUser']=atuser
	tmp1 = json.dumps(tmp)
	requests.post(webapi+'/v1/LuaApiCaller?funcname=SendMsg&qq='+robotqq,data=tmp1)
def sendPic(ToQQ,Content,imageUrl,sendToType=1):
	tmp={}
	tmp['sendToType'] = sendToType
	tmp['toUser']= ToQQ
	tmp['sendMsgType']="PicMsg"
	tmp['content']=Content
	tmp['picBase64Buf']=''
	tmp['fileMd5']=''
	tmp['picUrl']=imageUrl
	tmp1 = json.dumps(tmp)
	#print(tmp1)
	print(requests.post(webapi+'/v1/LuaApiCaller?funcname=SendMsg&timeout=10&qq='+robotqq,data=tmp1).text)
 

# standard Python
 
# SocketIO Client
#sio = socketio.AsyncClient(logger=True, engineio_logger=True)
 
# ----------------------------------------------------- 
# Socketio
# ----------------------------------------------------- 
def beat():
	while(1):
		sio.emit('GetWebConn',robotqq)
		time.sleep(60)
		getpicurl.random()
		getpicurl.sendmorning()
 
@sio.event
def connect():
	print('connected to server')
	sio.emit('GetWebConn',robotqq)#取得当前已经登录的QQ链接
	beat() #心跳包，保持对服务器的连接
 
@sio.on('OnGroupMsgs')
def OnGroupMsgs(message):
	''' 监听群组消息'''
	tmp3 = message['CurrentPacket']['Data']
	a = GMess(tmp3)
	cm = a.Content.split(' ',3) #分割命令
	'''
	a.FrQQ 消息来源
	a.QQGName 来源QQ群昵称
	a.FromQQG 来源QQ群
	a.FromNickName 来源QQ昵称
	a.Content 消息内容
	'''
	print('get group')
	if a.Content=='#list':
		sendg(a.FromQQG,"目前可用功能：\n#来份涩图\n#R18\n#口吐莲花\n#祖安语录\n#彩虹屁\n#随机图片\n#搜图 [keword]")
	if a.Content=='#R18':
		sendg(a.FromQQG,'R18模式')
		title,author,tags,picurl = getpicurl.getsetuR()
		sendPicg(a.FromQQG,title+'\n'+author+"\n"+tags,picurl)
		return
	if a.Content=='#来份涩图':
		#print(a.ToQQ)
		sendg(a.FromQQG,"loading...(P站资源 速度不稳定)")
		title,author,tags,picurl = getpicurl.getsetu()
		sendPicg(a.FromQQG,title+'\n'+author+"\n"+tags,picurl)
		return

	if a.Content=='#口吐莲花':
		sendg(a.FromQQG,requests.get('https://nmsl.shadiao.app/api.php?level=min&lang=zh_cn').text)
		return
	if a.Content=='#祖安语录':
		sendg(a.FromQQG,requests.get('https://nmsl.shadiao.app/api.php?lang=zh_cn').text)
		return
	if a.Content=='#彩虹屁':
		sendg(a.FromQQG,requests.get('https://chp.shadiao.app/api.php').text)
		return
	if cm[0]=='#搜图'and cm[1]!=None:
		sendg(a.FromQQG,"loading...(P站资源 速度不稳定)")
		title,author,tags,picurl = getpicurl.getsetu(cm[1])
		sendPicg(a.FromQQG,title+'\n'+author+"\n"+tags,picurl)
	if a.Content=='#随机图片':
		sendPicg(a.FromQQG,'',requests.get('http://api.mtyqx.cn/tapi/random.php',allow_redirects=False).headers['location'])
		sendPicg(a.FromQQG,'','https://api.169740.com/api/rand.img5')
		return



	# te = re.search(r'\#(.*)',str(a.Content))
	# if te == None:
	# 	return
	# temp = eval(requests.get("https://hlqsc.cn/lexicon/?id="+str(a.FromQQ)+"&msg="+te.group(1)+"&name=tuling").text)
	# sendtext = re.sub(r"http.*", "", temp['text'], count=0, flags=0)
	# send(a.FromQQG,sendtext,2,a.FromQQ)
	'''
	图灵接口 已丢弃
	如果你有图灵api可以直接使用
	data_temp = {}
	chat_temp = {}
	user = {}
	user['apiKey'] = '587f10e38dac47bd9abbaa7cfcf3dc64'
	user['userId'] = str(a.FromQQ)
	te = re.search(r'\#(.*)',str(a.Content))
	if te == None:
		return
	chat_temp['inputText'] = {'text':te.group(1)}
	data_temp['perception'] = chat_temp
	data_temp['userInfo'] = user
	json_temp = json.dumps(data_temp)
	print(json_temp)
	temp =eval(requests.post('http://openapi.tuling123.com/openapi/api/v2',data=json_temp).text)
	temp1 = temp['results']
	text = ''
	for i in temp1:
		if i['resultType'] == 'text':
			text+= i['values']['text']
	send(a.FromQQG,text,2,a.FromQQ)
	'''
	logging.info("["+str(a.FromQQG)+']'+str(a.FromQQ)+": "+str(a.Content))
	#print(message)
 
@sio.on('OnFriendMsgs')
def OnFriendMsgs(message):
	''' 监听好友消息 '''#接口是指令把函数写进其他文件
	tmp3 = message['CurrentPacket']['Data']
	a = Mess(tmp3)
	cm = a.Content.split(' ')
	if a.Content=='#list':
		send(a.FromQQ,"目前可用功能：\n点歌（点歌好运来）\n搜书（搜书 书名）\n口吐莲花\n祖安语录\n彩虹屁\n舔狗日记\n随机图片\n天气")
		return
	if a.Content=='舔狗日记':
		send(a.FromQQ,requests.get('https://www.somekey.cn/tiangou/random.php').json()['data']['content'])
		return
	if cm[0]=='天气':
		getpicurl.weather(a)
		return
	if cm[0]=='#注册' and cm[1]!=None:
		getpicurl.signup(a)
		return
	if cm[0]=='#' and cm[1]!=None:
		getpicurl.selection(a)
		return
	# if cm[0]=='更改时间':
	# 	getpicurl.pushtime(a)
	if cm[0]=='更改地区':
		getpicurl.location(a)
		return
	if cm[0]=='更改时间':
		send(a.FromQQ,'此功能暂维护，请联系admin更改')
	if cm[0]=='test':
		send(a.FromQQ,'test1')
		send(a.FromQQ,'test2')
		return
	if a.Content=='口吐莲花':
		send(a.FromQQ,requests.get('https://nmsl.shadiao.app/api.php?level=min&lang=zh_cn').text)
		return
	if a.Content=='祖安语录':
		send(a.FromQQ,requests.get('https://nmsl.shadiao.app/api.php?lang=zh_cn').text)
		return
	if a.Content=='彩虹屁':
		send(a.FromQQ,requests.get('https://chp.shadiao.app/api.php').text)
		return


@sio.on('OnEvents')
def OnEvents(message):
	''' 监听相关事件'''
	print(message)   
# ----------------------------------------------------- 
def main():
	try:

		sio.connect(webapi,transports=['websocket'])
		#pdb.set_trace() 这是断点
		print('已连上')
		sio.wait()
	except BaseException as e:
		logging.info(e)
		print (e)
 
if __name__ == '__main__':
	# setuurl = 'https://api.lolicon.app/setu/?r18=1&apikey=553636185ec7b7fadc60b7'
	# r = requests.get(setuurl).json()
	# picurl = r['data'][0]['url']
	# title = r['data'][0]['title']
	# author = r['data'][0]['author']
	# tags = ''.join(r['data'][0]['tags'])
	# sendPic(1695949332,title+'\n'+author+"\n"+tags,2,picurl)
	# send(1695949332,"loading...",1)
	# sendPic(1695949332,title+'\n'+author+"\n"+tags,2,picurl)
	main()

