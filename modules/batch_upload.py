from .ConexionBases import BasesUsuarios, BasesCap, BasesUserCap


class IntegrityErrors():

    def __init__(self, has_cap, df):
        self.has_cap = has_cap
        self.df = df

    def repeated(self):
        if self.has_cap:
            self.repeated_list = list(self.df.loc[:, ['usuario', '_cap']].itertuples(index=False, name=None))
            self.repeated_list = list(set([x for x in self.repeated_list if self.repeated_list.count(x) > 1]))
        else:
            self.repeated_list = list(self.df.loc[:, ['usuario']].itertuples(index=False, name=None))
            self.repeated_list = list(set([x for x in self.repeated_list if self.repeated_list.count(x) > 1]))
        return self.repeated_list

    def user_exists(self):
        if not self.has_cap:
            # Recupera información de login de usuarios (usuario y contraseña)
            self.login_info = BasesUsuarios().view_all_users_logininfo()
            # Crea conjunto de usuarios a partir de la información recuperada de SQL
            self.usernames = set([self.login_info[i][0] for i in range(len(self.login_info))])
            # Crea conjunto de usuarios a partir de la información del archivo csv
            self.usernames_csv = set(self.df.usuario.values.tolist())
            # Crea una lista de usuarios que están en archivo csv y que ya existen en SQL
            self.exists_username = list(self.usernames & self.usernames_csv)
            return self.exists_username
        else:
            return False

    def userpass_empty(self):
        self.login_info = BasesUsuarios().view_all_users_logininfo()
        self.usernames = set([self.login_info[i][0] for i in range(len(self.login_info))])
        self.usernames_csv = set(self.df.usuario.values.tolist())
        self.not_exists_username = list(self.usernames_csv - self.usernames)
        # Busca si existen valores vacíos en usuario
        self.check_usuario = self.df.loc[self.df['usuario'] == '', :]
        self.check_usuario = self.check_usuario.usuario.values.tolist()
        # Busca si existen valores vacíos en password para usuarios que no existen
        self.check_password = self.df.loc[(self.df['password'] == '') & (self.df['usuario'].isin(self.not_exists_username)), :]
        self.check_password = self.check_password.usuario.values.tolist()
        return self.check_usuario, self.check_password

    def cap_empty(self):
        if self.has_cap:
            self.check_cap = self.df.loc[self.df['_cap'] == '', :]
            self.check_cap = self.check_cap.usuario.values.tolist()
            return self.check_cap
        else:
            return False

    def invalid_keyname(self):
        if self.has_cap:
            self.key_name, self.name = BasesCap().retrieve_cap_info(key=True)
            self.csv_key_names = set(self.df['_cap'].values.tolist())
            self.invalid_keynames = list(self.csv_key_names - set(self.key_name))
            self.invalid_keynames = [i for i in self.invalid_keynames if i]
            return self.invalid_keynames
        else:
            return False

    def usertraining_exists(self):
        if self.has_cap:
            self.username_training = set(BasesUserCap().retrieve_usertraining_info())
            self.username_training_csv = self.df.loc[:, ['usuario', '_cap']]
            self.username_training_csv = set(list(self.username_training_csv.itertuples(index=False, name=None)))
            self.exists_usertraining = list(self.username_training & self.username_training_csv)
            return self.exists_usertraining
        else:
            return False


class Batch():

    def __init__(self, has_cap, df):
        self.has_cap = has_cap
        self.df = df

    def batch_users(self):
        self.login_info = BasesUsuarios().view_all_users_logininfo()
        # Crea conjunto de usuarios a partir de la información recuperada de SQL
        self.usernames = set([self.login_info[i][0] for i in range(len(self.login_info))])
        # Crea conjunto de usuarios a partir de la información del archivo csv
        self.usernames_csv = set(self.df.usuario.values.tolist())
        # Crea una lista de usuarios que están en archivo csv y que ya existen en SQL
        self.exists_username = list(self.usernames & self.usernames_csv)
        # Crea una lista de usuarios que están en archivo csv y que no existen en SQL
        self.not_exists_username = list(self.usernames_csv - self.usernames)
        return self.exists_username, self.not_exists_username
