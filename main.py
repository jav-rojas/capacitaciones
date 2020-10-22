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
        training_key=0,
        update_training_key=0,
        delete_training_key=0,
        video_key=0,
        update_video_key=0,
        delete_video_key=0,
        question_key=0,
        update_question_key=0,
        delete_question_key=0,
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
                st.markdown(to_HTML().paragraph("Dado que es primera vez que ingresa a la Web de Capacitaciones, es necesario que confirme sus "
                                                "información personal antes de continuar. Si ya existe algún valor asignado, puede modificarlo "
                                                "antes de enviar los datos al sistema."),
                            unsafe_allow_html=True)

                new_nombre = st.text_input("Nombre:", value='{}'.format(result[0][3] if result[0][3] is not None else ''), max_chars=35)
                new_apellido = st.text_input("Apellido:", value='{}'.format(result[0][3] if result[0][4] is not None else ''), max_chars=35)
                new_email = st.text_input("e-mail:", value='{}'.format(result[0][3] if result[0][5] is not None else ''), max_chars=255)
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
                training_options, training_ids = BasesUserCap().retrieve_associated_trainings(username=session_state.username)
                training_option = st.sidebar.selectbox('Seleccione un proyecto:', training_options)
                for i in range(1, len(training_options)):
                    if training_option == training_options[i]:
                        st.text(training_option)
                        st.text(training_ids[training_options.index(training_option)])

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
                    elements = BasesCap().retrieve_training_info(key=True, elements=True)
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
                                    st.subheader("Error: Hay capacitaciones en la columna '_cap' que no existen o no han sido creadas ({})".format(len(invalid_keynames)))
                                    for i in range(len(invalid_keynames)):
                                        st.error("La capacitación {} no existe o no ha sido creada".format(invalid_keynames[i]))

                                # Muestra advertencia si es que hay combinaciones usuario-capacitación que ya existen
                                exists_usertraining = integrity.usertraining_exists()
                                if exists_usertraining:
                                    st.subheader("Error: Hay usuarios que ya poseen la capacitación que se busca asignar ({})".format(len(exists_usertraining)))
                                    for i in range(len(exists_usertraining)):
                                        st.error("El usuario {} ya tiene asociada la capacitación {}".format(exists_usertraining[i][0], exists_usertraining[i][1]))

                                if not check_usuario and not check_password and not check_cap and not invalid_keynames and not exists_usertraining:
                                    if st.button("Cargar"):
                                        if has_cap:
                                            exists, not_exists = Batch(has_cap, df).batch_users()
                                            if exists:
                                                exists_cap = list(df.loc[df['usuario'].isin(exists), ['usuario', '_cap']].itertuples(index=False, name=None))
                                                BasesUserCap().add_usertraining(input_tuple=exists_cap, tuples=True)
                                            if not_exists:
                                                not_exists_login = list(df.loc[df['usuario'].isin(not_exists), ['usuario', 'password', 'nombre', 'apellido', 'email']].itertuples(index=False, name=None))
                                                BasesUsuarios().add_batch_users(input_tuple=not_exists_login, created_at=datetime.now())
                                                not_exists_cap = list(df.loc[df['usuario'].isin(not_exists), ['usuario', '_cap']].itertuples(index=False, name=None))
                                                BasesUserCap().add_usertraining(input_tuple=not_exists_cap, tuples=True)

            if admin_options == "Capacitaciones":
                option = st.selectbox(
                    'Seleccione una acción:',
                    ('-- Acción --', 'Agregar, modificar o eliminar Capacitación', 'Agregar, modificar o eliminar video de Capacitación', 'Agregar, modificar o eliminar cuestionario en video de Capacitación'),
                    key=session_state.training_key)

                if option == "Agregar, modificar o eliminar Capacitación":
                    st.header("Agregar, modificar o eliminar Capacitación")
                    training_ids, training_key_names, training_names = BasesCap().retrieve_training_info(info=True)

                    if len(training_ids):
                        training_titles = ["{} - {}".format(training_key_names[i], training_names[i]) for i in range(len(training_key_names))]
                        training_actions = ['-- Seleccione acción --', 'Agregar Capacitación', 'Modificar o actualizar Capacitación', 'Eliminar Capacitación']
                        training_action = st.selectbox(
                            "Seleccione la acción que desea realizar:", training_actions, key=session_state.training_key, index=0)

                        if training_action == 'Agregar Capacitación':
                            st.subheader('Agregue una nueva Capacitación:')
                            training_key_name = st.text_input("Clave de proyecto")
                            training_name = st.text_input("Nombre de proyecto")
                            st.markdown(to_HTML().paragraph("El nombre con el que se desplegará el proyecto es 'clave - nombre'"), unsafe_allow_html=True)
                            training_title = st.text_input("Título")
                            st.markdown(to_HTML().paragraph("Este será el título que se desplegará en la página de capacitación"), unsafe_allow_html=True)
                            st.markdown(to_HTML().paragraph("(Opcional) Ingrese párrafos posteriores al título de la capacitación. "
                                                            "Pueden ser una introducción al proyecto, una explicación de la capacitación, etc. "
                                                            "No es necesario rellenar todos los campos."), unsafe_allow_html=True)
                            training_text1 = st.text_area("Texto 1")
                            training_text2 = st.text_area("Texto 2")
                            training_text3 = st.text_area("Texto 3")

                            if st.button("Crear"):
                                BasesCap().add_training(training_key_name, training_name, training_title, training_text1, training_text2, training_text3, datetime.now())
                                st.success("La capacitación ha sido creada correctamente. Espere mientras es redirigido.")
                                time.sleep(1)
                                session_state.training_key += 1
                                rerun.rerun()

                        if training_action == 'Modificar o actualizar Capacitación':
                            training_options = ['-- Seleccione una Capacitación --'] + training_titles
                            training_option = st.selectbox("Seleccione la Capacitación a modificar o actualizar:", training_options, key=session_state.update_training_key, index=0)

                            for i in range(len(training_titles)):
                                if training_option == training_titles[i]:
                                    training = BasesCap().retrieve_training(id=training_ids[i])
                                    st.subheader('Modifique o actualice la información de la Capacitación seleccionada:')
                                    training_key_name = st.text_input("Clave de proyecto:", value='{}'.format(training[0] if training[0] is not None else ''))
                                    training_name = st.text_input("Nombre de proyectp:", value='{}'.format(training[1] if training[1] is not None else ''))
                                    training_title = st.text_input("Título:", value='{}'.format(training[2] if training[2] is not None else ''))
                                    training_text1 = st.text_area("Texto 1:", value='{}'.format(training[3] if training[3] is not None else ''))
                                    training_text2 = st.text_area("Texto 2:", value='{}'.format(training[4] if training[4] is not None else ''))
                                    training_text3 = st.text_area("Texto 3:", value='{}'.format(training[5] if training[5] is not None else ''))

                                    if st.button("Modificar"):
                                        BasesCap().update_training(
                                            id=training_ids[i],
                                            training_key_name=training_key_name,
                                            training_name=training_name,
                                            training_title=training_title,
                                            training_text1=training_text1,
                                            training_text2=training_text2,
                                            training_text3=training_text3,
                                            updated_at=datetime.now())
                                        st.success("La Capacitación ha sido modificado correctamente. Espere mientras es redirigido")
                                        time.sleep(1)
                                        session_state.update_training_key += 1
                                        rerun.rerun()

                        if training_action == 'Eliminar Capacitación':
                            training_options = ['-- Seleccione una Capacitación --'] + training_titles
                            training_option = st.selectbox("Seleccione la Capacitación a eliminar:", training_options, key=session_state.delete_training_key, index=0)
                            for i in range(len(training_titles)):
                                if training_option == training_titles[i]:
                                    st.subheader('¿Está seguro que desea eliminar esta Capacitación?')
                                    st.markdown(to_HTML().paragraph('La información de los videos y preguntas asociadas a esta Capacitación también serán eliminados. Recuerde que esta acción es permanente y no puede deshacerse.'), unsafe_allow_html=True)
                                    st.markdown(to_HTML().paragraph('Para confirmar, presione el botón "Eliminar".'), unsafe_allow_html=True)
                                    if st.button("Eliminar"):
                                        BasesCap().delete_training(id=training_ids[i])
                                        st.success("La capacitación ha sido eliminada correctamente. Espere mientras es redirigido")
                                        time.sleep(1)
                                        session_state.delete_training_key += 1
                                        rerun.rerun()

                    else:
                        training_key_name = st.text_input("Clave de proyecto", max_chars=15)
                        training_name = st.text_input("Nombre de proyecto", max_chars=50)
                        st.markdown(to_HTML().paragraph("El nombre con el que se desplegará el proyecto es 'clave - nombre'"), unsafe_allow_html=True)
                        training_title = st.text_input("Título", max_chars=50)
                        st.markdown(to_HTML().paragraph("Este será el título que se desplegará en la página de capacitación"), unsafe_allow_html=True)
                        st.markdown(to_HTML().paragraph("(Opcional) Ingrese párrafos posteriores al título de la capacitación. "
                                                        "Pueden ser una introducción al proyecto, una explicación de la capacitación, etc. "
                                                        "No es necesario rellenar todos los campos."), unsafe_allow_html=True)
                        training_text1 = st.text_area("Texto 1")
                        training_text2 = st.text_area("Texto 2")
                        training_text3 = st.text_area("Texto 3")

                        if st.button("Crear"):
                            BasesCap().add_training(training_key_name, training_name, training_title, training_text1, training_text2, training_text3, datetime.now())
                            st.success("La capacitación ha sido creada correctamente. Espere mientras es redirigido.")
                            time.sleep(1)
                            session_state.training_key += 1
                            rerun.rerun()

                if option == "Agregar, modificar o eliminar video de Capacitación":
                    st.header("Agregar, modificar o eliminar video de Capacitación")

                    # Aquí lee los proyectos actuales en SQL
                    # Recupera el id y el nombre del proyecto (que será mostrado como opción)
                    training_options, training_ids = BasesCap().retrieve_training_info()
                    training_option = st.selectbox('Seleccione un proyecto:', training_options)

                    for i in range(1, len(training_options)):
                        if training_option == training_options[i]:
                            # Se conecta a comprobar si hay videos existentes ya
                            # Recupera el número de videos para el id de capacitación seleccionado, el título de cada uno, y el link
                            video_ids, video_titles, video_links, orden = BasesCap().retrieve_video_info(training_ids[training_options.index(training_option)])

                            if len(video_ids):
                                st.markdown(to_HTML().paragraph(
                                            "Actualmente hay {0} video{1}, cuyo{1} link{1} puede ver a continuación:".format(len(video_ids), 's' if len(video_ids) > 1 else '')),
                                            unsafe_allow_html=True)

                                for i in range(0, len(video_links)):
                                    st.markdown(to_HTML().paragraph(
                                        "___", [("{}".format(video_links[i]), "Video {} - {}".format(orden[i], video_titles[i]))], new_tab=True),
                                        unsafe_allow_html=True)

                                video_actions = ['-- Seleccione acción --', 'Agregar video', 'Modificar o actualizar video', 'Eliminar video']
                                video_action = st.selectbox(
                                    "Seleccione la acción que desea realizar:", video_actions, key=session_state.video_key, index=0)

                                if video_action == 'Agregar video':
                                    st.subheader('Agregue un nuevo video:')
                                    training_id = training_ids[training_options.index(training_option)]
                                    video_title = st.text_input("Título del video:")
                                    video_link = st.text_input("Link del video*:")
                                    orden = st.text_input("Número de video (determina el orden en que se mostrarán):")
                                    st.markdown(to_HTML().paragraph("(Opcional) Textos de explicación previo al video de la Capacitación:"), unsafe_allow_html=True)
                                    video_text1 = st.text_area("Texto 1:")
                                    video_text2 = st.text_area("Texto 2:")
                                    st.markdown(to_HTML().paragraph("*Para agregar un video de Youtube, se debe respetar el formato específico "
                                                                    "requerido para el link. Puedes averiguar más sobre cómo obtenerlo ___",
                                                links=[('https://help.glassdoor.com/article/Finding-the-embed-code-on-YouTube-or-Vimeo/en_US/', 'ingresando a este link')]),
                                                unsafe_allow_html=True)

                                    if st.button("Agregar"):
                                        BasesCap().add_video(training_id, video_title, video_link, orden, video_text1, video_text2, datetime.now())
                                        st.success("El video ha sido agregado correctamente. Espere mientras es redirigido")
                                        time.sleep(1)
                                        session_state.video_key += 1
                                        rerun.rerun()

                                if video_action == 'Modificar o actualizar video':
                                    video_options = ['-- Seleccione un video --'] + video_titles
                                    video_option = st.selectbox("Seleccione el video a modificar o actualizar:", video_options, key=session_state.update_video_key, index=0)
                                    for i in range(len(video_titles)):
                                        if video_option == video_titles[i]:
                                            video = BasesCap().retrieve_video(id=video_ids[i])
                                            st.subheader('Modifique o actualice la información del video seleccionado:')
                                            titulo_video = st.text_input("Título del video:", value='{}'.format(video[0] if video[0] is not None else ''))
                                            orden_video = st.text_input("Número de video (determina el orden en que se mostrarán)*:", value='{}'.format(video[1] if video[1] is not None else ''))
                                            link = st.text_input("Link del video**:", value='{}'.format(video[2] if video[2] is not None else ''))
                                            text_1 = st.text_area("Texto 1:", value='{}'.format(video[3] if video[3] is not None else ''))
                                            text_2 = st.text_area("Texto 2:", value='{}'.format(video[4] if video[4] is not None else ''))
                                            st.markdown(to_HTML().paragraph(
                                                "*Recuerde que el orden debe ser único. Si modifica este valor a uno ya existente, debe borrar "
                                                "o actualizar el video afectado."),
                                                unsafe_allow_html=True)
                                            st.markdown(to_HTML().paragraph(
                                                "**Para agregar un video de Youtube, se debe respetar el formato específico "
                                                "requerido para el link. Puedes averiguar más sobre cómo obtenerlo ___",
                                                links=[('https://help.glassdoor.com/article/Finding-the-embed-code-on-YouTube-or-Vimeo/en_US/', 'ingresando a este link')]),
                                                unsafe_allow_html=True)

                                            if st.button("Modificar"):
                                                BasesCap().update_video(
                                                    id=video_ids[i],
                                                    video_title=titulo_video,
                                                    video_link=link,
                                                    orden=orden_video,
                                                    video_text1=text_1,
                                                    video_text2=text_2,
                                                    updated_at=datetime.now())
                                                st.success("El video ha sido modificado correctamente. Espere mientras es redirigido")
                                                time.sleep(1)
                                                session_state.update_video_key += 1
                                                rerun.rerun()

                                if video_action == 'Eliminar video':
                                    video_options = ['-- Seleccione un video --'] + video_titles
                                    video_option = st.selectbox("Seleccione el video a eliminar:", video_options, key=session_state.delete_video_key, index=0)
                                    for i in range(len(video_titles)):
                                        if video_option == video_titles[i]:
                                            st.subheader('¿Está seguro que desea eliminar este video?')
                                            st.markdown(to_HTML().paragraph('Las preguntas asociadas a este video también serán eliminadas. Recuerde que esta acción es permanente y no puede deshacerse. Para confirmar, presione el botón "Eliminar".'), unsafe_allow_html=True)
                                            if st.button("Eliminar"):
                                                BasesCap().delete_video(id=video_ids[i])
                                                st.success("El video ha sido eliminado correctamente. Espere mientras es redirigido")
                                                time.sleep(1)
                                                session_state.delete_video_key += 1
                                                rerun.rerun()

                            else:
                                training_id = training_ids[training_options.index(training_option)]
                                video_title = st.text_input("Título del video:")
                                video_link = st.text_input("Link del video*")
                                orden = st.text_input("Número de video (determina el orden en que se mostrarán):")
                                st.markdown(to_HTML().paragraph("(Opcional) Textos de explicación previo al video de la Capacitación."), unsafe_allow_html=True)
                                video_text1 = st.text_area("Texto 1")
                                video_text2 = st.text_area("Texto 2")
                                st.markdown(to_HTML().paragraph("*Para agregar un video de Youtube, se debe respetar el formato específico "
                                                                "requerido para el link. Puedes averiguar más sobre cómo obtenerlo ___",
                                            links=[('https://help.glassdoor.com/article/Finding-the-embed-code-on-YouTube-or-Vimeo/en_US/', 'ingresando a este link')]),
                                            unsafe_allow_html=True)

                                if st.button("Agregar"):
                                    BasesCap().add_video(training_id, video_title, video_link, order, video_text1, video_text2, datetime.now())
                                    st.success("El video ha sido agregado correctamente. Espere mientras es redirigido")
                                    time.sleep(1)
                                    rerun.rerun()

                if option == "Agregar, modificar o eliminar pregunta en video de Capacitación":
                    st.header("Agregar, modificar o eliminar pregunta en video de Capacitación")

                    # Recupera el id y el nombre del proyecto (que será mostrado como opción)
                    training_options, training_ids = BasesCap().retrieve_training_info()
                    training_option = st.selectbox('Seleccione un proyecto:', training_options)
                    for i in range(1, len(training_options)):
                        if training_option == training_options[i]:
                            video_ids, video_titles, video_links, orden = BasesCap().retrieve_video_info(training_ids[training_options.index(training_option)])
                            if len(video_ids):
                                video_options = ['-- Seleccione un video --'] + video_titles
                                video_option = st.selectbox("Seleccione un video:", video_options, key=session_state.update_video_key, index=0)
                                for i in range(len(video_titles)):
                                    if video_option == video_titles[i]:
                                        question_ids, question_titles = BasesCap().retrieve_question_info(
                                            training_id=training_ids[training_options.index(training_option)],
                                            trainingvideo_id=video_ids[i])

                                        if len(question_ids):
                                            question_actions = ['-- Seleccione acción --', 'Agregar pregunta', 'Modificar o actualizar pregunta', 'Eliminar pregunta']
                                            question_action = st.selectbox(
                                                "Seleccione la acción que desea realizar:", question_actions, key=session_state.question_key, index=0)

                                            if question_action == 'Agregar pregunta':
                                                st.subheader('Agregue una nueva pregunta:')
                                                training_id = training_ids[training_options.index(training_option)]
                                                trainingvideo_id = video_ids[i]
                                                question_types = ['Texto', 'Selección única', 'Selección múltiple']
                                                question_type = st.radio("Seleccione el tipo de pregunta:", question_types)

                                                if question_type == 'Texto':
                                                    question_title = st.text_input("Título o enunciado de la pregunta")

                                                    if st.button("Agregar"):
                                                        BasesCap().add_question(
                                                            training_id=training_id,
                                                            trainingvideo_id=trainingvideo_id,
                                                            question_type=question_type,
                                                            question_title=question_title,
                                                            created_at=datetime.now())
                                                        st.success("La pregunta ha sido agregado correctamente. Espere mientras es redirigido")
                                                        time.sleep(1)
                                                        session_state.question_key += 1
                                                        rerun.rerun()

                                                else:
                                                    question_title = st.text_input("Título o enunciado de la pregunta")
                                                    question_choice1 = st.text_input("Ingrese Alternativa 1:")
                                                    question_choice2 = st.text_input("Ingrese Alternativa 2:")
                                                    question_choice3 = st.text_input("(Opcional) Ingrese Alternativa 3:")
                                                    question_choice4 = st.text_input("(Opcional) Ingrese Alternativa 4:")

                                                    if st.button("Agregar"):
                                                        if question_choice1 == '':
                                                            st.error("Alternativa 1 no puede estar vacía.")
                                                        if question_choice2 == '':
                                                            st.error("Alternativa 2 no puede estar vacía")
                                                        if question_choice1 != '' and question_choice2 != '':
                                                            BasesCap().add_question(
                                                                training_id, trainingvideo_id, question_type, question_title,
                                                                question_choice1, question_choice2, question_choice3, question_choice4, datetime.now())
                                                            st.success("La pregunta ha sido agregado correctamente. Espere mientras es redirigido")
                                                            time.sleep(1)
                                                            rerun.rerun()

                                            if question_action == 'Modificar o actualizar pregunta':
                                                question_options = ['-- Seleccione un video --'] + question_titles
                                                question_option = st.selectbox("Seleccione la pregunta a modificar o actualizar:", question_options, key=session_state.update_question_key, index=0)

                                                for i in range(len(question_titles)):
                                                    if question_option == question_titles[i]:
                                                        question = BasesCap().retrieve_question(id=question_ids[i])
                                                        st.subheader('Modifique o actualice la información de la pregunta seleccionada:')
                                                        question_types = ['Texto', 'Selección única', 'Selección múltiple']
                                                        question_type = st.radio("Seleccione el tipo de pregunta:", question_types, index=question_types.index('{}'.format(question[0])))
                                                        if question_type == 'Texto':
                                                            question_title = st.text_input("Título o enunciado de la pregunta", value='{}'.format(question[1]))
                                                            if st.button("Modificar"):
                                                                BasesCap().update_question(
                                                                    id=question_ids[i],
                                                                    question_type=question_type,
                                                                    question_title=question_title,
                                                                    updated_at=datetime.now())
                                                                st.success("La pregunta ha sido modificada correctamente. Espere mientras es redirigido")
                                                                time.sleep(1)
                                                                session_state.update_question_key += 1
                                                                rerun.rerun()
                                                        else:
                                                            question_title = st.text_input("Título o enunciado de la pregunta", value='{}'.format(question[1]))
                                                            question_choice1 = st.text_input("Ingrese Alternativa 1:", value='{}'.format(question[2] if question[2] is not None else ''))
                                                            question_choice2 = st.text_input("Ingrese Alternativa 2:", value='{}'.format(question[3] if question[3] is not None else ''))
                                                            question_choice3 = st.text_input("(Opcional) Ingrese Alternativa 3:", value='{}'.format(question[4] if question[4] is not None else ''))
                                                            question_choice4 = st.text_input("(Opcional) Ingrese Alternativa 4:", value='{}'.format(question[5] if question[5] is not None else ''))

                                                            if st.button("Modificar"):
                                                                if question_choice1 == '':
                                                                    st.error("Alternativa 1 no puede estar vacía.")
                                                                if question_choice2 == '':
                                                                    st.error("Alternativa 2 no puede estar vacía")
                                                                if question_choice1 != '' and question_choice2 != '':
                                                                    BasesCap().update_question(
                                                                        id=question_ids[i],
                                                                        question_type=question_type,
                                                                        question_title=question_title,
                                                                        question_choice1=question_choice1,
                                                                        question_choice2=question_choice2,
                                                                        question_choice3=question_choice3,
                                                                        question_choice4=question_choice4,
                                                                        updated_at=datetime.now())
                                                                    st.success("La pregunta ha sido modificada correctamente. Espere mientras es redirigido")
                                                                    time.sleep(1)
                                                                    session_state.update_question_key += 1
                                                                    rerun.rerun()

                                            if question_action == 'Eliminar pregunta':
                                                question_options = ['-- Seleccione una pregunta --'] + question_titles
                                                question_option = st.selectbox("Seleccione la pregunta a eliminar:", question_options, key=session_state.delete_question_key, index=0)
                                                for i in range(len(question_titles)):
                                                    if question_option == question_titles[i]:
                                                        st.subheader('¿Está seguro que desea eliminar esta pregunta?')
                                                        st.markdown(to_HTML().paragraph('Esta acción es permanente y no puede deshacerse. Para confirmar, presione el botón "Eliminar".'), unsafe_allow_html=True)
                                                        if st.button("Eliminar"):
                                                            BasesCap().delete_question(id=question_ids[i])
                                                            st.success("La pregunta ha sido eliminada correctamente. Espere mientras es redirigido")
                                                            time.sleep(1)
                                                            session_state.delete_video_key += 1
                                                            rerun.rerun()

                                        else:
                                            training_id = training_ids[training_options.index(training_option)]
                                            trainingvideo_id = video_ids[i]
                                            question_types = ['Texto', 'Selección única', 'Selección múltiple']
                                            question_type = st.radio("Seleccione el tipo de pregunta:", question_types)
                                            if question_type == 'Texto':
                                                question_title = st.text_input("Título o enunciado de la pregunta")

                                                if st.button("Agregar"):
                                                    BasesCap().add_question(
                                                        training_id=training_id,
                                                        trainingvideo_id=trainingvideo_id,
                                                        question_type=question_type,
                                                        question_title=question_title,
                                                        created_at=datetime.now())
                                                    st.success("La pregunta ha sido agregado correctamente. Espere mientras es redirigido")
                                                    time.sleep(1)
                                                    rerun.rerun()
                                            else:
                                                question_title = st.text_input("Título o enunciado de la pregunta")
                                                question_choice1 = st.text_input("Ingrese Alternativa 1:")
                                                question_choice2 = st.text_input("Ingrese Alternativa 2:")
                                                question_choice3 = st.text_input("(Opcional) Ingrese Alternativa 3:")
                                                question_choice4 = st.text_input("(Opcional) Ingrese Alternativa 4:")

                                                if st.button("Agregar"):
                                                    if question_choice1 == '':
                                                        st.error("Alternativa 1 no puede estar vacía.")
                                                    if question_choice2 == '':
                                                        st.error("Alternativa 2 no puede estar vacía")
                                                    if question_choice1 != '' and question_choice2 != '':
                                                        BasesCap().add_question(
                                                            training_id, trainingvideo_id, question_type, question_title,
                                                            question_choice1, question_choice2, question_choice3, question_choice4, datetime.now())
                                                        st.success("La pregunta ha sido agregado correctamente. Espere mientras es redirigido")
                                                        time.sleep(1)
                                                        rerun.rerun()

                            else:
                                st.warning("Para utilizar esta opción, debe agregar al menos un video a la Capacitación.")

        else:
            if (session_state.password != "" and not result):
                st.sidebar.error('Usuario o contraseña incorrectos. Por favor intente nuevamente.')
            else:
                pass


if __name__ == '__main__':
    main()
