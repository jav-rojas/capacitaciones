import mysql.connector
import numpy as np

# Clases para BBDD:

class Conexion():
  
# Attributes (por ahora ninguno, irán en constructor)
  #host = "localhost"
  #user = "capacitaciones"
  #passwd = "Microdatos2020."
  #database = "capacitaciones"
  
  # Constructor
  def __init__(self, host = "162.243.165.69", user = "capacitaciones", passwd = "Microdatos2020.", database = "capacitaciones"):
    self.host = host
    self.user = user
    self.passwd = passwd
    self.database = database
  
  # Methods
  def create_connection(self):
    self.db_connection = mysql.connector.connect(
      host = self.host,
      user = self.user,
      passwd = self.passwd,
      database = self.database)
    self.c = self.db_connection.cursor()
    
  def commit_close_connection(self):
    self.db_connection.commit()
    self.c.close()
    self.db_connection.close()  
    
  def execute(self,query):
    self.create_connection()
    self.c.execute(query)
    self.data = self.c.fetchall()
    return self.data
  
class BasesUsuarios(Conexion):

  # Methods
  def add_user_login(self,username,password,created_at):
    self.create_connection()
    self.c.execute('INSERT INTO users_login (username,password) VALUES ("{}","{}")'.format(username,password))
    self.c.execute('INSERT INTO users_info (username,creation_date,last_access_date) VALUES ("{}","{}","{}")'.format(username,created_at,created_at))
    self.commit_close_connection()

  def add_user_info(self,username,new_nombre,new_apellido,new_email,new_last_access_date):
    self.create_connection()
    self.c.execute('UPDATE users_info SET nombre = "{}", apellido = "{}", email = "{}", last_access_date = "{}" WHERE username = "{}"'.format(new_nombre,new_apellido,new_email,new_last_access_date, username))
    self.commit_close_connection()

  def act_last_access(self,username,last_access_date):
    self.create_connection()
    self.c.execute('UPDATE users_info SET last_access_date = "{}" WHERE username = "{}"'.format(last_access_date,username))
    self.commit_close_connection()

  def login_user(self,username,password):
    # En cada login, recupera solo si el usuario y la contraseña coinciden:
    self.create_connection()
    self.c.execute('SELECT * FROM users_login WHERE username ="{}" AND password = "{}"'.format(username,password))
    self.data = self.c.fetchall()
    self.commit_close_connection()
    # También recupera la fecha de creación y de último acceso:
    self.create_connection()
    self.c.execute('SELECT creation_date, last_access_date FROM users_info WHERE username = "{}"'.format(username,password))
    self.dates = self.c.fetchall()
    self.commit_close_connection()
    return self.data, self.dates

  def view_all_users_logininfo(self):
    self.create_connection()
    self.c.execute('SELECT * FROM users_login')
    self.data = self.c.fetchall()
    self.commit_close_connection()
    return self.data
  
  def view_all_users_info(self):
    self.create_connection()
    self.c.execute('SELECT * FROM users_info')
    self.data = self.c.fetchall()
    self.commit_close_connection()
    return self.data  
  
class BasesCap(Conexion):

  # Methods
  def view_all_cap(self):
    self.create_connection()
    self.c.execute('SELECT * FROM capacitaciones')
    self.data = self.c.fetchall()
    self.commit_close_connection()
    return self.data
  
  def add_cap_info(self,new_cap,new_cap_name,new_title,new_text_1,new_text_2,new_text_3,created_at):
    self.create_connection()
    
    # Si el texto es vacío, debe ser NULL en SQL:
    texts = [new_text_1,new_text_2,new_text_3]
    for i in range(0,len(texts)):
      if texts[i]=="":
        texts[i] = "NULL"
      else:
        texts[i] = '"{}"'.format(texts[i])
    self.c.execute('INSERT INTO capacitaciones VALUES ("{}","{}","{}",{},{},{},"{}","{}")'.format(new_cap,new_cap_name,new_title,texts[0],texts[1],texts[2],created_at,created_at))
    self.commit_close_connection()
    
  def add_first_video_info(self,id_cap,id_video,new_title,new_order,new_link,new_text_1,new_text_2,created_at):
    self.create_connection()
    
    # Si el texto es vacío, debe ser NULL en SQL:
    texts = [new_text_1,new_text_2]
    for i in range(0,len(texts)):
      if texts[i]=="":
        texts[i] = "NULL"
      else:
        texts[i] = '"{}"'.format(texts[i])
    self.c.execute('INSERT INTO capacitaciones_videos VALUES ("{}","{}","{}","{}","{}",{},{},"{}","{}")'.format(id_cap,id_video,new_title,new_order,new_link,texts[0],texts[1],created_at,created_at))
    self.commit_close_connection()
    
  def retrieve_cap_info(self):
    self.create_connection()
    self.c.execute('SELECT id_cap,cap_name FROM capacitaciones')
    self.data = self.c.fetchall()
    self.options = []
    self.id_caps = []
    for i in range(0,len(self.data)):
      self.id_caps.append(self.data[i][0]) 
    for i in range(0,len(self.data)):
      self.options.append(self.data[i][1])
    self.commit_close_connection()
    return self.options, self.id_caps

  def retrieve_video_info(self,id_cap):
    self.create_connection()
    self.c.execute('SELECT id_video, titulo_video, link FROM capacitaciones_videos WHERE id_cap = "{}"'.format(id_cap))
    self.data = self.c.fetchall()
    self.titulo_video = []
    self.links = []
    self.n_videos = []
    print(self.data)
    for i in range(0,len(self.data)):
      self.n_videos.append(self.data[i][0])
    for i in range(0,len(self.data)):
      self.titulo_video.append(self.data[i][1])
    for i in range(0,len(self.data)):
      self.links.append(self.data[i][2])
    return self.n_videos, self.titulo_video, self.links 
  