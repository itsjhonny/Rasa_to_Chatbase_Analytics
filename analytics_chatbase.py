import pymysql
import json
import threading
from chatbase_menssage import ChatBaseMessage
from datetime import datetime


class AnalyticsChatBase:
    def __init__(self, data_config):
        self.data_config = data_config
        self.bot_confidence = 0.4

        self.api_key = data_config['api_key']
        self.api_platform = data_config['api_platform']
        self.api_version = data_config['api_version']

        self.database_last_id_sanded = data_config['last_id_sanded']

        self.mensages = []

    def get_from_database(self, connection):
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM events WHERE id > %s"
                cursor.execute(sql, (self.database_last_id_sanded,))
                result = cursor.fetchall()
                if result is not None:
                    for row in result:
                        if row['type_name'] == 'bot':

                            try:
                                #self.send_kibana_bot(row)
                                self.send_chat_base_bot(row)
                            except EOFError as e:
                                print('error_database_bot: {0}'.format(e))

                        elif row['type_name'] == 'user':
                            try:
                                #self.send_kibana_user(row)
                                self.send_chat_base_user(row)
                            except EOFError as e:
                                print('error_database_user: {0}'.format(e))

                        else:
                            pass

                cursor.close()

        except pymysql.MySQLError as e:
            print('Error get_from_Database Cursos')
            print(e)
        finally:
            print('last_id {0}'.format(self.database_last_id_sanded))

            connection.close()
            self.save_last_id()

    def save_last_id(self):
        # self.data_config['last_id_sanded'] = self.database_last_id_sanded
        self.data_config['last_id_sanded'] = 7000

        with open('src/chatbase/config.json', "w") as f:
            json.dump(self.data_config, f, indent=4, sort_keys=True)

        f.close()

        with open('src/chatbase/mensagens.json', "w", encoding='utf-8') as f:
            json.dump(self.mensages, f, ensure_ascii=False,
                      indent=4)

        f.close()

    def send_kibana_bot(self, data):

        in_json_data = json.loads(data['data'])

        msg = {
            "type": 'agent',
            "timestamp": self.transforme_timestamp_to_date(in_json_data['timestamp']),
            "user_id": data['sender_id'],
            "message": in_json_data['text']
        }

        self.mensages.append(msg)
        self.database_last_id_sanded = data['id']

    def send_chat_base_bot(self, data):

        in_json_data = json.loads(data['data'])

        ChatBaseMessage(
            api_key=self.api_key,
            platform=self.api_platform,
            version=self.api_version,
            type='agent',
            time_stamp=in_json_data['timestamp'],
            user_id=data['sender_id'],
            message=in_json_data['text']
        ).send()

        self.database_last_id_sanded = data['id']

        # print('BOT: {0}'.format(resp))

    def send_kibana_user(self, data):
        in_json_data = json.loads(data['data'])

        confidence = in_json_data['parse_data']['intent']['confidence']
        confidence = float(confidence) <= self.bot_confidence

        msg = {
            "type": data['type_name'],
            "timestamp": self.transforme_timestamp_to_date(in_json_data['timestamp']),
            "user_id": data['sender_id'],
            "intent_name": data['intent_name'],
            "not_handled": confidence,
            "message": in_json_data['text'],
        }

        self.mensages.append(msg)
        self.database_last_id_sanded = data['id']

    def send_chat_base_user(self, data):
        in_json_data = json.loads(data['data'])

        confidence = in_json_data['parse_data']['intent']['confidence']
        confidence = float(confidence) <= self.bot_confidence

        ChatBaseMessage(
            api_key=self.api_key,
            platform=self.api_platform,
            version=self.api_version,
            type=data['type_name'],
            time_stamp=in_json_data['timestamp'],
            user_id=data['sender_id'],
            message=in_json_data['text'],
            intent=data['intent_name'],
            not_handled=confidence
        ).send()

        self.database_last_id_sanded = data['id']

        print('\n USER: {0} \n Confidence: {1} \n MSG: {2} \n'.format(
            data['sender_id'], in_json_data['parse_data']['intent']['confidence'], in_json_data['text']))

    def transforme_timestamp_to_date(self, timestamp):
        time_stamp = int(timestamp)

        return datetime.utcfromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')


def connect_database(data_config):
    try:
        database_host = data_config['database_host']
        database_user = data_config['database_user']
        database_password = data_config['database_password']
        database_db = data_config['database_db']
        database_charset = data_config['database_charset']

        connection = pymysql.connect(host=database_host,
                                     user=database_user,
                                     password=database_password,
                                     db=database_db,
                                     charset=database_charset,
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection
    except pymysql.MySQLError as e:
        print(e)
        return e


def start_chatbase():
    config_file = open('src/chatbase/config.json', )
    data_config = json.load(config_file)
    config_file.close()

    analytics_chat_base = AnalyticsChatBase(data_config)
    connection = connect_database(data_config)
    analytics_chat_base.get_from_database(connection)

    time = 60 * 30
    # threading.Timer(time, start_chatbase).start()


def main():
    print(' ---- Inicializando Analytics_chatbase.py ---- \n')
    start_chatbase()


if __name__ == "__main__":
    main()
