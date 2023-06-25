import browser_cookie3
import requests
import configparser
import json

domain = 'bkkcpj.ucas.ac.cn'
website_cooke = browser_cookie3.edge(domain_name=domain)
cookie = website_cooke.__getattribute__('_cookies')
token = cookie[domain]['/']['Admin-Token']
auth = token.value
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

def get_term():
    url = 'https://bkkcpj.ucas.ac.cn/ea00031/findAllTerms'
    headers = {'Authorization': auth}
    all_terms_req = requests.get(url, cookies=website_cooke, headers=headers)
    terms_dict = json.loads(all_terms_req.text)
    all_terms = terms_dict['data']
    if(terms_dict['code'] != 200):
        print(f"get term info error with code: {str(terms_dict['code'])} and message: {terms_dict['message']}")
        exit(0)
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
        print("get course error with code: " + str(course_list['code']) +
                                " and message: " + course_list['message'])
        exit(0)
    course_list = course_list['data']
    id_dict_list = []
    for course in course_list:
        temp_dict = {'courseId': course['courseId'], 'pollId': course['pollId']}
        id_dict_list.append(temp_dict)
    return id_dict_list

def do_post_course_pull(course_id: int,poll_id:int):
    base_url = 'https://bkkcpj.ucas.ac.cn/myPoll/getById?id='
    headers = headers_post
    url = base_url + str(poll_id) + '&courseId=' + str(course_id)
    poll_req = requests.get(url, cookies=website_cooke, headers=headers)
    poll = json.loads(poll_req.text)
    poll = poll['data']
    poll['courseId'] = str(course_id)
    poll['totalScore'] = 100
    for index,question in enumerate(poll['questions']):
        if question['type'] == '1' or question['type'] == '4':
            poll['questions'][index]['answer'] = question['options2'][0]['value']
        elif question['type'] == '2':
            answer = [opt['value'] for opt in question['options2']]
            poll['questions'][index]['answers'] = answer[:3]
        elif question['type'] == '3':
            poll['questions'][index]['answer'] = defaultAnswer.get(question['seq']).get('answer')
        else:
            print('error question type : ' + question['type'])
            exit(0)
    post_data = json.dumps(poll)
    submit = requests.post('https://bkkcpj.ucas.ac.cn/myPoll/submit', cookies=website_cooke, headers=headers,data=post_data)
    if(submit.status_code != 200):
        print(f"post course {course_id} error with code: {str(submit.status_code)} and message: {submit.text}")
        exit(0)
    submit_statue = json.loads(submit.text)
    if(submit_statue['code'] != 200):
        print(f"post course {course_id} error with code: {str(submit_statue['code'])} and message: {submit_statue['message']}")
        exit(0)

def post_course_pull(id_dict_list:list):
    # for id_dict in id_dict_list:
    #     do_post_course_pull(id_dict['courseId'],id_dict['pollId'])
    id_dict = id_dict_list[-1]
    do_post_course_pull(id_dict['courseId'],id_dict['pollId'])

def course_pull():
    term_id = get_term()
    id_dict_list = get_course_list(term_id)
    post_course_pull(id_dict_list)
    print('finish')

if __name__ == "__main__":
    course_pull()
