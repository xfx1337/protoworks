import telebot
import db
import replies
import json

import os
import utils

from network_manager.network_manager import NetworkManager
net_manager = NetworkManager()
net_manager.login()

import services.server
import services.users

db.create_database()

bot = telebot.TeleBot("YOUR TOKEN THERE")
VOICE_PLAYBACK_SERVER = "http://ayaconference.ru:5358"
#VOICE_PLAYBACK_SERVER = "http://127.0.0.1:2358"

admin_markup = telebot.types.ReplyKeyboardMarkup(True, False)
admin_markup.row("Состояние сервера", "Состояние LAN")
admin_markup.row("Действия(Сервер)", "Действия(LAN)")
admin_markup.row("Действия(Панель)", "Действия(Цех)")
admin_markup.row("Пользователи Панель", "Пользователи ProtoWorks")
admin_markup.row("Другое")

users_actions_markup = telebot.types.ReplyKeyboardMarkup(True, False)
users_actions_markup.row("Добавить", "Удалить")
users_actions_markup.row("Админ панель")

actions_server_markup = telebot.types.ReplyKeyboardMarkup(True, False)
actions_server_markup.row("Проекты", "Станки")
actions_server_markup.row("Перезагрузка сервера", "Action Manager")
actions_server_markup.row("Данные для входа на сервера")
actions_server_markup.row("Админ панель")

projects_markup = telebot.types.ReplyKeyboardMarkup(True, False)
projects_markup.row("Информация", "Пометить сданным")
projects_markup.row("Аудит", "Админ панель")

only_admin_button_markup = telebot.types.ReplyKeyboardMarkup(True, False)
only_admin_button_markup.row("Админ панель")

are_you_sure_markup = telebot.types.ReplyKeyboardMarkup(True, False)
are_you_sure_markup.row("Да", "Нет")
are_you_sure_markup.row("Админ Панель")

logs_get_action_markup = telebot.types.ReplyKeyboardMarkup(True, False)
logs_get_action_markup.row("Перезаписать")
logs_get_action_markup.row("Админ панель")

actions_factory_markup = telebot.types.ReplyKeyboardMarkup(True, False)
actions_factory_markup.row("Печать на бумаге", "Отправить голосовое")
actions_factory_markup.row("Камера", "Получить фото")
actions_factory_markup.row("Админ панель")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row("Админ Панель")
    msg = bot.send_message(message.chat.id, replies.START, reply_markup=user_markup)
    bot.register_next_step_handler(msg, open_admin_panel)

@bot.message_handler(func=lambda call: True)
def message_all(message):
    admin_menu_accept_action(message)
        

def open_admin_panel(message):
    if not db.check_admin(message):
        bot.send_message(message.chat.id, "Нет прав доступа.")
    else:
        if message.text.lower() == "админ панель":
            msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
            bot.register_next_step_handler(msg, admin_menu_accept_action)

def admin_menu_accept_action(message):
    if not db.check_admin(message):
        bot.send_message(message.chat.id, "Нет прав доступа.")
        return
    
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)

    if message.text.lower() == "состояние сервера":
        try:
            out = services.server.get_status()
            msg = bot.send_message(message.chat.id, out, reply_markup=admin_markup)
            bot.register_next_step_handler(msg, admin_menu_accept_action)
        except:
            msg = bot.send_message(message.chat.id, "Сервер недоступен", reply_markup=admin_markup)
            bot.register_next_step_handler(msg, admin_menu_accept_action)

    if message.text.lower() == "состояние lan":
        bot.send_message(message.chat.id, "Это можно занять некоторое время.")
        out = services.server.get_lan_clients()
        msg = bot.send_message(message.chat.id, out, reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)

    if message.text.lower() == "пользователи панель":
        users_list_str = services.users.get_users_list_str()
        bot.send_message(message.chat.id, users_list_str)
        msg = bot.send_message(message.chat.id, "Выберите действие", reply_markup=users_actions_markup)
        bot.register_next_step_handler(msg, users_menu_accept_action)

    if message.text.lower() == "пользователи protoworks":
        users_list_str = services.server.get_users_list_str()
        bot.send_message(message.chat.id, users_list_str)
        msg = bot.send_message(message.chat.id, "Выберите действие", reply_markup=users_actions_markup)
        bot.register_next_step_handler(msg, users_protoworks_menu_accept_action)

    if message.text.lower() == "действия(сервер)":
        msg = bot.send_message(message.chat.id, 'Меню "Действия(Сервер) открыто"', reply_markup=actions_server_markup)
        bot.register_next_step_handler(msg, actions_server_menu)

    if message.text.lower() == "действия(панель)":
        msg = bot.send_message(message.chat.id, "Не реализовано. Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)

    if message.text.lower() == "действия(цех)":
        msg = bot.send_message(message.chat.id, 'Меню "Действия(Цех) открыто"', reply_markup=actions_factory_markup)
        bot.register_next_step_handler(msg, actions_factory_menu)

def users_menu_accept_action(message):
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)

    if message.text.lower() == "добавить":
        msg = bot.send_message(message.chat.id, "Укажите username человека в Telegram без @ (пример: xfx1337)")
        bot.register_next_step_handler(msg, users_menu_add)

    if message.text.lower() == "удалить":
        msg = bot.send_message(message.chat.id, "Укажите username человека в Telegram без @ (пример: xfx1337)")
        bot.register_next_step_handler(msg, users_menu_delete)

