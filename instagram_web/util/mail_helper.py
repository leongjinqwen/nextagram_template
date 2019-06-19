from instagram_web import sg
import os
from sendgrid.helpers.mail import *
from flask_login import current_user

def send_pay_email(receiver,amount):
    #when payment is success, send email to inform both donor and receiver
    from_email = Email("leongjinqwen@gmail.com")
    to_email = Email(receiver.email)
    if receiver==current_user :
        subject = "Thank you from Nextagram!"
        content = Content("text/html", f"<h1>Dear {receiver.username},</h1><br/>Thank you very much for your recent donation of {amount} USD.<br/><br/><h1>NEXTAGRAM</h1>")
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)
    else:
        subject = "You got donation on your Nextagram photo!"
        content = Content("text/html", f"<h1>Dear {receiver.username},</h1><br/>You got a donation of {amount} USD on your photo. Go to your donation summary to check for the details.<br/>Keep going and post more awesome photos! <br/><br/><h1>NEXTAGRAM</h1>")
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)

def reset_password_email(user,user_password):
    from_email = Email("leongjinqwen@gmail.com")
    to_email = Email("leongjinqwen@gmail.com")
    subject = "Reset your password"
    content = Content("text/html", f"<h1>Dear {user.username},</h1><br/>Here is your temporary password <h4>{user_password}</h4>Remember to update it after login to your account.<br/><br/><h1>NEXTAGRAM</h1>")
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
    



