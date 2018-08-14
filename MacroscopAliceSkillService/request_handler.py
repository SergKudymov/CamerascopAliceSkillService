from __future__ import unicode_literals

from MacroscopAliceSkillService.common import get_response_pattern, suggests_buttons
from MacroscopAliceSkillService.user import User
from urllib.request import urlopen
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


def create_new_user_response(request):
    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Здравствуйте! Я могу запустить ' \
                  'для Вас демо сервер или рассказать ' \
                  'о Камераскоп'

    response['response']['buttons'] = suggests_buttons

    return response


def create_default_response(request):
    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Вот что я умею:'
    response['response']['buttons'] = suggests_buttons

    return response


def create_best_soft_response(request):
    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Знают мамы, знают дети,\nМакроскоп самый лучший на свете!'

    return response


def create_about_response(request):
    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Камераскоп - помогает просматривать видео в формате mjpeg с вашего сервера Macroscop, \n' \
                  'а также получать информацию по камерам на нём.'

    return response


def create_joke_response(request):
    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Сергей, Илья и Андрей купили по даче. Сергей не поставил никакой сигнализации, \n' \
                  'Илья установил простенькую сигнализацию, ну а Андрей навороченную систему видеонаблюдения. \n' \
                  'Через месяц растащили дачу Сергея, дачу Ильи и дачу Андрея тоже, зато он смог всё это \n' \
                  'посмотреть. ха ха ха  '

    return response


def create_demo_response(request):
    output = urlopen("http://demo.macroscop.com/configex?login=root&password=").read()
    demo_server_config = output.decode('utf-8')
    response = create_channels_response(demo_server_config, request)

    return response


def create_channels_response(config, request, url='demo.macroscop.com', login='root', password=''):
    xml_doc = minidom.parseString(config)
    channels = xml_doc.getElementsByTagName('ChannelInfo')
    response = get_response_pattern(request)
    response['response']['text'] = 'Выберите камеру на демо сервере для просмотра видео:'
    cameras_buttons = []

    for channel in channels:
        channel_id = channel.attributes['Id'].value
        cameras_buttons.append({'title': channel.attributes['Name'].value,
                                'url': f'http://{url}/mobile?'
                                       f'channelId={channel_id}&'
                                       f'resolutionX=1024&'
                                       f'resolutionY=662&'
                                       f'fps=15&'
                                       f'login={login}&'
                                       f'password={password}&'
                                       f'is_ajax=true&'
                                       f'whoami=webclient&'
                                       f'withcontenttype=true',
                                'hide': False})

    response['response']['buttons'] = cameras_buttons

    return response


def create_enter_server_response(request):
    response = get_response_pattern(request)
    response['response']['text'] = 'Введите адрес сервера, логин и пароль в формате:\n' \
                                   '(ip адрес или доменное имя):(порт)%(логин)%(пароль)'

    return response


def create_test_response(request):
    response = get_response_pattern(request)
    response['response']['text'] = 'тест'
    response['response']['url'] = 'https://macroscop.com'

    return response


def create_error_response(request):
    response = get_response_pattern(request)
    response['response']['text'] = 'Упс, произошла внутренняя ошибка, обратитесь к Сергею!'

    return response


def handle_request(request):
    """Handle dialog and returns response"""

    try:
        user = UsersStorage().get_user(request)
        if user.is_new:
            user.is_new = False
            return create_new_user_response(request)

        self_server_login_words_pattern = ['%']
        if any(word in user.original_utterance.lower() for word in self_server_login_words_pattern):
            return user.login_to_server(request)

        demo_words_pattern = ['демо', 'дэмо', 'demo']
        if any(word in user.original_utterance.lower() for word in demo_words_pattern):
            return create_demo_response(request)

        self_server_words_pattern = ['зайти на свой сервер', 'свой сервер', 'сервер']
        if any(word in user.original_utterance.lower() for word in self_server_words_pattern):
            return create_enter_server_response(request)

        best_soft_words_pattern = ['самое лучшее', 'почему', 'самая лучшая']
        if any(word in user.original_utterance.lower() for word in best_soft_words_pattern):
            return create_best_soft_response(request)

        about_mc_words_pattern = ['camerascop', 'камераскоп', 'рассказывай', 'давай', 'трави']
        if any(word in user.original_utterance.lower() for word in about_mc_words_pattern):
            return create_about_response(request)

        about_mc_words_pattern = ['шутка про видео', 'анекдот про видео', 'жги']
        if any(word in user.original_utterance.lower() for word in about_mc_words_pattern):
            return create_joke_response(request)

        test_words_pattern = ['тест', 'тэст', 'test']
        if any(word in user.original_utterance.lower() for word in test_words_pattern):
            return create_test_response(request)

        alarm_words_pattern = ['тревога', 'аларм', 'аларма']
        if any(word in user.original_utterance.lower() for word in alarm_words_pattern):
            return user.create_alarm(request)
    except:
        return create_error_response(request)

    return create_default_response(request)