def users_menu_add(message):
    username = message.text
    try:
        db.add_user(username)
        msg = bot.send_message(message.chat.id, "Пользователь добавлен", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
    except:
        msg = bot.send_message(message.chat.id, "Не удалось", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)

def users_menu_delete(message):
    username = message.text
    try:
        db.delete_user(username)
        msg = bot.send_message(message.chat.id, "Пользователь удален", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
    except:
        msg = bot.send_message(message.chat.id, "Ошибка. Пользователь не является администратором", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)

def users_protoworks_menu_accept_action(message):
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)

    if message.text.lower() == "добавить":
        msg = bot.send_message(message.chat.id, "Укажите username")
        bot.register_next_step_handler(msg, users_protoworks_ask_password)

    if message.text.lower() == "удалить":
        msg = bot.send_message(message.chat.id, "Укажите username")
        bot.register_next_step_handler(msg, users_protoworks_menu_delete)

def users_protoworks_ask_password(message):
    username = message.text
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
    msg = bot.send_message(message.chat.id, "Укажите пароль")
    bot.register_next_step_handler(msg, users_protoworks_add_user, username)

def users_protoworks_add_user(message, username):
    password = message.text
    services.server.register_user(username, password)
    msg = bot.send_message(message.chat.id, "Запрос отправлен", reply_markup=admin_markup)
    bot.register_next_step_handler(msg, admin_menu_accept_action)

def users_protoworks_menu_delete(message):
    username = message.text
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return
    try:
        services.server.remove_user(username)
        msg = bot.send_message(message.chat.id, "Запрос отправлен", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
    except:
        msg = bot.send_message(message.chat.id, "Не удалось", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)


def actions_server_menu(message):
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return

    if message.text.lower() == "проекты":
        projects_str = services.server.get_projects_str()
        msg = bot.send_message(message.chat.id, projects_str, reply_markup=projects_markup)
        bot.register_next_step_handler(msg, projects_menu_accept_action)

    if message.text.lower() == "перезагрузка сервера":
        msg = bot.send_message(message.chat.id, "Вы уверены?", reply_markup=are_you_sure_markup)
        bot.register_next_step_handler(msg, restart_server_sure)

    if message.text.lower() == "станки":
        bot.send_message(message.chat.id, "Это может занять некоторое время")
        machines_str = services.server.get_machines_str()
        msg = bot.send_message(message.chat.id, machines_str, reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)

    if message.text.lower() == "action manager":
        example = '{"action": "NEXT_JOB", "devices": ["MACHINE1"]}'
        msg = bot.send_message(message.chat.id, f"Введите действие в формате как в примере: \n{example}", reply_markup=only_admin_button_markup)
        bot.register_next_step_handler(msg, action_manager_get_action)

    if message.text.lower() == "данные для входа на сервера":
        msg = bot.send_message(message.chat.id, "Данные: \n" + db.get_logs(), reply_markup=logs_get_action_markup)
        bot.register_next_step_handler(msg, logs_get_action)

def projects_menu_accept_action(message):
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
    
    if message.text.lower() == "информация":
        msg = bot.send_message(message.chat.id, "Напишите ID проекта", reply_markup=only_admin_button_markup)
        bot.register_next_step_handler(msg, projects_menu_accept_info_id)

    if message.text.lower() == "пометить сданным":
        msg = bot.send_message(message.chat.id, "Напишите ID проекта", reply_markup=only_admin_button_markup)
        bot.register_next_step_handler(msg, projects_menu_accept_done_id)

    if message.text.lower() == "аудит":
        msg = bot.send_message(message.chat.id, "Напишите ID проекта", reply_markup=only_admin_button_markup)
        bot.register_next_step_handler(msg, projects_menu_accept_audit_id)

def projects_menu_accept_info_id(message):
    id = message.text
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return

    try:
        out = services.server.get_project_info_str(int(id))
    except:
        msg = bot.send_message(message.chat.id, "Не найден", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return
    msg = bot.send_message(message.chat.id, out, reply_markup=admin_markup)
    bot.register_next_step_handler(msg, admin_menu_accept_action)

def projects_menu_accept_done_id(message):
    id = message.text
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return

    try:
        out = services.server.make_project_done(int(id))
    except:
        msg = bot.send_message(message.chat.id, "Не найден", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return
    msg = bot.send_message(message.chat.id, "Сдан", reply_markup=admin_markup)
    bot.register_next_step_handler(msg, admin_menu_accept_action)

def projects_menu_accept_audit_id(message):
    id = message.text
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return

    try:
        out = services.server.get_project_audit_str(int(id))
    except:
        msg = bot.send_message(message.chat.id, "Не найден", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return
    msg = bot.send_message(message.chat.id, out, reply_markup=admin_markup)
    bot.register_next_step_handler(msg, admin_menu_accept_action)

def restart_server_sure(message):
    if message.text.lower() == "да":
        services.server.restart_server()
        msg = bot.send_message(message.chat.id, "Запрос отправлен.", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
    else:
        msg = bot.send_message(message.chat.id, "Отмена.", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)

def action_manager_get_action(message):
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return

    try:
        action = json.loads(message.text)
    except:
        msg = bot.send_message(message.chat.id, "Invalid syntax.", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return
    try:
        services.server.send_action(action)
    except:
        pass
    msg = bot.send_message(message.chat.id, "Отправлено.", reply_markup=admin_markup)
    bot.register_next_step_handler(msg, admin_menu_accept_action)

def logs_get_action(message):
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return
    
    if message.text.lower() == "перезаписать":
        msg = bot.send_message(message.chat.id, "Введите данные")
        bot.register_next_step_handler(msg, logs_get_text)
        return

def logs_get_text(message):
    text = message.text
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return
    db.set_logs(text)
    msg = bot.send_message(message.chat.id, "Записано", reply_markup=admin_markup)
    bot.register_next_step_handler(msg, admin_menu_accept_action)


def actions_factory_menu(message):
    if message.text.lower() == "админ панель":
        msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return

    if message.text.lower() == "печать на бумаге":
        msg = bot.send_message(message.chat.id, "Отправьте pdf файл(есть поддержка только PDF!)")
        bot.register_next_step_handler(msg, paper_print)

    if message.text.lower() == "отправить голосовое":
        msg = bot.send_message(message.chat.id, "Отправьте голосовое сообщение")
        bot.register_next_step_handler(msg, send_voice)

def paper_print(message):
    try:
        if message.text.lower() == "админ панель":
            msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
            bot.register_next_step_handler(msg, admin_menu_accept_action)
            return
    except:
        pass

    if message.document == None:
        msg = bot.send_message(message.chat.id, "Не удалось получить файл.", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return
    
    file = message.document

    file_name = file.file_name
    extension = file_name.split(".")[-1]
    unique_name = utils.get_unique_id()


    file_info = bot.get_file(file.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_name = unique_name + "." + extension
    with open(os.path.join("media", save_name), 'wb') as new_file:
        new_file.write(downloaded_file)

    file = os.path.join("media", save_name)
    services.server.paper_print(file)
    os.remove(file)
    msg = bot.send_message(message.chat.id, "Отправлено.", reply_markup=admin_markup)
    bot.register_next_step_handler(msg, admin_menu_accept_action)

def send_voice(message):
    try:
        if message.text.lower() == "админ панель":
            msg = bot.send_message(message.chat.id, "Панель администратора открыта", reply_markup=admin_markup)
            bot.register_next_step_handler(msg, admin_menu_accept_action)
            return
    except:
        pass

    if message.voice == None:
        msg = bot.send_message(message.chat.id, "Не удалось получить файл.", reply_markup=admin_markup)
        bot.register_next_step_handler(msg, admin_menu_accept_action)
        return

    file = message.voice

    file_name = file.file_name
    extension = "ogg"
    unique_name = utils.get_unique_id()

    file_info = bot.get_file(file.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_name = unique_name + "." + extension
    with open(os.path.join("media", save_name), 'wb') as new_file:
        new_file.write(downloaded_file)

    file = os.path.join("media", save_name)

    #AudioSegment.from_file(file).export(file.split(".")[0] + ".mp3", format="mp3")
    #os.remove(file)

    #services.server.send_voice(file.split(".")[0] + ".mp3", VOICE_PLAYBACK_SERVER)
    #os.remove(file.split(".")[0] + ".mp3")

    #data, samplerate = sf.read(file)
    #sf.write(file.split(".")[0] + ".wav", data, samplerate)  

    services.server.send_voice(file, VOICE_PLAYBACK_SERVER)
    os.remove(file)

    msg = bot.send_message(message.chat.id, "Файл отправлен.", reply_markup=admin_markup)
    bot.register_next_step_handler(msg, admin_menu_accept_action)
    return

print("Protoworks Telegram front bot v0.1")

bot.infinity_polling()
