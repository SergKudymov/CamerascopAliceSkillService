from __future__ import unicode_literals

from MacroscopAliceSkillService.user import User


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
        'text'] = 'Здравствуйте! Я могу запустить для Вас демо сервер или рассказать о Macroscop'

    suggests_buttons = [
        {'title': 'Demo', 'url': 'http://demo.macroscop.com', 'hide': False},
        {'title': 'Что такое Macroscop?', 'url': 'http://macroscop.com', 'hide': False}
        # {'title': 'Показать кадр с камеры', 'hide': True}
    ]
    response['response']['buttons'] = suggests_buttons

    return response


def create_default_response(request):
    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Я не поняла Вашу команду. Вот что я умею:'

    suggests_buttons = [
        {'title': 'Demo', 'url': 'http://demo.macroscop.com', 'hide': False},
        {'title': 'Что такое Macroscop?', 'url': 'http://macroscop.com', 'hide': False}
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
        'text'] = 'Макроскоп - программное обеспечение для систем видеонаблюдения, интеллектуальные модули и \n' \
                  'сетевые видеорегистраторы. С Макроскоп возможно построить систему от 1 до бесконечного числа \n' \
                  'любых ай пи камер. Программный комплекс легок в проектировании, внедрении, настройке и обслуживании. \n' \
                  'Приобретая софт для камер макроскоп, вы получаете возможность использования мобильных клиентов \n' \
                  'для ОС iOS, Android и WinPhone бесплатно. '

    return response


def create_joke_response(request):
    response = get_response_pattern(request)
    response['response'][
        'text'] = 'Сергей, Александр и Андрей купили по даче. Сергей не поставил никакой сигнализации, \n' \
                  'Александр установил простенькую сигнализацию, ну а Андрей навороченную систему видеонаблюдения. \n' \
                  'Через месяц растащили дачу Сергея, дачу Александра и дачу Андрея тоже, зато он смог всё это \n' \
                  'посмотреть. ха ха ха  '

    return response


def handle_request(request):
    """Handle dialog and returns response"""

    user = UsersStorage().get_user(request)

    if user.is_new:
        user.is_new = False
        return create_new_user_response(request)

    best_soft_words_pattern = ['самое лучшее', 'почему']
    if any(word in user.original_utterance.lower() for word in best_soft_words_pattern):
        return create_best_soft_response(request)

    about_mc_words_pattern = ['macroscop', 'макроскоп', 'рассказывай', 'давай', 'трави']
    if any(word in user.original_utterance.lower() for word in about_mc_words_pattern):
        return create_about_mc_response(request)

    about_mc_words_pattern = ['шутка про видео', 'анекдот про видео', 'жги']
    if any(word in user.original_utterance.lower() for word in about_mc_words_pattern):
        return create_joke_response(request)

    return create_default_response(request)
