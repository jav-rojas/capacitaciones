import streamlit as st
import pandas as pd
import mysql.connector
import EstadoSesion
import ConexionBases
import rerun
from datetime import datetime

def main():

  ### Bloques de sesión ###
  session_state = EstadoSesion.get(boton_login=False, boton_registro=False, reg_state = False)
  if session_state.reg_state:
    st.sidebar.success("Tu cuenta ha sido creada correctamente. Por favor inicie sesión.")
    session_state.reg_state = False
  ### Fin de bloques de sesión ###
  
  st.title("Capacitaciones Centro de Microdatos")
		
  username = st.sidebar.text_input("Usuario")
  password = st.sidebar.text_input("Contraseña",type='password')
        
  boton_login = st.sidebar.button("Login")
  if boton_login or session_state.boton_login:
    session_state.boton_login = True
    session_state.boton_registro = False
    login = ConexionBases.Bases()
    result = login.login_user(username,password)
    
    if result:
      login.act_last_access(username,datetime.now())
      st.text("Estos son los usuarios actuales en la tabla users_login en MySQL")
      st.sidebar.success("Has iniciado sesión como {}".format(username))
      usuarios = ConexionBases.Bases()
      login_info = usuarios.view_all_users_logininfo()
      info1 = pd.DataFrame(login_info,columns=["Username","Password"])
      st.dataframe(info1)
      st.text("Esta es la información de registro de los usuarios actuales en la tabla users_info en MySQL")
      username_info = usuarios.view_all_users_info()
      info2 = pd.DataFrame(username_info,columns=["Username","Nombre","Apellido","Email","Fecha de creación","Última fecha de conexión"]) 
      st.dataframe(info2)
      
    else:
      st.sidebar.error('Usuario o contraseña incorrectos. Por favor intente nuevamente.')

  boton_registro = st.sidebar.button("Registrarse")
  if boton_registro or session_state.boton_registro:
    if session_state.boton_login:
      session_state.boton_login = False
      rerun.rerun()
    session_state.boton_registro = True  
    session_state.boton_login = False
    st.subheader("Crear nueva cuenta")
    new_user = st.text_input("Usuario:")
    st.text("Debe contener un máximo de 16 carácteres.")
    new_password = st.text_input("Contraseña:",type='password')
    st.text("Debe contener un máximo de 16 carácteres entre letras y números.")
    new_nombre = st.text_input("Nombre:")
    new_apellido = st.text_input("Apellido:")
    new_email = st.text_input("e-mail:")
    new_creation_date = datetime.now()
    new_last_access_date = datetime.now()
    
    if st.button("Enviar datos de registro"):
      add_login = ConexionBases.Bases()
      add_login.add_user_login(new_user,new_password)
      add_login.add_user_info(new_user,new_nombre,new_apellido,new_email,new_creation_date,new_last_access_date)
      st.sidebar.success("Tu cuenta ha sido creada correctamente. Por favor inicie sesión.")
      session_state.boton_registro = False
      session_state.reg_state = True
      rerun.rerun()
      
if __name__ == '__main__':
	main()