import json,html, cssselect
import requests
from retrying import retry
from datetime import datetime
from lxml.html import fromstring
from app import send,sendPic,sendg,sendPicg
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
'Accept': '*/*',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-CN,zh;q=0.9',
# 'Cookie':' _m_site_userid=42bcd76b-56db-4451-b36a-f1145ea2343e'
    }
def getsetu(keyword=None):
	if keyword!=None:
		setuurl = f'https://api.lolicon.app/setu/?r18=0&{keyword}&apikey=553636185ec7b7fadc60b7'
	else:
		setuurl = f'https://api.lolicon.app/setu/?r18=0&apikey=553636185ec7b7fadc60b7'
	r = requests.get(setuurl).json()
	picurl = r['data'][0]['url']
	title = r['data'][0]['title']
	author = r['data'][0]['author']
	tags = ''.join(r['data'][0]['tags'])
	print(tags,picurl)
	return title,author,tags,picurl

def getsetuR():
	setuurl = f'https://api.lolicon.app/setu/?r18=1&apikey=553636185ec7b7fadc60b7'
	r = requests.get(setuurl).json()
	picurl = r['data'][0]['url']
	title = r['data'][0]['title']
	author = r['data'][0]['author']
	tags = ''.join(r['data'][0]['tags'])
	print(tags,picurl)
	return title,author,tags,picurl

def random():
	if datetime.now().hour==23 and datetime.now().minute==1:
		sendPicg(1039758138,datetime.now(),'https://api.169740.com/api/rand.img5')

def weather(a):
	settings = read_settings()

	# 如果用户注册过，直接返回实时#天气

	city_name = member_in_list(settings,a.FromQQ)
	
	if city_name:
		current_weather_data = get_current_weather_data(settings['city_list'][city_name]['code'])
		send(a.FromQQ,format_msg(current_weather_data, settings['city_list'][city_name], current=True))
	
	# 如果没有注册过，自动进入注册流程
	else:
		send(a.FromQQ,'您还没有注册过推送地区\n请发送命令#注册（如：#注册 威远县）')
		#没有会话来get只能结束对话让对方发送新指令到下个函数
	return
	#还不能直接发地址需要指令进入，并用空格分开代入
def signup(a):
	# 如果搜索的地区别人已经注册过了，直接添加至该列表
	settings = read_settings()
	key_word = a.Content.split(' ')[1]
	if key_word in settings['city_list']:
		settings['city_list'][key_word]['members'].append([a.FromQQ, 6])
		update_settings(settings)
		send(a.FromQQ,f'“{key_word}”已经存在，已将您的推送地区设置为“{key_word}”\n修改时间请发送【更改时间】\n修改地区请发送【更改地区】')
		return
	search_results = get_search_results(key_word)
	if search_results == []:
		send(a.FromQQ,'没有查到任何结果，请发送“#天气”重新查询\n\n请确认您的输入为中文名，且仅为城市名，如：\n维多利亚(√)\n维多利亚哥伦比亚(×)\n维多利亚加拿大(×)')
		return
	# send(a.FromQQ,"回复序号例如（# 0)")
	with open('tempselction.json','w') as f:
		json.dump(search_results,f)
	format_str = format_results(search_results)
	send(a.FromQQ,"回复序号例如（# 0)\n"+format_str)
	return

def selection(a):
	settings = read_settings()
	selection = int(a.Content.split(' ')[1])
	with open('tempselction.json','r') as f:
		search_results = json.load(f)
	format_str = format_results(search_results)
	print('in selection ')
	# session.get('selection', prompt="回复序号确认地区", arg_filters=[extractors.extract_text, str.strip, validators.not_empty('输入不能为空'), validators.match_regex(r'\d', message='序号必须为数字', fullmatch=True), int])
	code = search_results[selection]['code']
	city = search_results[selection]
	settings['city_list'][city['local']] = {'code': code, 'local': city['local'], 'admin': city['admin'], 'country': city['country'], 'time_zone': 0, 'members': [[a.FromQQ, 7]]}
	update_settings(settings)
	send(a.FromQQ,f"已将您的天气推送地区设为：\n {format_str.splitlines()[selection]}\n天气会每天7点自动推送\n修改时间请发送【更改时间】\n修改地区请发送【更改地区】")

def location(a):
	settings = read_settings()
	for name, city in settings['city_list'].items():
		for member in city['members']:
			if a.FromQQ == member[0]:
				settings['city_list'][name]['members'].remove(member)
				update_settings(settings)
				send(a.FromQQ,f"已将您从“{name}”中移除，请发送【天气】重设地区")
				return
	send(a.FromQQ,f"您还没有注册过地区，请发送【天气】设置")

# def pushtime(a):
#     send(a.FromQQ,"现在开始更改时间") #bug：一来就finish
#     settings = read_settings()
#     for name, city in settings['city_list'].items():
#             for member in city['members']:
#                 if session.ctx['user_id'] == member[0]:
#                     session.state['name'] = name
#                     session.state['index'] = city['members'].index(member)
#                     send(a.FromQQ,"回复时间（0~23）")
					
#         session.finish(f"您还没有注册过地区，请发送【#注册】设置--modif")
#     settings['city_list'][session.state.get('name')]['members'][session.state.get('index')] = [session.ctx['user_id'], session.state.get('time')]
#     await update_settings(settings)
#     await session.send(f"已将您的推送时间设置为{session.state.get('time')}点")

