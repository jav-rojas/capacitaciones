import streamlit as st
import pandas as pd
import mysql.connector
import EstadoSesion
import ConexionBases
from Utilidades import to_HTML
from ConexionBases import Bases
import rerun
from datetime import datetime

def main():

  
  st.beta_set_page_config(page_title="Capacitaciones CMD", page_icon="https://pbs.twimg.com/profile_images/1161359420967784449/Hsgy0Zv2.jpg", layout='centered', initial_sidebar_state='auto')

  ### Bloques de sesión ###
  session_state = EstadoSesion.get(boton_login=False, boton_registro=False, log_state = False, username = "", password = "", key = 0)
  ### Fin de bloques de sesión ###

  username = st.sidebar.text_input("Usuario", key = session_state.key)
  session_state.username = username
  password = st.sidebar.text_input("Contraseña", type='password', key = session_state.key)
  session_state.password = password

  boton_login = st.sidebar.button("Login")
  if boton_login or session_state.boton_login:
    session_state.boton_login = True
    result, dates = Bases().login_user(session_state.username,session_state.password)
    
    if result and session_state.username != "admin":
      # Botón para cerrar sesión
      cerrar_sesion = st.sidebar.button("Cerrar sesión")
      if cerrar_sesion:
        session_state.boton_login = False
        session_state.key += 1
        rerun.rerun()   
      
      # Si es primera vez que entra, entonces debe ingresar sus datos antes de continuar
      if dates[0][0] == dates[0][1]:
        st.header("Formulario de datos personales")
        st.markdown(to_HTML().paragraph("Dado que es primera vez que ingresa a la Web de Capacitaciones, es necesario que ingrese sus datos personales para continuar:"), unsafe_allow_html = True)    
        new_nombre = st.text_input("Nombre:", max_chars = 35)
        new_apellido = st.text_input("Apellido:", max_chars = 35)
        new_email = st.text_input("e-mail:", max_chars = 255)
        new_last_access_date = datetime.now()
        
        if st.button("Enviar"):
          try:
            Bases().add_user_info(session_state.username,new_nombre,new_apellido,new_email,new_last_access_date)
            st.success("Los datos se han guardado correctamente. Presiona aquí para continuar:")
            if st.button("Continuar a la página de capacitaciones"):
              rerun.rerun()
              
          except:
            st.warning("Por favor revise los datos ingresados.")
      
      # Si ya ha ingresado antes, entonces que continúe directamente
      else:
        if not session_state.log_state:
          Bases().act_last_access(session_state.username,datetime.now())
          st.sidebar.success("Has iniciado sesión como {}".format(session_state.username))
          session_state.log_state = True
        
        # Aquí debería acceder a SQL a buscar nombres de proyectos para capacitación
        opciones_cap_selec = ['-- Seleccione un proyecto --','TS4 - Termómetro Social 4','EOD - Encuesta de Ocupación y Desocupación']
        cap_selec = st.sidebar.selectbox("Seleccione un proyecto:", opciones_cap_selec, index=0)        
        
        if cap_selec == "TS4 - Termómetro Social 4":
          
          st.title("Capacitación Termómetro Social 4")
          
          # Aquí debería acceder a SQL a buscar links de capacitación de TS4
          st.markdown(to_HTML().paragraph(), unsafe_allow_html = True)
          st.markdown(to_HTML().paragraph(), unsafe_allow_html = True)
          
          opciones_cap_ts4 = ['-- Seleccione un video de capacitación --','Video 1 - Algo particular', 'Video 2 - Otro particular']
          cap_ts4 = st.selectbox("Por favor seleccione un video de capacitación:", opciones_cap_ts4, index=0)
          
          if cap_ts4 == 'Video 1 - Algo particular':
            st.markdown(to_HTML().video(), unsafe_allow_html = True)
            st.header("Cuestionario")
            st.text_area("1. Alguna pregunta iría aquí con limitantes de altura y carácteres máximos")
            st.text_area("2. Alguna pregunta iría aquí con limitantes de altura y carácteres máximos")
            st.text_area("3. Alguna pregunta iría aquí con limitantes de altura y carácteres máximos")
            st.button("Enviar respuestas")
            
          elif cap_ts4 == 'Video 2 - Otro particular':
            st.markdown(to_HTML().video(), unsafe_allow_html = True)
            st.header("Cuestionario")
            st.text_area("1. Alguna pregunta iría aquí con limitantes de altura y carácteres máximos")
            st.text_area("2. Alguna pregunta iría aquí con limitantes de altura y carácteres máximos")
            st.text_area("3. Alguna pregunta iría aquí con limitantes de altura y carácteres máximos")
            st.button("Enviar respuestas")

        if cap_selec == "EOD - Encuesta de Ocupación y Desocupación":
          
          st.title("Capacitación Encuesta de Ocupación y Desocupación")
          
          # Aquí debería acceder a SQL a buscar links de capacitación de EOD
          st.markdown(to_HTML().paragraph(), unsafe_allow_html = True)
          st.markdown(to_HTML().paragraph(), unsafe_allow_html = True)
          
          opciones_cap_eod = ['-- Seleccione un video de capacitación --','Video 1 - Algo particular', 'Video 2 - Otro particular']
          cap_eod = st.selectbox("Por favor seleccione un video de capacitación:", opciones_cap_eod, index=0)
          
          if cap_eod == 'Video 1 - Algo particular':
            st.markdown(to_HTML().video(), unsafe_allow_html = True)   
            st.header("Cuestionario")
            st.text_area("1. Alguna pregunta iría aquí con limitantes de altura y carácteres máximos")
            st.text_area("2. Alguna pregunta iría aquí con limitantes de altura y carácteres máximos")
            st.text_area("3. Alguna pregunta iría aquí con limitantes de altura y carácteres máximos")
            st.button("Enviar respuestas")
            
          elif cap_eod == 'Video 2 - Otro particular':
            st.markdown(to_HTML().video(), unsafe_allow_html = True) 
            st.header("Cuestionario")
            st.text_area("1. Alguna pregunta iría aquí con limitantes de altura y carácteres máximos")
            st.text_area("2. Alguna pregunta iría aquí con limitantes de altura y carácteres máximos")
            st.text_area("3. Alguna pregunta iría aquí con limitantes de altura y carácteres máximos")
            st.button("Enviar respuestas")
            
    elif result and session_state.username == "admin":
      cerrar_sesion = st.sidebar.button("Cerrar sesión")
      if cerrar_sesion:
        session_state.boton_login = False
        session_state.key += 1
        rerun.rerun()
      Bases().act_last_access(session_state.username,datetime.now())
      st.sidebar.success("Has iniciado sesión con la cuenta de administrador")
      st.title("Administración Web Capacitaciones Centro de Microdatos")
      st.markdown(to_HTML().paragraph("Bienvenido al apartado de administración de la web de capacitaciones del Centro de Microdatos. En este apartado, podrás realizar algunas tareas importantes, como crear nuevos usuarios, y revisar la información de los usuarios actuales. Para ello, por favor selecciona la opción deseada de la lista desplegable.") , unsafe_allow_html = True)
      option = st.selectbox(
                            'Seleccione una tarea',
                            ('','Crear nuevo usuario', 'Revisar información de usuarios existentes'))
      
      if option == "Crear nuevo usuario":
        st.subheader("Crear nueva cuenta")
        new_user = st.text_input("Usuario:", max_chars = 16)
        st.text("Debe contener un máximo de 16 carácteres.")
        new_password = st.text_input("Contraseña:", max_chars = 16, type='password')
        st.text("Debe contener un máximo de 16 carácteres entre letras y números.")
        if st.button("Enviar"):
          Bases().add_user_login(new_user,new_password,datetime.now())
          st.success("La cuenta ha sido creada correctamente.")
          
      if option == "Revisar información de usuarios existentes":
        st.subheader("Información de usuarios existentes")
        st.markdown("Estos son los usuarios actuales en la tabla users_login en MySQL")        
        login_info = Bases().view_all_users_logininfo()
        info1 = pd.DataFrame(login_info,columns=["Username","Password"])
        st.dataframe(info1)
        st.markdown(to_HTML().paragraph("Esta es la información actual de cada usuario en la tabla users_info en MySQL"), unsafe_allow_html = True)    
        username_info = Bases().view_all_users_info()
        info2 = pd.DataFrame(username_info,columns=["Username","Nombre","Apellido","Email","Fecha de creación","Última fecha de conexión"]) 
        st.dataframe(info2)
    else:
      if (session_state.password != "" and not result):
        st.sidebar.error('Usuario o contraseña incorrectos. Por favor intente nuevamente.')
      else:
        pass

if __name__ == '__main__':
	main()