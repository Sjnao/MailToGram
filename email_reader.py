import email
import imaplib


class EmailReader:

    def __init__(self, config):

        host = config['smtp']['server']
        port = config['smtp']['port']

        self.conn = imaplib.IMAP4_SSL(host, port)

        self.user = config['from'] + config['org']
        pwd = config['pwd']

        self.conn.login(self.user, pwd)
        assert self.conn.select('INBOX'), "Connection to Mail Server Failed"

    def get_unseen_mail(self):
        retcode, messages = self.conn.search(None, f'UNSEEN (FROM "{self.user}")')
        msg_list = []
        if retcode == "OK":
            ids = messages[0].decode('utf-8').split()
            for id in ids:
                typ, data = self.conn.fetch(id, '(UID BODY[TEXT])')
                msg = email.message_from_bytes(data[0][1])
                body = msg.get_payload(decode=True)
                msg_list.append(body)
                self.conn.uid('STORE', id, '-FLAGS', '(\Seen)')
        return msg_list