def member_in_list(settings, user_id):
	"""检查QQ是否已经注册，并返回所在城市"""
	for city in settings['city_list']:
		for member in settings['city_list'][city]['members']:
			if member[0] == user_id:
				return city
	return False


def format_results(results):
	"""格式化打印搜索结果"""
	format_string = ''
	for i in range(len(results)):
		format_string += f"# {i} {results[i]['local']}（{results[i]['country']}，{results[i]['admin']}）\n"
	return format_string

# @nonebot.on_command('定时', shell_like=True)
# async def on_time(session):


def get_search_results(city):
	"""根据关键字，返回搜索结果"""
	url = 'https://m.weathercn.com/citysearchajax.do'
	r = requests.post(url,headers=headers, data={'q': city})
	results = json.loads(r.text)['listAccuCity']
	cities = []
	for city in results:
		new_city = {
			'code': city['key'], 
			'country': city['countryLocalizedName'], 
			'admin': city['administrativeAreaLocalizedName'], 
			'local': city['localizedName']
			}
		cities.append(new_city)
	return cities

def sendmorning():
	"""检查时间是否到点发送早安"""
	settings = read_settings()
	for city in settings['city_list'].keys():
		# settings['city_list'][city]['time_zone'] = await tz_calc(settings['city_list'][city]['code'])
		# await update_settings(settings)
		# print('test timer')
		for member in settings['city_list'][city]['members']:
			if datetime.now().hour==member[1] and datetime.now().minute==1:
				weather_data = get_weather_data(settings['city_list'][city]['code'])
				weather_str = format_msg(weather_data, settings['city_list'][city])
				send(member[0],weather_str)

def format_msg(w, city, current=False):
	"""格式化打印#天气数据处"""
	if current:
		current_time = datetime.now().strftime('%m/%d %X')
		weather_str = f"{city['local']}（{city['country']}）\n{current_time}\n\n" \
			f"天气：{w['current_weather']}\n气温：{w['current_temp']}\n体感温度：{w['current_feel']}\n" \
				f"日出/日落：{w['sunrise']} / {w['sunset']}\n修改时间请发送【更改时间】\n修改地区请发送【更改地区】"
	else:
		weather_str = f"早安！\n{city['local']}（{city['country']}）\n{w['date']}\n\n" \
			f"白天：{w['day_weather']}\n气温：{w['day_temp']}\n体感温度：{w['day_feel']}\n" \
				f"夜晚：{w['night_weather']}\n气温：{w['night_temp']}\n体感温度：{w['night_feel']}\n" \
					f"日出/日落：{w['sunrise']} / {w['sunset']}" 
	return weather_str


def read_settings():
	"""读取用户注册信息"""
	try:
		with open('settings.json', encoding='utf8') as f:
			settings = json.loads(f.read())
	except FileNotFoundError:
		settings = {"city_list": {}}
	return settings

@retry(stop_max_attempt_number=10)
def get_tree(url):
	r = requests.get(url,headers=headers)
	print(r)
	return fromstring(r.text)


def get_weather_data(location):
	"""爬取当天#天气"""
	url = f'https://m.weathercn.com/daily-weather-forecast.do?day=1&id={location}'
	tree = get_tree(url)
	date = tree.cssselect('section.date > div > ul > li')[0].text_content()
	weather = tree.cssselect('section.detail > section.weather > div.left > p')
	day_weather = weather[0].text_content()
	night_weather = weather[1].text_content()
	temp = tree.cssselect('ul.right li.top > p.left > strong')
	day_temp = temp[0].text_content()
	night_temp = temp[1].text_content()
	feel = tree.cssselect('ul.right li.top > p.right > strong')
	day_feel = feel[0].text_content()
	night_feel = feel[1].text_content()
	sunrise = tree.cssselect('section.cloud > p > strong')[0].text_content()
	sunset = tree.cssselect('section.cloud > p > strong')[1].text_content()

	weather_data = {
		'date': date,
		'day_weather': day_weather,
		'day_temp': day_temp,
		'day_feel': day_feel,
		'night_weather': night_weather,
		'night_temp': night_temp,
		'night_feel': night_feel,
		'sunrise': sunrise,
		'sunset': sunset
	}
	return weather_data


def get_current_weather_data(code):
	"""获取实时#天气"""
	url = f'https://m.weathercn.com/current-weather.do?id={code}'

	tree = get_tree(url)
	current_weather = tree.cssselect('a.head-right1 > p')[0].text_content().split()[0]
	current_temp = tree.cssselect('section.real_weather > section.weather > p ')[0].text_content()
	current_feel = tree.cssselect('ol.detail_01 li > p')[1].text_content()
	sun = tree.cssselect('section.sun_moon > p span')
	sunrise = sun[0].text_content()
	sunset = sun[1].text_content()

	current_weather_data = {
		'current_temp': current_temp,
		'current_feel': current_feel,
		'current_weather': current_weather,
		'sunrise': sunrise,
		'sunset': sunset
	}
	return current_weather_data

def update_settings(settings):
	"""更新注册信息"""
	with open('settings.json', 'w', encoding='utf-8') as f:
		f.write(json.dumps(settings, ensure_ascii=False, indent=4))







