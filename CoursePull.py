import browser_cookie3
import requests
import configparser
import json

domain = 'bkkcpj.ucas.ac.cn'
# 从本地获取cookie
try:
    website_cooke = browser_cookie3.load(domain_name=domain)
except Exception as e:
    try:
        website_cooke = browser_cookie3.edge(domain_name=domain)
    except Exception as e:
        raise e
cookie = website_cooke.__getattribute__('_cookies')
#从cookie解析出Admin-Token, 用于header中的Authorization字段
try:
    token = cookie[domain]['/']['Admin-Token']
except KeyError:
    raise Exception(f"获取cookie失败，请先登陆课程评价网站以刷新cookie")
auth = token.value
#构造headers
headers = {'Authorization': token.value}
headers_post = {
    'Authorization': token.value,
    'Content-Type': 'application/json'
    }

def load_config(config_file_path:str):
    '''
        读取配置文件
    '''
    config = configparser.ConfigParser()
    config.read(config_file_path,encoding='utf-8')
    sections = config.sections()
    config_dict = dict((section,dict(config.items(section))) for section in sections)
    return config_dict

defaultAnswer = load_config('defaultAnswer.ini')
default_choice_single = 0
default_choice_multiple_start = 0
default_choice_multiple_end = 3
MAX_MULTIPLE_AMOUNT = 17
default_choice = defaultAnswer.get('defaultChoiceOption',{})
if len(default_choice) >0:
    default_choice_single = min(int(default_choice.get('single',0)),4)
    default_choice_multiple_start = min(int(default_choice.get('multipleStart',0)),MAX_MULTIPLE_AMOUNT)
    default_choice_multiple_end = min(int(default_choice.get('multipleAmount',3)),
                                        MAX_MULTIPLE_AMOUNT-default_choice_multiple_start)
    default_choice_multiple_end += default_choice_multiple_start

def get_term():
    url = 'https://bkkcpj.ucas.ac.cn/ea00031/findAllTerms'
    headers = {'Authorization': auth}
    all_terms_req = requests.get(url, cookies=website_cooke, headers=headers)
    terms_dict = json.loads(all_terms_req.text)
    all_terms = terms_dict['data']
    if(terms_dict['code'] == 4000):
        raise Exception("Cookie 已过期，请重新登陆课程评价网站以刷新cookie")
    elif(terms_dict['code'] != 200):
        raise Exception(f"get term info error with code: {str(terms_dict['code'])} and message: {terms_dict['message']}")

    id = 0
    for term in all_terms:
        if(term["isXk"]=='Y'):
            id = term["id"]
            break
    return id

def get_course_list(term_id:int):
    url = 'https://bkkcpj.ucas.ac.cn/myCourse/list?title=&pollTypeId=&termId=' + str(term_id) + '&page=1&size=100'
    headers = {'Authorization': auth}
    course_list_req = requests.get(url, cookies=website_cooke, headers=headers)
    course_list = json.loads(course_list_req.text)
    if(course_list['code'] != 200):
        raise Exception(f"get course error with code: {str(course_list['code'])} and message: {course_list['message']}" )
    
    course_list = course_list['data']
    id_dict_list = []
    for course in course_list:
        temp_dict = {'courseId': course['courseId'], 'pollId': course['pollId']}
        id_dict_list.append(temp_dict)
    return id_dict_list

def do_post_course_pull(course_id: int,poll_id:int):
    '''
        提交课程评价
        return :bool 是否进行了提交
    '''
    do_post :bool = True
    base_url = 'https://bkkcpj.ucas.ac.cn/myPoll/getById?id='
    headers = headers_post
    url = base_url + str(poll_id) + '&courseId=' + str(course_id)
    poll_req = requests.get(url, cookies=website_cooke, headers=headers)
    poll = json.loads(poll_req.text)
    poll = poll['data']
    poll['courseId'] = str(course_id)
    poll['totalScore'] = 100
    for index,question in enumerate(poll['questions']):
        # 如果已经填写过了，就跳过，并且不发送post请求
        if question['answer'] != None or question['answers'] != None:
            do_post = False
            break
        # type=1是文字单选，type=4是数字单选
        if question['type'] == '1' or question['type'] == '4':
            poll['questions'][index]['answer'] = question['options2'][default_choice_single]['value']
        # type=2是文字多选
        elif question['type'] == '2':
            answer = [opt['value'] for opt in question['options2']]
            poll['questions'][index]['answers'] = answer[default_choice_multiple_start:default_choice_multiple_end]
        # type=3是文字简答
        elif question['type'] == '3':
            poll['questions'][index]['answer'] = defaultAnswer.get(question['seq'],'default').get('answer')
        else:
            raise ValueError('error question type : ' + question['type'])
    
    if do_post:
        post_data = json.dumps(poll)
        submit = requests.post('https://bkkcpj.ucas.ac.cn/myPoll/submit', cookies=website_cooke, headers=headers,data=post_data)
        if(submit.status_code != 200):
            raise Exception(f"post course {course_id} error with code: {str(submit.status_code)} and message: {submit.text}")
        submit_statue = json.loads(submit.text)
        if(submit_statue['code'] != 200):
            raise Exception(f"post course {course_id} error with code: {str(submit_statue['code'])} and message: {submit_statue['message']}")
    
    return do_post

def post_course_pull(id_dict_list:list):
    '''
        对课程列表中的所有课程提交评价
        - return :tuple (total,counter) total:总数 counter:提交数
    '''
    counter = 0
    total = len(id_dict_list)
    for id_dict in id_dict_list:
        if(do_post_course_pull(id_dict['courseId'],id_dict['pollId'])):
            counter += 1
    return total,counter

def course_pull():
    term_id = get_term()
    id_dict_list = get_course_list(term_id)
    post_course_pull(id_dict_list)
    print('finish')

if __name__ == "__main__":
    course_pull()
