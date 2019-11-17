import email
import imaplib
from email.message import Message
from typing import List, Optional, Match
import re


class EmailReader:
    pattern = re.compile('.*(text\/plain; charset=\"UTF-8\")([^--]*)', re.DOTALL)

    def __init__(self, config: dict):

        host: str = config['smtp']['server']
        port: int = config['smtp']['port']

        self.conn: imaplib.IMAP4_SSL = imaplib.IMAP4_SSL(host, port)

        self.user: str = config['from'] + config['org']
        pwd: str = config['pwd']

        self.conn.login(self.user, pwd)
        assert self.conn.select('INBOX'), "Connection to Mail Server Failed"

    def get_unseen_mail(self) -> List[str]:
        self.conn.select('INBOX')
        retcode, messages = self.conn.search(None, f'UNSEEN (FROM "{self.user}")')
        msg_list: List[str] = []
        if retcode == "OK":
            ids: List[str] = messages[0].decode('utf-8').split()
            for _id in ids:
                typ, data = self.conn.fetch(_id, '(UID BODY[TEXT])')
                msg: Message = email.message_from_bytes(data[0][1])

                body: str = self._clean_mail(msg.get_payload(decode=True).decode())
                msg_list.append(body)
                self.conn.uid('STORE', _id, '-FLAGS', '(\Seen)')
        return msg_list

    def _clean_mail(self, body: str) -> str:
        groups: Optional[Match[str]] = self.pattern.match(body)
        if len(groups.groups()) == 2:
            return groups[2]
        return ""
