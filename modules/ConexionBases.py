import mysql.connector
import numpy as np

# Clases para BBDD:


class Conexion():

    # Attributes (por ahora ninguno, irán en constructor)
    # host = "localhost"
    # user = "capacitaciones"
    # passwd = "Microdatos2020."
    # database = "capacitaciones"

    # Constructor
    def __init__(self, host="localhost", user="capacitaciones", passwd="Microdatos2020.", database="capacitaciones"):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database

    # Methods
    def create_connection(self):
        self.db_connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            database=self.database)
        self.c = self.db_connection.cursor()

    def commit_close_connection(self):
        self.db_connection.commit()
        self.c.close()
        self.db_connection.close()

    def execute(self, query):
        self.create_connection()
        self.c.execute(query)
        self.data = self.c.fetchall()
        return self.data


class BasesUsuarios(Conexion):

    # Methods
    def add_user_login(self, username, password, created_at):
        self.create_connection()
        self.c.execute('INSERT INTO Username (username,password,created_at,updated_at) VALUES ("{}","{}","{}","{}")'.format(username, password, created_at, created_at))
        self.commit_close_connection()

    def add_user_info(self, username, new_nombre, new_apellido, new_email, new_updated_at):
        self.create_connection()
        self.c.execute('UPDATE Username SET first_name = {}, last_name = {}, email = {}, updated_at = "{}" WHERE username = "{}"'.format(
            "'{}'".format(new_nombre) if new_nombre != '' else 'NULL',
            "'{}'".format(new_apellido) if new_apellido != '' else 'NULL',
            "'{}'".format(new_email) if new_email != '' else 'NULL',
            new_updated_at,
            username))
        self.commit_close_connection()

    def add_batch_users(self, input_tuple=None, created_at=None):
        for i in range(len(input_tuple)):
            self.add_user_login(username=input_tuple[i][0], password=input_tuple[i][1], created_at=created_at)
            self.add_user_info(username=input_tuple[i][0], new_nombre=input_tuple[i][2], new_apellido=input_tuple[i][3], new_email=input_tuple[i][4], new_updated_at=created_at)

    def act_last_access(self, username, new_updated_at):
        self.create_connection()
        self.c.execute('UPDATE Username SET updated_at = "{}" WHERE username = "{}"'.format(new_updated_at, username))
        self.commit_close_connection()

    def login_user(self, username, password):
        # En cada login, recupera solo si el usuario y la contraseña coinciden:
        self.create_connection()
        self.c.execute('SELECT * FROM Username WHERE username = "{}" AND password = "{}"'.format(username, password))
        self.data = self.c.fetchall()
        self.commit_close_connection()
        return self.data

    def view_all_users_logininfo(self):
        self.create_connection()
        self.c.execute('SELECT username, password FROM Username')
        self.data = self.c.fetchall()
        self.commit_close_connection()
        return self.data

    def view_all_users_info(self):
        self.create_connection()
        self.c.execute('SELECT username, first_name, last_name, email, created_at, updated_at FROM Username')
        self.data = self.c.fetchall()
        self.commit_close_connection()
        return self.data


