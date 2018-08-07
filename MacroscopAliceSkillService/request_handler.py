from __future__ import unicode_literals

from MacroscopAliceSkillService.user import User
import urllib.request
from xml.dom import minidom


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class UsersStorage(metaclass=Singleton):
    def __init__(self):
        self.users = {}

    def get_user(self, request):
        user_id = request['session']['user_id']
        original_utterance = request['request']['original_utterance']

        if user_id in self.users:
            self.users[user_id].original_utterance = original_utterance
            return self.users[user_id]
        else:
            new_user = User(user_id, original_utterance)
            self.users[user_id] = new_user
            return new_user


def get_response_pattern(request):
    response_pattern = {
        "version": request['version'],
        "session": request['session'],
        "response": {
            "end_session": False
        }
    }
    return response_pattern


def create_new_user_response(request):
    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Здравствуйте! Я могу запустить для Вас демо сервер или рассказать о Камераскоп'

    suggests_buttons = [
        {'title': 'Demo сервер', 'hide': False},
        {'title': 'Зайти на свой сервер', 'hide': False},
        {'title': 'Что такое Камераскоп?', 'hide': False}
        # {'title': 'Показать кадр с камеры', 'hide': True}
    ]
    response['response']['buttons'] = suggests_buttons

    return response


def create_default_response(request):
    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Вот что я умею:'

    suggests_buttons = [
        {'title': 'Demo server', 'hide': False},
        {'title': 'Что такое Camerascop?', 'hide': False}
        # {'title': 'Показать кадр с камеры', 'hide': True}
    ]
    response['response']['buttons'] = suggests_buttons

    return response


def create_best_soft_response(request):
    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Знают мамы, знают дети,\nМакроскоп самый лучший на свете!'

    return response


def create_about_mc_response(request):
    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Камераскоп - помогает просматривать видео в формате mjpeg с вашего сервера Macroscop, \n' \
                  'а также получать информацию по камерам на нём.'

    return response


def create_joke_response(request):
    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Сергей, Александр и Андрей купили по даче. Сергей не поставил никакой сигнализации, \n' \
                  'Александр установил простенькую сигнализацию, ну а Андрей навороченную систему видеонаблюдения. \n' \
                  'Через месяц растащили дачу Сергея, дачу Александра и дачу Андрея тоже, зато он смог всё это \n' \
                  'посмотреть. ха ха ха  '

    return response


def create_demo_response(request):
    output = urllib.request.urlopen("http://demo.macroscop.com/configex?login=root&password=").read()
    response = output.decode('utf-8')
    xml_doc = minidom.parseString(response)
    channels = xml_doc.getElementsByTagName('ChannelInfo')

    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Вот список камер:'
    suggests_buttons = []

    for channel in channels:
        channel_id = channel.attributes['Id'].value
        suggests_buttons.append({'title': channel.attributes['Name'].value, 'url': f'http://demo.macroscop.com/mobile?channelId={channel_id}&resolutionX=1024&resolutionY=662&fps=15&login=root&password=&is_ajax=true&whoami=webclient&withcontenttype=true', 'hide': False})

    response['response']['buttons'] = suggests_buttons

    return response

def handle_request(request):
    """Handle dialog and returns response"""

    user = UsersStorage().get_user(request)

    if user.is_new:
        user.is_new = False
        return create_new_user_response(request)

    demo_words_pattern = ['демо', 'дэмо', 'demo']
    if any(word in user.original_utterance.lower() for word in demo_words_pattern):
        return create_demo_response(request)

    best_soft_words_pattern = ['самое лучшее', 'почему']
    if any(word in user.original_utterance.lower() for word in best_soft_words_pattern):
        return create_best_soft_response(request)

    about_mc_words_pattern = ['camerascop', 'камераскоп', 'рассказывай', 'давай', 'трави']
    if any(word in user.original_utterance.lower() for word in about_mc_words_pattern):
        return create_about_mc_response(request)

    about_mc_words_pattern = ['шутка про видео', 'анекдот про видео', 'жги']
    if any(word in user.original_utterance.lower() for word in about_mc_words_pattern):
        return create_joke_response(request)

    return create_default_response(request)
