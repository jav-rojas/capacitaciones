import base64
import csv
import mysql.connector
import numpy as np
import pandas as pd
import streamlit as st
import time
from io import StringIO
from os import path
from datetime import datetime
from modules import EstadoSesion
from modules import rerun
from modules.Utilidades import to_HTML
from modules.ConexionBases import Conexion, BasesUsuarios, BasesCap, BasesUserCap
from modules.batch_upload import IntegrityErrors, Batch


def main():
    st.beta_set_page_config(
        page_title="Capacitaciones CMD",
        page_icon="https://pbs.twimg.com/profile_images/1161359420967784449/Hsgy0Zv2.jpg",
        layout='centered',
        initial_sidebar_state='auto')

    st.set_option('deprecation.showfileUploaderEncoding', False)

    # Bloques de sesión #
    session_state = EstadoSesion.get(
        boton_login=False,
        boton_registro=False,
        log_state=False,
        username="",
        password="",
        key=0,
        video_key=0,
        cap_key=0,
        user_option=0)
    # Fin de bloques de sesión #

    username = st.sidebar.text_input("Usuario", key=session_state.key)
    session_state.username = username
    password = st.sidebar.text_input("Contraseña", type='password', key=session_state.key)
    session_state.password = password

    boton_login = st.sidebar.button("Login")
    if boton_login or session_state.boton_login:
        session_state.boton_login = True
        result = BasesUsuarios().login_user(session_state.username, session_state.password)
        # Hora de último acceso se actualiza la primera vez que entra

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
                st.markdown(to_HTML().paragraph("Dado que es primera vez que ingresa a la Web de Capacitaciones, es necesario que ingrese sus "
                                                "datos personales para continuar:"),
                            unsafe_allow_html=True)

                new_nombre = st.text_input("Nombre:", max_chars=35)
                new_apellido = st.text_input("Apellido:", max_chars=35)
                new_email = st.text_input("e-mail:", max_chars=255)
                new_last_access_date = datetime.now()

                if st.button("Enviar"):
                    try:
                        BasesUsuarios().add_user_info(session_state.username, new_nombre, new_apellido, new_email, new_last_access_date)
                        st.success("Los datos se han guardado correctamente. Presiona aquí para continuar:")
                        if st.button("Continuar a la página de capacitaciones"):
                            rerun.rerun()
                    except Exception:
                        st.warning("Por favor revise los datos ingresados.")

            # Si ya ha ingresado antes, entonces que continúe directamente
            else:
                if not session_state.log_state:
                    BasesUsuarios().act_last_access(session_state.username, datetime.now())
                    st.sidebar.success("Has iniciado sesión como {}".format(session_state.username))
                    session_state.log_state = True

                # Aquí debería acceder a SQL a buscar nombres de proyectos para capacitación
                opciones_cap_selec = ['-- Seleccione un proyecto --', 'TS4 - Termómetro Social 4', 'EOD - Encuesta de Ocupación y Desocupación']
                cap_selec = st.sidebar.selectbox("Seleccione un proyecto:", opciones_cap_selec, index=0)

                if cap_selec == 'TS4 - Termómetro Social 4':
                    cap_info = BasesCap().view_all_cap()
                    cap1 = pd.DataFrame(cap_info, columns=["id_cap", "cap_name", "title", "text_1", "text_2", "text_3"])
                    st.dataframe(cap1)

        elif result and session_state.username == "admin":
            cerrar_sesion = st.sidebar.button("Cerrar sesión")
            if cerrar_sesion:
                session_state.boton_login = False
                session_state.key += 1
                rerun.rerun()

            if not session_state.log_state:
                BasesUsuarios().act_last_access(session_state.username, datetime.now())
                session_state.log_state = True

            st.sidebar.success("Has iniciado sesión con la cuenta de administrador")
            st.title("Administración Web Capacitaciones Centro de Microdatos")
            st.markdown(to_HTML().paragraph("Bienvenido al apartado de administración de la web de capacitaciones del Centro de Microdatos. "
                                            "En este apartado, podrás realizar algunas tareas importantes, como crear nuevos usuarios, y "
                                            "revisar la información de los usuarios actuales. Para ello, por favor selecciona la opción "
                                            "deseada de la lista desplegable."), unsafe_allow_html=True)

            admin_options = st.selectbox(
                'Seleccione un área para administrar:',
                ('-- Área --', 'Usuarios', 'Capacitaciones'))

            if admin_options == "Usuarios":
                option = st.selectbox(
                    'Seleccione una acción',
                    ('-- Acción --', 'Crear nuevo usuario', 'Cargar usuarios por lote', 'Revisar información de usuarios existentes'), index=session_state.user_option)

                if option == "Crear nuevo usuario":
                    st.header("Crear nueva cuenta")
                    new_user = st.text_input("Usuario:", max_chars=16)
                    new_password = st.text_input("Contraseña:", max_chars=16, type='password')
                    if st.button("Enviar"):
                        BasesUsuarios().add_user_login(new_user, new_password, datetime.now())
                        st.success("La cuenta ha sido creada correctamente.")

                if option == "Revisar información de usuarios existentes":
                    st.header("Información de usuarios existentes")
                    st.markdown(to_HTML().paragraph("Estos son los usuarios actuales en la tabla Username en MySQL"), unsafe_allow_html=True)
                    login_info = BasesUsuarios().view_all_users_logininfo()
                    info1 = pd.DataFrame(login_info, columns=["Username", "Password"])
                    st.dataframe(info1)
                    st.markdown(to_HTML().paragraph("Esta es la información actual de cada usuario en la tabla Username en MySQL"), unsafe_allow_html=True)
                    username_info = BasesUsuarios().view_all_users_info()
                    info2 = pd.DataFrame(username_info, columns=["Username", "Nombre", "Apellido", "Email", "Fecha de creación", "Última fecha de conexión"])
                    st.dataframe(info2)

                if option == "Cargar usuarios por lote":
                    st.header("Carga de usuarios por lote")

                    st.markdown(to_HTML().paragraph("La carga de usuarios por lote permite la utilización de un archivo separado por comas (.csv) para crear "
                                                    "usuarios automáticamente dentro de la plataforma. Además, es posible asociarlos inmediatamente a una "
                                                    "capacitación, con el único requisito de que esta ya esté creada."),
                                unsafe_allow_html=True)
                    st.markdown(to_HTML().paragraph("Para cargar usuarios masivamente, siga los siguientes pasos:"), unsafe_allow_html=True)

                    # Genera archivo para descarga
                    data = open(path.join('files', 'users_schema.csv'), "r", encoding='utf-8-sig').read()
                    b64 = base64.b64encode(data.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="users_schema.csv">la siguiente plantilla</a>'

                    # Lista de capacitaciones disponibles
                    elements = BasesCap().retrieve_cap_info(key=True, elements=True)
                    caps = to_HTML().list(elements=elements)

                    st.markdown(to_HTML().list(elements=[
                                "Descargue {}. Puede ser editada con Excel o cualquier editor de texto.".format(href),
                                "Rellene las columnas deseadas. Si solo está creando usuarios, las columnas <em>usuario</em> y <em>password</em> no pueden tener valores vacíos. "
                                "Si carga capacitaciones a un usuario ya existente, las columnas <em>password</em>, <em>nombre</em>, <em>apellido</em> y <em>mail</em> serán ignoradas.",
                                "(Opcional) Para asociar los usuarios a una capacitación específica, agregue una columna con el nombre <em>_cap</em>. "
                                "El valor de la columna <em>_cap</em> deberá ser uno de los siguientes: {}".format(caps),
                                "Cargue el archivo (arrastrando o utilizando el cuadro de diálogo más abajo)",
                                "Compruebe que el archivo se ha cargado correctamente. Debería poder visualizar el archivo, y comprobar que las columnas son las deseadas.",
                                "Presione el botón 'Cargar'.",
                                "Si no es redirigido automáticamente, compruebe que los usuarios se han cargado correctamente seleccionando "
                                "Usuarios > Revisar información de usuarios existentes"], ordered=True),
                                unsafe_allow_html=True)

                    # Genera widget para subir archivo
                    uploaded_file = st.file_uploader('Seleccione un archivo CSV', type='csv')

                    if uploaded_file is not None:
                        # Lee contenido del archivo, lo almacanea como StringIO. Genera un segundo objeto para ser utilizado posteriormente (una vez utilizado, desaparece)
                        uploaded_file_df = StringIO(uploaded_file.read())
                        uploaded_file_data = StringIO(uploaded_file_df.getvalue())

                        if uploaded_file_df is not None:
                            df = pd.read_csv(uploaded_file_df, delimiter=';')

                            # Reemplaza valores nan por '' para mostrar en página
                            df.loc[df['usuario'].isna(), 'usuario'] = ''
                            df.loc[df['password'].isna(), 'password'] = ''
                            df.loc[df['nombre'].isna(), 'nombre'] = ''
                            df.loc[df['apellido'].isna(), 'apellido'] = ''
                            df.loc[df['email'].isna(), 'email'] = ''

                            # Variables para identificar columna _cap
                            has_cap = False  # True si tiene columna _cap
                            check_cap = pd.DataFrame  # DF utilizado si tiene columna _cap

                            if '_cap' in df.columns:
                                df.loc[df['_cap'].isna(), '_cap'] = ''
                                has_cap = True

                            st.write(df)

                            # Chequeos sobre archivo .csv (integrity checks antes de SQL)
                            integrity = IntegrityErrors(has_cap=has_cap, df=df)

                            # Muestra error si es que hay combinaciones que no pueden estar repetidas
                            repeated = integrity.repeated()
                            if repeated:
                                st.subheader("Error: Hay filas con información repetida incompatible ({})".format(len(repeated)))
                                for i in range(len(repeated)):
                                    if has_cap:
                                        st.error("La combinación usuario-capacitación está repetida en el archivo para {}-{}".format(repeated[i][0], repeated[i][1]))
                                    else:
                                        st.error("El usuario {} está repetido en el archivo".format(repeated[i][0]))

                            # Permite mostrar otros errores sí y sólo sí no hay valores repetidos
                            if not repeated:
                                # Muestra error si es que no hay columna de capacitación y un usuario ya existe
                                exists_username = integrity.user_exists()
                                if exists_username:
                                    st.subheader("Error: Hay usuarios que ya existen ({})".format(len(exists_username)))
                                    for i in range(len(exists_username)):
                                        st.error("El usuario {} ya existe".format(exists_username[i]))

                                # Muestra error si es que hay valores vacíos en columnas 'usuario' o 'password'
                                check_usuario, check_password = integrity.userpass_empty()
                                if check_usuario:
                                    st.subheader("Error: Hay valores vacíos en la columna 'usuario' ({})".format(len(check_usuario)))
                                if check_password:
                                    st.subheader("Error: Hay valores vacíos en la columna 'password' ({})".format(len(check_password)))
                                    for i in range(len(check_password)):
                                        st.error("El usuario {} no puede tener la columna 'password' en blanco".format(check_password[i]))

                                # Muestra error si es que tiene la columna _cap, y hay valores vacíos en ella
                                check_cap = integrity.cap_empty()
                                if check_cap:
                                    st.subheader("Error: Hay valores vacíos en la columna '_cap' ({})".format(len(check_cap)))
                                    st.error("No pueden existir valores vacíos en la columna _cap")

                                # Muestra error si es que tiene la columna _cap, pero ese key_name no existe en la base actual
                                invalid_keynames = integrity.invalid_keyname()
                                if invalid_keynames:
                                    st.subheader("Error: Hay capacitaciones en la columna _cap que no existen o no han sido creadas ({})".format(len(invalid_keynames)))
                                    for i in range(len(invalid_keynames)):
                                        st.error("La capacitación {} no existe o no ha sido creada".format(invalid_keynames[i]))

                                # Muestra advertencia si es que hay combinaciones usuario-capacitación que ya existen
                                exists_usertraining = integrity.usertraining_exists()
                                if exists_usertraining:
                                    st.subheader("Error: Hay usuarios que ya tienen la capacitación asignada ({})".format(len(exists_usertraining)))
                                    for i in range(len(exists_usertraining)):
                                        st.error("El usuario {} ya tiene asociada la capacitación {}".format(exists_usertraining[i][0], exists_usertraining[i][1]))

                                if not check_usuario and not check_password and not check_cap and not invalid_keynames and not exists_usertraining:
                                    if st.button("Cargar"):
                                        if has_cap:
                                            exists, not_exists = Batch(has_cap, df).batch_users()
                                            if exists:
                                                exists_cap = list(df.loc[df['usuario'].isin(exists), ['usuario', '_cap']].itertuples(index=False, name=None))
                                                print(exists_cap)
                                            if not_exists:
                                                not_exists_login = list(df.loc[df['usuario'].isin(not_exists), ['usuario', 'password', 'nombre', 'apellido', 'email']].itertuples(index=False, name=None))
                                                not_exists_cap = list(df.loc[df['usuario'].isin(not_exists), ['usuario', '_cap']].itertuples(index=False, name=None))
                                                print(not_exists_login)
                                                print(not_exists_cap)

            if admin_options == "Capacitaciones":
                option = st.selectbox(
                    'Seleccione una acción:',
                    ('-- Acción --', 'Crear nueva Capacitación', 'Agregar o modificar video de Capacitación'), key=session_state.cap_key)

                if option == "Crear nueva Capacitación":
                    st.header("Crear nueva Capacitación")
                    new_cap = st.text_input("Clave de proyecto", max_chars=15)
                    new_cap_name = st.text_input("Nombre de proyecto", max_chars=50)
                    st.markdown(to_HTML().paragraph("Este será el nombre con el que se desplegará el proyecto a los usuarios"), unsafe_allow_html=True)
                    new_title = st.text_input("Título", max_chars=50)
                    st.markdown(to_HTML().paragraph("Este será el título que se desplegará en la página de capacitación"), unsafe_allow_html=True)
                    st.markdown(to_HTML().paragraph("(Opcional) Ingrese párrafos posteriores al título de la capacitación. "
                                                    "Pueden ser una introducción al proyecto, una explicación de la capacitación, etc. "
                                                    "No es necesario rellenar todos los campos."), unsafe_allow_html=True)
                    new_text_1 = st.text_area("Texto 1")
                    new_text_2 = st.text_area("Texto 2")
                    new_text_3 = st.text_area("Texto 3")

                    if st.button("Crear"):
                        BasesCap().add_cap_info(new_cap, new_cap_name, new_title, new_text_1, new_text_2, new_text_3, datetime.now())
                        st.success("La capacitación ha sido creada correctamente. Espere mientras es redirigido.")
                        time.sleep(1.5)
                        session_state.cap_key += 1
                        rerun.rerun()

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
                    for i in range(1, len(vid_options)):
                        if vid_option == vid_options[i]:
                            print("vid option == " + str(vid_option))
                            # Se conecta a comprobar si hay videos existentes ya
                            # Recupera el número de videos para el id de capacitación seleccionado, el título de cada uno, y el link
                            n_videos, titulos_videos, links = BasesCap().retrieve_video_info(id_caps[vid_options.index(vid_option)])

                            if len(n_videos):
                                st.markdown(to_HTML().paragraph(
                                            "Actualmente hay {0} video{1}, cuyo{1} link{1} puede ver a continuación:".format(len(n_videos), 's' if len(n_videos) > 1 else '')),
                                            unsafe_allow_html=True)

                                for i in range(0, len(links)):
                                    print(links)
                                    st.markdown(to_HTML().paragraph(
                                        "___", [
                                            ("{}".format(links[i]), "Video {} - {}".format(i + 1, titulos_videos[i]))], new_tab=True),
                                        unsafe_allow_html=True)

                                accion_video = st.radio(
                                    "Seleccione la acción que desea realizar:",
                                    ('Modificar un video existente', 'Agregar nuevo video'),
                                    key=session_state.video_key)

                                if accion_video == 'Modificar un video existente':
                                    st.text("Aquí irán opciones")
                                if accion_video == 'Agregar nuevo video':
                                    id_cap = id_caps[vid_options.index(vid_option)]
                                    titulo_video = st.text_input("Título del video:")
                                    orden_video = st.text_input("Número de video (determina el orden en que se mostrarán):")
                                    link = st.text_input("Link del video*")
                                    st.markdown(to_HTML().paragraph("(Opcional) Textos de explicación previo al video de la Capacitación."), unsafe_allow_html=True)
                                    new_text_1 = st.text_area("Texto 1")
                                    new_text_2 = st.text_area("Texto 2")
                                    st.markdown(to_HTML().paragraph("*Para agregar un video de Youtube, se debe respetar el formato específico "
                                                                    "requerido para el link. Puedes averiguar más sobre cómo obtenerlo ___",
                                                links=[('https://help.glassdoor.com/article/Finding-the-embed-code-on-YouTube-or-Vimeo/en_US/', 'ingresando a este link')]),
                                                unsafe_allow_html=True)

                                    if st.button("Agregar"):
                                        BasesCap().add_video(id_cap, titulo_video, orden_video, link, new_text_1, new_text_2, datetime.now())
                                        st.success("El video ha sido agregado correctamente. Espere mientras es redirigido")
                                        time.sleep(2)
                                        session_state.video_key += 1
                                        rerun.rerun()

                            else:
                                id_cap = id_caps[vid_options.index(vid_option)]
                                titulo_video = st.text_input("Título del video:")
                                link = st.text_input("Link del video*")
                                orden_video = st.text_input("Número de video (determina el orden en que se mostrarán):")
                                st.markdown(to_HTML().paragraph("(Opcional) Textos de explicación previo al video de la Capacitación."), unsafe_allow_html=True)
                                new_text_1 = st.text_area("Texto 1")
                                new_text_2 = st.text_area("Texto 2")
                                st.markdown(to_HTML().paragraph("*Para agregar un video de Youtube, se debe respetar el formato específico "
                                                                "requerido para el link. Puedes averiguar más sobre cómo obtenerlo ___",
                                            links=[('https://help.glassdoor.com/article/Finding-the-embed-code-on-YouTube-or-Vimeo/en_US/', 'ingresando a este link')]),
                                            unsafe_allow_html=True)

                            if st.button("Agregar"):
                                BasesCap().add_video(id_cap, titulo_video, orden_video, link, new_text_1, new_text_2, datetime.now())
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
