"""Модуль с функцией main программы"""
import argparse

from vk_api import VkApi


def main():
    """Функция main

    Через ключ --user_id с помощью argparse вводится id пользователя.
    Создается объект класса VkApi и вызывается его метод get_user_friends,
    который возвращает DataFrame с информацией о друзьях пользователя
    """
    vk_api = VkApi()

    parser = argparse.ArgumentParser()
    parser.add_argument("--user_id", type=str, help="id пользователя", required=True)
    args = parser.parse_args()
    vk_api.get_user_friends(args.user_id)


if __name__ == '__main__':
    main()
