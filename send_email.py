import smtplib
from email.mime.text import MIMEText


def send_email(getter, message, subject="IRaMFan"):
    sender = "1ramfanbot@gmail.com"
    password = "987654asdvbn"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        msg = MIMEText(message)
        msg["Subject"] = subject
        server.sendmail(sender, getter, msg.as_string())

        return "OK"
    except Exception as ex:
        return ex


def main():
    getter = input("Type getter: ")
    message = input("Type your message: ")
    print(send_email(getter, message))


if __name__ == '__main__':
    main()
