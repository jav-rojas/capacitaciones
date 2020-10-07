import streamlit as st
import pandas as pd
import mysql.connector
import EstadoSesion
from Utilidades import to_HTML
from ConexionBases import Conexion, BasesUsuarios, BasesCap
import rerun
from datetime import datetime    
import time

def main():
  
  st.beta_set_page_config(page_title="Capacitaciones CMD", page_icon="https://pbs.twimg.com/profile_images/1161359420967784449/Hsgy0Zv2.jpg", layout='centered', initial_sidebar_state='auto')

  ### Bloques de sesión ###
  session_state = EstadoSesion.get(boton_login=False, boton_registro=False, log_state = False, username = "", password = "", key = 0, video_key = 0)
  ### Fin de bloques de sesión ###

  username = st.sidebar.text_input("Usuario", key = session_state.key)
  session_state.username = username
  password = st.sidebar.text_input("Contraseña", type='password', key = session_state.key)
  session_state.password = password

  boton_login = st.sidebar.button("Login")
  if boton_login or session_state.boton_login:
    session_state.boton_login = True
    result = BasesUsuarios().login_user(session_state.username,session_state.password)
    # Mostrar que hora de último acceso solo se actualiza la primera vez que entra

    if result and session_state.username != "admin":
      # Botón para cerrar sesión
      cerrar_sesion = st.sidebar.button("Cerrar sesión")
      if cerrar_sesion:
        session_state.boton_login = False
        session_state.key += 1
        rerun.rerun()   
      
      # Si es primera vez que entra, entonces debe ingresar sus datos antes de continuar

      if result[0][6] == result[0][7]:
        st.header("Formulario de datos personales")
        st.markdown(to_HTML().paragraph("Dado que es primera vez que ingresa a la Web de Capacitaciones, es necesario que ingrese sus datos personales para continuar:"), unsafe_allow_html = True)    
        new_nombre = st.text_input("Nombre:", max_chars = 35)
        new_apellido = st.text_input("Apellido:", max_chars = 35)
        new_email = st.text_input("e-mail:", max_chars = 255)
        new_last_access_date = datetime.now()
        
        if st.button("Enviar"):
          try:
            BasesUsuarios().add_user_info(session_state.username,new_nombre,new_apellido,new_email,new_last_access_date)
            st.success("Los datos se han guardado correctamente. Presiona aquí para continuar:")
            if st.button("Continuar a la página de capacitaciones"):
              rerun.rerun()
          except:
            st.warning("Por favor revise los datos ingresados.")
      
      # Si ya ha ingresado antes, entonces que continúe directamente
      else:
        if not session_state.log_state:
          BasesUsuarios().act_last_access(session_state.username,datetime.now())
          st.sidebar.success("Has iniciado sesión como {}".format(session_state.username))
          session_state.log_state = True
        
        # Aquí debería acceder a SQL a buscar nombres de proyectos para capacitación
        opciones_cap_selec = ['-- Seleccione un proyecto --','TS4 - Termómetro Social 4','EOD - Encuesta de Ocupación y Desocupación']
        cap_selec = st.sidebar.selectbox("Seleccione un proyecto:", opciones_cap_selec, index=0)
        
        if cap_selec == 'TS4 - Termómetro Social 4':
          cap_info = BasesCap().view_all_cap()
          cap1 = pd.DataFrame(cap_info,columns=["id_cap","cap_name","title","text_1","text_2","text_3"])
          st.dataframe(cap1)
          
    elif result and session_state.username == "admin":
      cerrar_sesion = st.sidebar.button("Cerrar sesión")
      if cerrar_sesion:
        session_state.boton_login = False
        session_state.key += 1
        rerun.rerun()
      if not session_state.log_state:
          BasesUsuarios().act_last_access(session_state.username,datetime.now())
          session_state.log_state = True

      st.sidebar.success("Has iniciado sesión con la cuenta de administrador")
      st.title("Administración Web Capacitaciones Centro de Microdatos")
      st.markdown(to_HTML().paragraph("Bienvenido al apartado de administración de la web de capacitaciones del Centro de Microdatos. En este apartado, podrás realizar algunas tareas importantes, como crear nuevos usuarios, y revisar la información de los usuarios actuales. Para ello, por favor selecciona la opción deseada de la lista desplegable.") , unsafe_allow_html = True)
      
      admin_options = st.selectbox(
                                   'Seleccione un área para administrar:',
                                  ('-- Área --', 'Usuarios', 'Capacitaciones'))
      
      if admin_options == "Usuarios":
        option = st.selectbox(
                              'Seleccione una acción',
                              ('-- Acción --','Crear nuevo usuario', 'Revisar información de usuarios existentes'))

        if option == "Crear nuevo usuario":
          st.header("Crear nueva cuenta")
          new_user = st.text_input("Usuario:", max_chars = 16)
          new_password = st.text_input("Contraseña:", max_chars = 16, type='password')
          if st.button("Enviar"):
            BasesUsuarios().add_user_login(new_user,new_password,datetime.now())
            st.success("La cuenta ha sido creada correctamente.")
          
        if option == "Revisar información de usuarios existentes":
          st.header("Información de usuarios existentes")
          st.markdown(to_HTML().paragraph("Estos son los usuarios actuales en la tabla Username en MySQL"), unsafe_allow_html = True)    
          login_info = BasesUsuarios().view_all_users_logininfo()
          info1 = pd.DataFrame(login_info,columns=["Username","Password"])
          st.dataframe(info1)
          st.markdown(to_HTML().paragraph("Esta es la información actual de cada usuario en la tabla Username en MySQL"), unsafe_allow_html = True)    
          username_info = BasesUsuarios().view_all_users_info()
          info2 = pd.DataFrame(username_info,columns=["Username","Nombre","Apellido","Email","Fecha de creación","Última fecha de conexión"]) 
          st.dataframe(info2)
      
      if admin_options == "Capacitaciones":
        option = st.selectbox(
                              'Seleccione una acción:',
                              ('-- Acción --', 'Crear nueva Capacitación', 'Agregar o modificar video de Capacitación'))

        if option == "Crear nueva Capacitación":
          st.header("Crear nueva Capacitación")
          new_cap = st.text_input("Clave de proyecto", max_chars = 15)
          new_cap_name = st.text_input("Nombre de proyecto", max_chars = 50)
          st.markdown(to_HTML().paragraph("Este será el nombre con el que se desplegará el proyecto a los usuarios"), unsafe_allow_html = True)
          new_title = st.text_input("Título", max_chars = 50)
          st.markdown(to_HTML().paragraph("Este será el título que se desplegará en la página de capacitación"), unsafe_allow_html = True)
          st.markdown(to_HTML().paragraph("(Opcional) Ingrese párrafos posteriores al título de la capacitación. Pueden ser una introducción al proyecto, una explicación de la capacitación, etc. No es necesario rellenar todos los campos."), unsafe_allow_html = True)
          new_text_1 = st.text_area("Texto 1")
          new_text_2 = st.text_area("Texto 2")
          new_text_3 = st.text_area("Texto 3")
          
          if st.button("Crear"):
            BasesCap().add_cap_info(new_cap,new_cap_name,new_title,new_text_1,new_text_2,new_text_3,datetime.now())
            st.success("La capacitación ha sido creada correctamente")
    
        if option == "Agregar o modificar video de Capacitación":
          st.header("Agregar o modificar video de Capacitación")
          
          # Aquí lee los proyectos actuales en SQL
          # Recupera el id y el nombre del proyecto (que será mostrado como opción)
          vid_options, id_caps = BasesCap().retrieve_cap_info()
          vid_option = st.selectbox(
                              'Seleccione un proyecto:',
                              vid_options)
          print(vid_options)
          print(id_caps)
          for i in range(1,len(vid_options)):
            if vid_option == vid_options[i]:
              print("vid option == " + str(vid_option))
              # Se conecta a comprobar si hay videos existentes ya
              # Recupera el número de videos para el id de capacitación seleccionado, el título de cada uno, y el link
              n_videos, titulos_videos, links = BasesCap().retrieve_video_info(id_caps[vid_options.index(vid_option)])

              if len(n_videos):
                st.markdown(to_HTML().paragraph("Actualmente hay {0} video{1}, cuyo{1} link{1} puede ver a continuación:".format(len(n_videos),'s' if len(n_videos)>1 else '')), unsafe_allow_html = True)
                for i in range(0,len(links)):
                  print(links)
                  st.markdown(to_HTML().paragraph("___",[("{}".format(links[i]),"Video {} - {}".format(i+1,titulos_videos[i]))], new_tab=True), unsafe_allow_html = True)                
                
                accion_video = st.radio("Seleccione la acción que desea realizar:",('Modificar un video existente','Agregar nuevo video'), key = session_state.video_key)
                if accion_video == 'Modificar un video existente':
                  st.text("Aquí irán opciones")
                if accion_video == 'Agregar nuevo video':
                  id_cap = id_caps[vid_options.index(vid_option)]
                  titulo_video = st.text_input("Título del video:")
                  orden_video = st.text_input("Número de video (determina el orden en que se mostrarán):")
                  link = st.text_input("Link del video*")
                  st.markdown(to_HTML().paragraph("(Opcional) Textos de explicación previo al video de la Capacitación."), unsafe_allow_html = True)
                  new_text_1 = st.text_area("Texto 1")
                  new_text_2 = st.text_area("Texto 2")
                  st.markdown(to_HTML().paragraph("*Para agregar un video de Youtube, se debe respetar el formato específico requerido para el link. Puedes averiguar más sobre cómo obtenerlo ___", links = [('https://help.glassdoor.com/article/Finding-the-embed-code-on-YouTube-or-Vimeo/en_US/','ingresando a este link')]), unsafe_allow_html = True)

                  if st.button("Agregar"):
                    BasesCap().add_video(id_cap,titulo_video,orden_video,link,new_text_1,new_text_2,datetime.now())
                    st.success("El video ha sido agregado correctamente. Espere mientras es redirigido")
                    time.sleep(2)
                    session_state.video_key += 1
                    rerun.rerun()

              else:
                id_cap = id_caps[vid_options.index(vid_option)]
                titulo_video = st.text_input("Título del video:")
                link = st.text_input("Link del video*")
                orden_video = st.text_input("Número de video (determina el orden en que se mostrarán):")
                st.markdown(to_HTML().paragraph("(Opcional) Textos de explicación previo al video de la Capacitación."), unsafe_allow_html = True)
                new_text_1 = st.text_area("Texto 1")
                new_text_2 = st.text_area("Texto 2")
                st.markdown(to_HTML().paragraph("*Para agregar un video de Youtube, se debe respetar el formato específico requerido para el link. Puedes averiguar más sobre cómo obtenerlo ___", links = [('https://help.glassdoor.com/article/Finding-the-embed-code-on-YouTube-or-Vimeo/en_US/','ingresando a este link')]), unsafe_allow_html = True)
                
                if st.button("Agregar"):
                  BasesCap().add_video(id_cap,titulo_video,orden_video,link,new_text_1,new_text_2,datetime.now())
                  st.success("El video ha sido agregado correctamente. Espere mientras es redirigido")
                  time.sleep(2)
                  rerun.rerun()
    else:
      if (session_state.password != "" and not result):
        st.sidebar.error('Usuario o contraseña incorrectos. Por favor intente nuevamente.')
      else:
        pass

if __name__ == '__main__':
	main()