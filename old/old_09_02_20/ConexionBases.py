import mysql.connector
# Clase para BBDD:

class Bases():
  
  # Attributes
  host = "localhost"
  user = "capacitaciones"
  passwd = "Microdatos2020."
  database = "capacitaciones"
  
  # Constructor
  def __init__(self, host = "localhost", user = "capacitaciones", passwd = "Microdatos2020.", database = "capacitaciones"):
    self.host = host
    self.user = user
    self.passwd = passwd
    self.database = database
  
  def create_connection(self):
    self.db_connection = mysql.connector.connect(
      host = self.host,
      user = self.user,
      passwd = self.passwd,
      database = self.database)
    print(self.db_connection)
    self.c = self.db_connection.cursor()
    print(self.c)
    
  def commit_close_connection(self):
    self.db_connection.commit()
    self.c.close()
    self.db_connection.close()

  # Methods
  def add_user_login(self,username,password):
    self.create_connection()
    self.c.execute('INSERT INTO users_login (username,password) VALUES ("{}","{}")'.format(username,password))
    self.commit_close_connection()

  def add_user_info(self,new_user,new_nombre,new_apellido,new_email,new_creation_date,new_last_access_date):
    self.create_connection()
    self.info = '(username,nombre,apellido,email,creation_date,last_access_date)'
    self.c.execute('INSERT INTO users_info {} VALUES ("{}","{}","{}","{}","{}","{}")'.format(self.info,new_user,new_nombre,new_apellido,new_email,new_creation_date,new_last_access_date))
    self.commit_close_connection()    

  def act_last_access(self,username,last_access_date):
    self.create_connection()
    self.c.execute('UPDATE users_info SET last_access_date = "{}" WHERE username = "{}"'.format(last_access_date,username))
    self.commit_close_connection()

  def login_user(self,username,password):
    self.create_connection()
    self.c.execute('SELECT * FROM users_login WHERE username ="{}" AND password = "{}"'.format(username,password))
    self.data = self.c.fetchall()
    self.commit_close_connection()
    return self.data

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