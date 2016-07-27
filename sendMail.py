import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
# from email.header import Header
import csv
import configparser
from datetime import datetime


class InvalidConfigException(Exception):
    """invalid configure or some errors found."""
    def __init__(self, errinfo: str):
        self.info = errinfo


# column A, Index 0;column B, Index 1; and so on
def addrListFromCSV(csvname, colindex):
    maillist = []
    with open(csvname, 'r', newline='') as cf:
        reader = csv.reader(cf)
        for row in reader:
            addr = row[colindex]
            if addr.count('@') == 1:
                maillist.append(row[colindex])
            else:
                print("Skip Invalid Email Address:", addr)
    print(len(maillist), "Valid Email Address Read From CSV")
    return maillist


def loadSenderConfig(configfile):
    senders = []
    config = configparser.ConfigParser()
    config.read(configfile)
    for section in config.sections():
        cdic = config[section]
        sender = {'type': cdic['server_type'], 'host': cdic['server_host'], 'port': cdic['server_port'],
                  'auth': cdic['server_auth'], 'addr': cdic['sender_addr'], 'pass': cdic['sender_passwd'],
                  'max': cdic['day_max']}
        senders.append(sender)
    print(len(senders), "Sender Config Read")
    return senders


def loadGlobalConfig(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    if 'global' in config.sections():
        g = config['global']
        gcfg = {'subject': g['mail_subject'], 'text': g['mail_text'], 'attach': g['mail_attach'], 'csv': g['target_csv'],
                'senders': g['sender_config']}
        return gcfg
    else:
        raise InvalidConfigException("No 'global' section!")


def logFailedAddress(addrs):
    with open('failed.log', 'a') as log:
        dt = datetime.now()
        log.write('\n------{0} [{1}]------\n'.format(dt, len(addrs)))
        log.write('\n'.join(addrs))
        log.write('\n------{0} [{1}]------\n'.format(dt, len(addrs)))


def sendMail(sender, addrlist, subject, textfile='', attach=''):
    if '' == textfile and '' == attach:
        print("No Mail Content at All!")
        return

    mail = MIMEMultipart()
    mail['Subject'] = subject
    mail['From'] = sender['addr']
    # mail['To'] = ';'.join(addrlist)

    if '' != textfile:
        with open(textfile, 'r') as tf:
            mail.attach(MIMEText(tf.read()))
    else:
        print("No Text Content Assigned")

    if '' != attach:
        with open(attach, 'rb') as af:
            part = MIMEBase('application', 'octet-stream', filename=attach)
            part.add_header('Content-Disposition', 'attachment', filename=attach)
            part.add_header('Content-ID', '<0>')
            part.add_header('X-Attachment-Id', '0')
            part.set_payload(af.read())
            encoders.encode_base64(part)
            mail.attach(part)
    else:
        print('No Attachment Assigned')
    msg = mail.as_string()

    sendcount = 0
    s = smtplib.SMTP()
    try:
        s.connect(sender['host'], int(sender['port']))
        print('Connect Server {0}:{1} OK'.format(sender['host'], sender['port']))
        if sender['auth'] == 'TLS':
            print('Starting TLS...')
            s.starttls()
            s.ehlo()
            print('Start TLS Mode OK')
        s.login(sender['addr'], sender['pass'])
        print('User', sender['addr'], 'Login OK')
        for addr in addrlist:
            s.sendmail(sender['addr'], addr, msg)
            sendcount += 1
        # print('Send Mail OK!')
        s.quit()
    except Exception as ex:
        print('Error:'+str(ex))
    finally:
        print("Finish!Send Count:", sendcount)
        logFailedAddress(addrlist[sendcount:])
        # s.quit()


globalconfig = loadGlobalConfig('sendmail.ini')
print(globalconfig)
tolist = addrListFromCSV(globalconfig['csv'], 0)
print(tolist)
senders = loadSenderConfig(globalconfig['senders'])
print(senders)
for sender in senders:
    sendMail(sender, tolist, globalconfig['subject'], globalconfig['text'], globalconfig['attach'])
