class Chat:
    def __init__(self, chat_name, users):
        self.chat_name = chat_name
        self.users = users
        self.messages = []   # ✅ 오타 수정 (maessages → messages)

    def add_message(self, sender, message):
        msg = f'{sender}: {message}'
        self.messages.append(msg)

    def delete_user(self, username):
        if username in self.users:
            self.users.remove(username)

    def get_my_messages(self, username):
        # ✅ sender 기준으로 필터링
        return [msg for msg in self.messages if msg['sender'] == username]

    def get_all_messages(self):
        return self.messages


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.chattings: list[Chat] = []
        self.is_logged_in = False

    def join_chat(self, chat: Chat):
        if chat not in self.chattings:
            self.chattings.append(chat)
            if self.username not in chat.users:
                chat.users.append(self.username)

    def leave_chat(self, chat: Chat):
        if chat in self.chattings:
            self.chattings.remove(chat)
            chat.delete_user(self.username)


class Usermanager:
    __users: list[User] = []

    @classmethod
    def add_user(cls, username, password):
        cls.__users.append(User(username, password))

    @classmethod
    def get_user(cls, username) -> User | None:
        for user in cls.__users:
            if user.username == username:
                return user
        return None

    @classmethod
    def remove_user(cls, username):
        user = cls.get_user(username)
        if user:
            cls.__users.remove(user)

    @classmethod
    def get_count(cls) -> int:
        return len(cls.__users)

    @classmethod
    def get_class_by_username(cls, username) -> User | None:
        return cls.get_user(username)

    @classmethod
    def is_logged_in(cls, username) -> bool:
        user = cls.get_user(username)
        return user.is_logged_in if user else False


class Chatmanager:
    __chats: list[Chat] = []

    @classmethod
    def add_chat(cls, chat_name, users: list[str]):
        cls.__chats.append(Chat(chat_name, users))

    @classmethod
    def get_chatname_by_class(cls, chat_name) -> Chat | None:
        return cls.get_class_by_chatname(chat_name)

    @classmethod
    def get_class_by_chatname(cls, chat_name) -> Chat | None:
        for chat in cls.__chats:
            if chat.chat_name == chat_name:
                return chat
        return None

    @classmethod
    def remove_chat(cls, chat_name):
        chat = cls.get_class_by_chatname(chat_name)
        if chat:
            cls.__chats.remove(chat)

    @classmethod
    def get_count(cls) -> int:
        return len(cls.__chats)
