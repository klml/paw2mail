import sys, os, http.server, socketserver, json, smtplib, ssl
from json2html import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# python3 paw2mail.py 80
try:
    PORT        = int(sys.argv[1])
except:
    PORT        = 8080


def send_mail(post_body_json):

    try:
        smtp_from= os.environ['smtp_from']
        smtp_host= os.environ['smtp_host']
        smtp_port= os.environ['smtp_port']
    except:
        print("smtp setting is missing")
        return

    smtp_server=smtplib.SMTP(smtp_host, smtp_port)
    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.ehlo()
    try:
        smtp_server.login(os.environ['smtp_user'], os.environ['smtp_pass'])
    except:
        pass

    msg = MIMEMultipart('alternative')
    msg['Subject'] = post_body_json['commonLabels']['alertname']
    msg['From'] = smtp_from
    msg['To'] = post_body_json['commonLabels']['paw2mail']

    json_html = json2html.convert(json = post_body_json, table_attributes="style=\"border:1px solid #CCCCCC;\"")

    msg_text = MIMEText( str( post_body_json ), 'plain' )
    msg_html = MIMEText( str( json_html ), 'html' )

    msg.attach(msg_text)
    msg.attach(msg_html)

    smtp_server.sendmail(smtp_from, msg['To'] , str(msg))
    smtp_server.quit()

    return


class paw2mail(http.server.SimpleHTTPRequestHandler):

    def _set_headers(self):
        self.send_header('Content-type', 'text/html')
        self.send_header('Strict-Transport-Security', 'max-age=31536000')
        self.send_header('Content-Security-Policy', "script-src 'self'")
        self.send_header('Allow', 'POST')
        self.end_headers()

    def do_POST(self):
        try :
            content_length  = int(self.headers['Content-Length'])
            post_body       = str(self.rfile.read(content_length).decode('utf-8'))

            if self.path == "/paw2mail" :
                send_mail( json.loads( post_body ) )
                self.send_response(200)
                self._set_headers()
            raise Exception()
        except:
            self.send_error(404) # 404 Not Found
            self._set_headers()
            return

    def do_GET(self):
            self.send_error(405) # 405 Method Not Allowed
            self._set_headers()
            return

with socketserver.TCPServer(("", PORT), paw2mail) as httpd:
    print("Http Server Serving at port", PORT)
    httpd.serve_forever()