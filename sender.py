import smtplib, ssl
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

# MANDATORY REQUIREMENT
# Join with sender_email
# https://myaccount.google.com/lesssecureapps

# OPTIONAL
# python -m smtpd -c DebuggingServer -n localhost:1025

def send_mail(sender_email, password, send_to, subject, text, archive):
	smtp_server = "smtp.gmail.com"
	port = 587  # For starttls
	# Create a secure SSL context
	context = ssl.create_default_context()
	# Try to log in to server and send email
	try:
		server = smtplib.SMTP(smtp_server,port)
		server.ehlo() # Can be omitted
		server.starttls(context=context) # Secure the connection
		server.ehlo() # Can be omitted
		server.login(sender_email, password)
		msg = MIMEMultipart()
		msg['From'] = sender_email
		msg['To'] = send_to #COMMASPACE.join("wilber.cutire@ucsp.edu.pe")
		msg['Date'] = formatdate(localtime=True)
		msg['Subject'] = subject
		msg.attach(MIMEText(text))
		f = archive
		with open(f, "rb") as fil:
			part = MIMEApplication(fil.read(), Name=basename(f))
		part['Content-Disposition']='attachment; filename="%s"' % basename(f)
		msg.attach(part)
		# TODO: Send email here
		server.sendmail(sender_email, send_to, msg.as_string())
	except Exception as e:
		# Print any error messages to stdout
		print(e)
	finally:
		server.quit() 

send_mail("rvhmora@ucsp.edu.pe", "miguitarrabellaucsp1!@", "soulchicano@gmail.com", "[SCGI] Certificado", "Enviamos certificado de asistencia.", "descarga.jpg")