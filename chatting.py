import os
import pickle as pkl
import threading as td
import time

import dotenv as dv
from flask import Flask, redirect, render_template, request, session, url_for

from chatmanager import Chatmanager, Usermanager

dv.load_dotenv('.env')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


def if_logged_in(username):
    return Usermanager.is_logged_in(username)

def is_user_active():
    try:
        if session['username'] == None:
            print(end='')#의미없는 코드
            #로그인 안돼있으면 except문으로
        else:
            return True
    except KeyError:
        return False
        

@app.get('/')
def index():
    if is_user_active():
        return render_template('index.html',logined_user=session['username'])
    else:
        return render_template('index.html',logined_user="로그인되어 있지 않음")
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if Usermanager.get_user(username) is None:
            Usermanager.add_user(username, password)
            return render_template('signup.html', username=username)
        else:
            return redirect(url_for('login'))
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Usermanager.get_user(username)
        if user and user.password == password and user.username == username:
            user.is_logged_in = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')


@app.post('/logout')
def logout():
    username = session.get('username')
    if username:
        user = Usermanager.get_class_by_username(username)
        if user:
            user.is_logged_in = False
        session.pop('username', None)
    return redirect(url_for('index'))


@app.get('/inchat/<chatname>')
def inchat(chatname):
    username = session.get('username')
    if username and if_logged_in(username):
        chat = Chatmanager.get_class_by_chatname(chatname)
        if not chat:
            return redirect(url_for('chat'))
        return render_template(
            'inchat.html',
            chatname=chat.chat_name,
            messages=chat.get_all_messages(),
            username=username
        )
    else:
        return redirect(url_for('login'))


@app.get('/chat')
def chat():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    user = Usermanager.get_class_by_username(username)
    chat_names = user.chattings if user else []
    return render_template('chat.html', chats=chat_names, username=username)


@app.route('/addchat', methods=['GET', 'POST'])
def addchat():
    username = session.get('username')
    if username and if_logged_in(username):
        if request.method == 'POST':
            chat_name = request.form.get('chat_name')
            users = request.form.get('users').split(',')
            users = [u.strip() for u in users if u.strip()]
            users.append(username)

            Chatmanager.add_chat(chat_name, users)
            chat = Chatmanager.get_class_by_chatname(chat_name)
            for user in users:
                Usermanager.get_class_by_username(user).join_chat(chat)
            return redirect(url_for('chat'))
        else:
            return render_template('addchat.html')
    else:
        return redirect(url_for('login'))


@app.post('/leavechat')
def leavechat():
    username = session.get('username')
    check = request.form.get('동의')
    check = True if check == 'True' else False
    if username and if_logged_in(username) and check:
        chat_name = request.form.get('chatname')
        chat = Chatmanager.get_class_by_chatname(chat_name)
        user = Usermanager.get_class_by_username(username)
        if chat and user:
            chat.send_admin_message(f'[{username}]님이 채팅방을 나갔습니다.')
            user.leave_chat(chat)
        return redirect(url_for('chat'))
    else:
        return redirect(url_for('login'))


@app.post('/addmessage')
def addmessage():   
    username = session.get('username')
    if username and if_logged_in(username):
        chat = Chatmanager.get_class_by_chatname(request.form.get('chatname'))
        message = request.form.get('message')
        if chat and message:
            chat.add_message(username, message)
        return redirect(url_for('inchat', chatname=chat.chat_name))
    else:
        return redirect(url_for('login'))


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

def update_db():
    while True:
        time.sleep(2)
        pkl.dump(Usermanager, open('db/user.pkl', 'wb'))
        pkl.dump(Chatmanager, open('db/chat.pkl', 'wb'))
if __name__ == '__main__':
    db_thread = td.Thread(target=update_db, daemon=True)
    db_thread.start()
    app.run(
        port=int(os.environ.get('PORT')),
        debug=True if os.environ.get('DEBUG') == 'True' else False,
        host=os.environ.get('HOST')
            )
else:
    raise RuntimeError("This module is not meant to be imported directly.")