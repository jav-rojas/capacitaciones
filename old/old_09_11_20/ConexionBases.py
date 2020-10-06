import mysql.connector

# Clase para BBDD:

class Bases():
  
  # Attributes (por ahora ninguno, irán en constructor)
  #host = "localhost"
  #user = "capacitaciones"
  #passwd = "Microdatos2020."
  #database = "capacitaciones"
  
  # Constructor
  def __init__(self, host = "localhost", user = "capacitaciones", passwd = "Microdatos2020.", database = "capacitaciones"):
    self.host = host
    self.user = user
    self.passwd = passwd
    self.database = database
  
  # Funciones internas
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
                   
  def add_created_last(self,username,):
    self.create_connection()
    dt = datetime
    self.c.execute('INSERT INTO users_info {} VALUES ("{}","{}","{}")')
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