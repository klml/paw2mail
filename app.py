import os, logging, http.server, socketserver, json, smtplib, ssl
from json2html import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

if os.environ.get('port') is not None:
    PORT        = int(os.environ['port'])
else:
    PORT        = 8080


def create_smtp_server():

    try:
        smtp_from= os.environ['smtp_from']
        smtp_host= os.environ['smtp_host']
        smtp_port= os.environ['smtp_port']
    except:
        logging.error('smtp setting is missing')
        return

    smtp_server=smtplib.SMTP(smtp_host, smtp_port)
    smtp_server.ehlo()
    try:
        smtp_server.login(os.environ['smtp_user'], os.environ['smtp_pass'])
    except:
        pass

    return smtp_server, smtp_from


def send_mail(post_body_json, smtp_server, smtp_from):

    msg = MIMEMultipart('alternative')
    msg['Subject'] = post_body_json['commonLabels']['alertname']
    msg['From'] = smtp_from
    try:
        msg['To'] = post_body_json['commonLabels']['paw2mail']
    except:
        return "no paw2mail"

    json_html = json2html.convert(json = post_body_json, table_attributes="style=\"border:1px solid #CCCCCC;\"")

    msg_text = MIMEText( str( post_body_json ), 'plain' )
    msg_html = MIMEText( str( json_html ), 'html' )

    msg.attach(msg_text)
    msg.attach(msg_html)

    smtp_server.sendmail(smtp_from, msg['To'] , str(msg))
    smtp_server.quit()

    return "mail send"


class paw2mail(http.server.SimpleHTTPRequestHandler):

    def _set_headers(self):
        self.send_header('Content-type', 'text/html')
        self.send_header('Strict-Transport-Security', 'max-age=31536000')
        self.send_header('Content-Security-Policy', "script-src 'self'")
        self.send_header('Allow', 'POST')
        self.end_headers()

    def do_POST(self):
        if self.path == "/paw2mail" :


            try:
                content_length  = int(self.headers['Content-Length'])
                post_body       = str(self.rfile.read(content_length).decode('utf-8'))
                smtp_server, smtp_from = create_smtp_server()
                mailsend = send_mail( json.loads( post_body ), smtp_server, smtp_from)
                self.send_response(200)
                self._set_headers()
                self.wfile.write(mailsend.encode("utf-8"))
                return

            except:
                self.send_error(500) # Internal Server Error
                self._set_headers()
                return

        else:
            self.send_error(404) # 404 Not Found
            self._set_headers()
            return

    def do_GET(self):
            self.send_error(405) # 405 Method Not Allowed
            self._set_headers()
            return

with socketserver.TCPServer(("", PORT), paw2mail) as httpd:
    if create_smtp_server() != None: # test smtp_server
        print("Http Server Serving at port", PORT)
        httpd.serve_forever()