class BasesCap(Conexion):

    # Methods
    def add_cap_info(self, new_cap, new_cap_name, new_title, new_text_1, new_text_2, new_text_3, created_at):
        self.create_connection()

        # Si el texto es vacío, debe ser NULL en SQL:
        texts = [new_text_1, new_text_2, new_text_3]
        for i in range(0, len(texts)):
            if texts[i] == "":
                texts[i] = "NULL"
            else:
                texts[i] = '"{}"'.format(texts[i])
        self.c.execute('INSERT INTO Training (key_name,name,title,text1,text2,text3,created_at,updated_at) '
                       'VALUES ("{}","{}","{}",{},{},{},"{}","{}")'.format(new_cap, new_cap_name, new_title, texts[0], texts[1], texts[2], created_at, created_at))
        self.commit_close_connection()

    def add_video(self, id_cap, new_title, new_order, new_link, new_text_1, new_text_2, created_at):
        self.create_connection()

        # Si el texto es vacío, debe ser NULL en SQL:
        texts = [new_text_1, new_text_2]
        for i in range(0, len(texts)):
            if texts[i] == "":
                texts[i] = "NULL"
            else:
                texts[i] = '"{}"'.format(texts[i])
        self.c.execute('INSERT INTO TrainingVideo (training_id,title,link,orden,text1,text2,created_at,updated_at) '
                       'VALUES ("{}","{}","{}","{}",{},{},"{}","{}")'.format(id_cap, new_title, new_link, new_order, texts[0], texts[1], created_at, created_at))
        self.commit_close_connection()

    def retrieve_all_cap(self):
        self.create_connection()
        self.c.execute('SELECT * FROM Training')
        self.data = self.c.fetchall()
        self.commit_close_connection()
        return self.data

    def retrieve_cap_info(self, key=False, elements=False):
        self.create_connection()
        self.c.execute('SELECT {}, name FROM Training WHERE name != "default"'.format('key_name' if key else 'id'))
        self.data = self.c.fetchall()
        if not key:
            self.options = ['-- Seleccione una capacitación --']
            self.id_caps = [1]
            for i in range(0, len(self.data)):
                self.id_caps.append(self.data[i][0])
            for i in range(0, len(self.data)):
                self.options.append(self.data[i][1])
            self.commit_close_connection()
            return self.options, self.id_caps
        else:
            self.key_name = []
            self.name = []
            for i in range(0, len(self.data)):
                self.key_name.append(self.data[i][0])
            for i in range(0, len(self.data)):
                self.name.append(self.data[i][1])
            self.commit_close_connection()
            self.elements = []
            for i in range(0, len(self.data)):
                self.elements.append('<strong>' + self.key_name[i] + '</strong>' + ' para ' + self.name[i])
            if elements:
                return self.elements
            else:
                return self.key_name, self.name

    def retrieve_video_info(self, id_cap):
        self.create_connection()
        self.c.execute('SELECT id, title, link FROM TrainingVideo WHERE training_id = "{}"'.format(id_cap))
        self.data = self.c.fetchall()
        self.titulo_video = []
        self.links = []
        self.n_videos = []
        for i in range(0, len(self.data)):
            self.n_videos.append(self.data[i][0])
        for i in range(0, len(self.data)):
            self.titulo_video.append(self.data[i][1])
        for i in range(0, len(self.data)):
            self.links.append(self.data[i][2])
        return self.n_videos, self.titulo_video, self.links


class BasesUserCap(Conexion):

    # Methods
    def add_usertraining(self, username=None, key_name=None, input_tuple=None, tuples=False):
        self.create_connection()
        if tuples:
            for i in range(len(input_tuple)):
                self.c.execute(
                    'INSERT INTO UsernameTraining (username_id, training_id) '
                    'VALUES ( '
                    '(SELECT Username.id FROM Username WHERE username = "{}"), '
                    '(SELECT Training.id FROM Training WHERE key_name = "{}")) '.format(input_tuple[i][0], input_tuple[i][1]))
            self.commit_close_connection()
        else:
            self.c.execute(
                'INSERT INTO UsernameTraining (username_id, training_id) '
                'VALUES ( '
                '(SELECT Username.id FROM Username WHERE username = "{}"), '
                '(SELECT Training.id FROM Training WHERE key_name = "{}")) '.format(username, key_name))
            self.commit_close_connection()

    def retrieve_associated_trainings(self, username=None):
        self.create_connection()
        self.c.execute(
            'SELECT training.id, training.key_name, training.name '
            'FROM UsernameTraining '
            'JOIN Training ON UsernameTraining.training_id = Training.id '
            'WHERE username_id = (SELECT id FROM Username WHERE username = "{}")'.format(username))
        self.data = self.c.fetchall()
        self.options = ['-- Seleccione una capacitación --']
        self.id_caps = [1]
        for i in range(len(self.data)):
            self.id_caps.append(self.data[i][0])
        for i in range(len(self.data)):
            self.options.append(self.data[i][1] + ' - ' + self.data[i][2])
        self.commit_close_connection()
        return self.options, self.id_caps

    def retrieve_usertraining_info(self):
        self.create_connection()
        self.c.execute(
            'SELECT username.username, training.key_name '
            'FROM username '
            'JOIN usernametraining ON username.id = usernametraining.username_id '
            'JOIN training ON usernametraining.training_id = training.id')
        self.data = self.c.fetchall()
        self.username_training = []
        for i in range(0, len(self.data)):
            self.username_training.append((self.data[i][0], self.data[i][1]))
        return self.username_training
