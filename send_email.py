import mailtrap

token="fdf92a477ae866bf54e396effeb9c72a"

def email(to,subject,message):
    mail=mailtrap.Mail(
        sender=mailtrap.Address(email="hello@demomailtrap.co",name="FLASK_API"),
        to=[mailtrap.Address(email=to)],
        subject=subject,
        text=message,
        category="mailtrap integration test"
    )
    client=mailtrap.MailtrapClient(token=token)
    response=client.send(mail)

    print("this is mailtrap------------------------------------------")
    print(response)

# email("mitchellewanjohi69@gmail.com","Testing API","testing my API")