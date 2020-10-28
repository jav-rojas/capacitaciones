import mysql.connector
import numpy as np
import pandas as pd


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
            self.create_connection()
            self.c.execute('SELECT * FROM Username WHERE username = "{}"'.format(input_tuple[i][0]))
            self.data = self.c.fetchall()
            if not self.data:
                self.add_user_login(username=input_tuple[i][0], password=input_tuple[i][1], created_at=created_at)
                self.add_user_info(username=input_tuple[i][0], new_nombre=input_tuple[i][2], new_apellido=input_tuple[i][3], new_email=input_tuple[i][4], new_updated_at=created_at)
            else:
                pass

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

    # Internal Methods
    def parse_ids(self, ids):
        if isinstance(ids, list) and len(ids) == 1:
            ids = '({})'.format(ids[0])
        elif isinstance(ids, list) and len(ids) > 1:
            ids = str(tuple(ids))
        elif isinstance(ids, (str, int)):
            ids = '({})'.format(ids)
        else:
            print(type(ids))
        return ids

    # Insert Methods
    def add_training(self, training_key_name, training_name, training_title, training_text1, training_text2, training_text3, created_at):
        self.create_connection()
        self.c.execute(
            'INSERT INTO Training (key_name,name,title,text1,text2,text3,created_at,updated_at) '
            'VALUES ("{}","{}","{}",{},{},{},"{}","{}")'.format(
                training_key_name,
                training_name,
                training_title,
                "'{}'".format(training_text1) if training_text1 else 'NULL',
                "'{}'".format(training_text2) if training_text2 else 'NULL',
                "'{}'".format(training_text3) if training_text3 else 'NULL',
                created_at,
                created_at))
        self.commit_close_connection()

    def add_video(self, training_id, video_title, video_link, orden, video_text1, video_text2, created_at):
        self.create_connection()
        self.c.execute(
            'INSERT INTO TrainingVideo (training_id,title,link,orden,text1,text2,created_at,updated_at) '
            'VALUES ("{}","{}","{}","{}",{},{},"{}","{}")'.format(
                training_id,
                video_title,
                video_link,
                orden,
                "'{}'".format(video_text1) if video_text1 else 'NULL',
                "'{}'".format(video_text2) if video_text2 else 'NULL',
                created_at,
                created_at))
        self.commit_close_connection()

    def add_question(self, training_id=None, trainingvideo_id=None, question_type=None, question_title=None, question_choice1=False, question_choice2=False, question_choice3=False, question_choice4=False, created_at=None):
        self.create_connection()
        self.c.execute(
            'INSERT INTO TrainingQuestion (training_id,trainingvideo_id,type,title,choice1,choice2,choice3,choice4,created_at,updated_at) '
            'VALUES ("{}","{}","{}","{}",{},{},{},{},"{}","{}")'.format(
                training_id,
                trainingvideo_id,
                question_type,
                question_title,
                "'{}'".format(question_choice1) if question_choice1 else 'NULL',
                "'{}'".format(question_choice2) if question_choice2 else 'NULL',
                "'{}'".format(question_choice3) if question_choice3 else 'NULL',
                "'{}'".format(question_choice4) if question_choice4 else 'NULL',
                created_at,
                created_at))
        self.commit_close_connection()

    # Update Methods
    def update_training(self, id, training_key_name, training_name, training_title, training_text1, training_text2, training_text3, updated_at):
        self.create_connection()
        self.c.execute(
            'UPDATE Training '
            'SET key_name = "{}", name = "{}", title = "{}", text1 = {}, text2 = {}, text3 = {}, updated_at = "{}" WHERE id = "{}"'.format(
                training_key_name,
                training_name,
                training_title,
                "'{}'".format(training_text1) if training_text1 != '' else 'NULL',
                "'{}'".format(training_text2) if training_text2 != '' else 'NULL',
                "'{}'".format(training_text3) if training_text3 != '' else 'NULL',
                updated_at,
                id))
        self.commit_close_connection()

    def update_video(self, id, video_title, video_link, orden, video_text1, video_text2, updated_at):
        self.create_connection()
        self.c.execute(
            'UPDATE TrainingVideo '
            'SET title = "{}", link = "{}", orden = "{}", text1 = {}, text2 = {}, updated_at = "{}" WHERE id = "{}"'.format(
                video_title,
                video_link,
                orden,
                "'{}'".format(video_text1) if video_text1 != '' else 'NULL',
                "'{}'".format(video_text2) if video_text2 != '' else 'NULL',
                updated_at,
                id))
        self.commit_close_connection()

    def update_question(self, id, question_type, question_title, question_choice1=None, question_choice2=None, question_choice3=None, question_choice4=None, updated_at=None):
        self.create_connection()
        self.c.execute(
            'UPDATE TrainingQuestion '
            'SET type = "{}", title = "{}", choice1 = {}, choice2 = {}, choice3 = {}, choice4 = {}, updated_at = "{}" WHERE id = "{}"'.format(
                question_type,
                question_title,
                "'{}'".format(question_choice1) if question_choice1 else 'NULL',
                "'{}'".format(question_choice2) if question_choice2 else 'NULL',
                "'{}'".format(question_choice3) if question_choice3 else 'NULL',
                "'{}'".format(question_choice4) if question_choice4 else 'NULL',
                updated_at,
                id))
        self.commit_close_connection()

    # Select Methods
    def retrieve_training(self, id):
        self.create_connection()
        self.c.execute('SELECT key_name, name, title, text1, text2, text3 FROM Training WHERE id = "{}"'.format(id))
        self.data = self.c.fetchall()
        self.training = []
        for i in range(len(self.data[0])):
            self.training.append(self.data[0][i])
        self.commit_close_connection()
        return self.training

    def retrieve_video(self, id):
        self.create_connection()
        self.c.execute('SELECT title, orden, link, text1, text2 FROM TrainingVideo WHERE id = "{}"'.format(id))
        self.data = self.c.fetchall()
        self.video = []
        for i in range(len(self.data[0])):
            self.video.append(self.data[0][i])
        return self.video

    def retrieve_question(self, id):
        self.create_connection()
        self.c.execute('SELECT type, title, choice1, choice2, choice3, choice4 FROM TrainingQuestion WHERE id = "{}"'.format(id))
        self.data = self.c.fetchall()
        self.question = []
        for i in range(len(self.data[0])):
            self.question.append(self.data[0][i])
        return self.question

    def retrieve_training_info(self, info=False, key=False, elements=False):
        if info:
            self.create_connection()
            self.c.execute('SELECT id, key_name, name FROM Training WHERE id > 1')
            self.data = self.c.fetchall()
            self.training_ids = []
            self.training_key_names = []
            self.training_name = []
            for i in range(len(self.data)):
                self.training_ids.append(self.data[i][0])
                self.training_key_names.append(self.data[i][1])
                self.training_name.append(self.data[i][2])
            return self.training_ids, self.training_key_names, self.training_name

        else:
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

    def retrieve_video_info(self, training_id):
        self.training_id = self.parse_ids(training_id)
        self.create_connection()
        print('SELECT id, title, link, orden FROM TrainingVideo WHERE training_id in {} ORDER BY orden ASC'.format(self.training_id))
        self.c.execute('SELECT id, title, link, orden FROM TrainingVideo WHERE training_id in {} ORDER BY orden ASC'.format(self.training_id))
        self.data = self.c.fetchall()
        self.video_ids = []
        self.video_titles = []
        self.video_links = []
        self.orden = []
        for i in range(0, len(self.data)):
            self.video_ids.append(self.data[i][0])
        for i in range(0, len(self.data)):
            self.video_titles.append(self.data[i][1])
        for i in range(0, len(self.data)):
            self.video_links.append(self.data[i][2])
        for i in range(0, len(self.data)):
            self.orden.append(self.data[i][3])
        return self.video_ids, self.video_titles, self.video_links, self.orden

    def retrieve_question_info(self, training_id, trainingvideo_id):
        self.training_id = self.parse_ids(training_id)
        self.trainingvideo_id = self.parse_ids(trainingvideo_id)
        self.create_connection()
        self.c.execute('SELECT id, title FROM TrainingQuestion WHERE training_id in {} AND trainingvideo_id in {}'.format(self.training_id, self.trainingvideo_id))
        self.data = self.c.fetchall()
        self.question_ids = []
        self.question_titles = []
        for i in range(0, len(self.data)):
            self.question_ids.append(self.data[i][0])
        for i in range(0, len(self.data)):
            self.question_titles.append(self.data[i][1])
        return self.question_ids, self.question_titles

    def retrieve_all_info(self, training_id):
        self.training_id = self.parse_ids(training_id)
        self.create_connection()
        self.c.execute(
            'SELECT '
            'Training.title, Training.text1, Training.text2, Training.text3, '
            'TrainingVideo.title, TrainingVideo.link, TrainingVideo.orden, TrainingVideo.text1, TrainingVideo.text2, '
            'TrainingQuestion.type, TrainingQuestion.title, TrainingQuestion.choice1, TrainingQuestion.choice2, TrainingQuestion.choice3, TrainingQuestion.choice4 '
            'FROM Training '
            'JOIN TrainingVideo ON Training.id = TrainingVideo.training_id '
            'JOIN TrainingQuestion ON TrainingVideo.id = TrainingQuestion.trainingvideo_id '
            'WHERE TrainingQuestion.training_id in {} '
            'ORDER BY TrainingVideo.orden, TrainingQuestion.id ASC'.format(self.training_id))
        self.data = self.c.fetchall()
        return self.data

    def view_training_info(self, id, admin_view=True):
        self.id = self.parse_ids(id)
        self.create_connection()
        if admin_view:
            self.df = pd.read_sql(
                'SELECT key_name, name, title, text1, text2, text3, created_at, updated_at '
                'FROM Training '
                'WHERE id in {} '
                'ORDER BY id ASC'.format(self.id),
                con=self.db_connection)
            return self.df
        else:
            self.c.execute(
                'SELECT '
                'Training.title, Training.text1, Training.text2, Training.text3 '
                'FROM Training '
                'WHERE id in {}'.format(self.id))
            self.data = self.c.fetchall()
            return self.data[0]

    def view_video_info(self, training_id, id=[], admin_view=True):
        self.training_id = self.parse_ids(training_id)
        self.id = self.parse_ids(id)
        self.create_connection()
        if admin_view:
            self.df = pd.read_sql(
                'SELECT Training.key_name, Training.name, TrainingVideo.title, TrainingVideo.link, TrainingVideo.orden, TrainingVideo.text1, TrainingVideo.text2, TrainingVideo.created_at, TrainingVideo.updated_at '
                'FROM Training '
                'JOIN TrainingVideo ON Training.id = TrainingVideo.training_id '
                'WHERE TrainingVideo.training_id in {} and TrainingVideo.id in {} '
                'ORDER BY Training.id, TrainingVideo.orden ASC'.format(self.training_id, self.id),
                con=self.db_connection)
            return self.df
        else:
            self.c.execute(
                'SELECT TrainingVideo.title, TrainingVideo.link, TrainingVideo.orden, TrainingVideo.text1, TrainingVideo.text2 '
                'FROM Training '
                'JOIN TrainingVideo ON Training.id = TrainingVideo.training_id '
                'WHERE TrainingVideo.training_id IN {} AND TrainingVideo.id IN {}'
                'ORDER BY TrainingVideo.orden ASC'.format(self.training_id, self.id))
            self.data = self.c.fetchall()
            return self.data[0]

    def view_question_info(self, training_id, trainingvideo_id, id=[], admin_view=True):
        self.training_id = self.parse_ids(training_id)
        self.trainingvideo_id = self.parse_ids(trainingvideo_id)
        self.create_connection()
        if admin_view:
            self.id = self.parse_ids(id)
            self.df = pd.read_sql(
                'SELECT Training.key_name, Training.name, TrainingVideo.title, TrainingVideo.orden, TrainingQuestion.title, TrainingQuestion.type, '
                'TrainingQuestion.choice1, TrainingQuestion.choice2, TrainingQuestion.choice3, TrainingQuestion.choice4, TrainingQuestion.created_at, TrainingQuestion.updated_at '
                'FROM Training '
                'JOIN TrainingVideo ON Training.id = TrainingVideo.training_id '
                'JOIN TrainingQuestion ON TrainingVideo.id = TrainingQuestion.trainingvideo_id '
                'WHERE TrainingQuestion.training_id in {} and TrainingQuestion.trainingvideo_id in {} and TrainingQuestion.id in {} '
                'ORDER BY Training.id, TrainingVideo.orden, TrainingQuestion.id ASC'.format(self.training_id, self.trainingvideo_id, self.id),
                con=self.db_connection)
            return self.df
        else:
            self.c.execute(
                'SELECT '
                'TrainingQuestion.type, TrainingQuestion.title, TrainingQuestion.choice1, TrainingQuestion.choice2, TrainingQuestion.choice3, TrainingQuestion.choice4 '
                'FROM Training '
                'JOIN TrainingVideo ON Training.id = TrainingVideo.training_id '
                'JOIN TrainingQuestion ON TrainingVideo.id = TrainingQuestion.trainingvideo_id '
                'WHERE TrainingQuestion.training_id IN {} AND TrainingQuestion.trainingvideo_id in {} '
                'ORDER BY TrainingQuestion.id ASC'.format(self.training_id, self.trainingvideo_id))
            self.data = self.c.fetchall()
            return self.data

    # Delete Methods
    def delete_training(self, id):
        self.create_connection()
        self.c.execute('DELETE FROM Training WHERE id = "{}"'.format(id))
        self.commit_close_connection()

    def delete_video(self, id):
        self.create_connection()
        self.c.execute('DELETE FROM TrainingVideo WHERE id = "{}"'.format(id))
        self.commit_close_connection()

    def delete_question(self, id):
        self.create_connection()
        self.c.execute('DELETE FROM TrainingQuestion WHERE id = "{}"'.format(id))
        self.commit_close_connection()


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
