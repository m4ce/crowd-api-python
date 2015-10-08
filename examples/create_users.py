#!/usr/bin/env python
#
# create_users.py
#
# Simple example to create users in a batch fashion
#
# Author: Matteo Cerutti <matteo.cerutti@hotmail.co.uk>
#

import os
import sys
from crowd import CrowdAPI
import logging
import jinja2
import yaml
import json
import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendmail(**mail):
  msg = MIMEMultipart('alternative')

  msg['Subject'] = mail['subject']
  msg['To'] = mail['recipient']

  if 'cc' in mail and len(mail['cc']) > 0:
    msg['Cc'] = ",".join(mail['cc'])

  if 'bcc' in mail and len(mail['bcc']) > 0:
    msg['Bcc'] = ",".join(mail['bcc'])

  recipients = mail['cc'] + mail['bcc'] + [mail['recipient']]

  try:
    body = MIMEText(mail['body'])
    msg.attach(body)
    server = smtplib.SMTP(mail['server'])
    server.sendmail(mail['sender'], recipients, msg.as_string())
    server.quit()
  except Exception, e:
    print "Failed to send email: " + str(e)

def parse_opts():
  parser = argparse.ArgumentParser(description='Crowd Tool')
  parser.add_argument("--crowd-url", action="store", dest="crowd_url", default="http://127.0.0.1/crowd", help="Crowd front-end URL (default: %(default)s)")
  parser.add_argument("--api-url", action="store", dest="api_url", default="http://127.0.0.1/crowd/rest/usermanagement/latest", help="API URL (default: %(default)s)")
  parser.add_argument("--app-name", action="store", dest="app_name", help="Application name")
  parser.add_argument("--app-password", action="store", dest="app_password", help="Application password")
  parser.add_argument("--no-ssl-verify", action="store_false", dest="ssl_verify", help="Disable SSL verification")
  parser.add_argument("--notify-email", action="store_true", default=False, dest="notify_email", help="Enable E-Mail notification upon user creation")
  parser.add_argument("--mail-sender", action="store", dest="mail_sender", default="crowd@localhost", help="E-mail sender (default: %(default))")
  parser.add_argument("--mail-recipients-cc", action="store", dest="mail_recipients_cc", help="E-mail recipients to CC (default: %(default))")
  parser.add_argument("--mail-recipients-bcc", action="store", dest="mail_recipients_bcc", help="E-mail recipients to BCC (default: %(default))")
  parser.add_argument("--mail-server", action="store", dest="mail_server", default="localhost", help="Mail server host (default: %(default))")
  parser.add_argument("--users-json", action="store", dest="users_json", help="Users JSON file")
  parser.add_argument("-c", "--config", action="store", dest="config_file", default="./crowd.yaml", help="Optional configuration file to read options from (default: %(default)s)")
  parser.add_argument("-l", "--log-level", action="store", dest="loglevel", default="INFO", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level (default: %(default)s)")
  opts = parser.parse_args()

  if os.path.isfile(opts.config_file):
    try:
      with open(opts.config_file, 'r') as stream:
        data = yaml.load(stream)
        if data is not None:
          for k, v in data.iteritems():
            setattr(opts, k, v)
    except Exception, e:
      print("Caught exception: " + str(e))
      sys.exit(1)

  if (opts.app_name is None or opts.app_password is None):
    parser.error("Application name and password are required to authenticate against Crowd")

  if opts.users_json is None:
    parser.error("Please provide a JSON file with the users definitions")

  # normalize cc and bcc
  if opts.mail_recipients_cc is None:
    opts.mail_recipients_cc = []
  else:
    opts.mail_recipients_cc = opts.mail_recipients_cc.split(',')

  if opts.mail_recipients_bcc is None:
    opts.mail_recipients_bcc = []
  else:
    opts.mail_recipients_bcc = opts.mail_recipients_bcc.split(',')

  return opts

if __name__ == "__main__":
  opts = parse_opts()

  logger = logging.getLogger("Crowd Tool")
  logger.setLevel(getattr(logging, opts.loglevel))
  console = logging.StreamHandler()
  formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s [%(filename)s:%(lineno)s]: %(message)s')
  console.setFormatter(formatter)
  logger.addHandler(console)

  crowd = CrowdAPI(**vars(opts))

  users = []

  try:
    with open(opts.users_json, 'rb') as fd:
      users = json.load(fd)
  except Exception, e:
    print "Caught exception: " + str(e)
    sys.exit(1)

  for user in users:
    # does the user exist already?
    user_req = crowd.get_user(user['name'])
    if user_req['status']:
      logger.info("User " + user['name'] + " already exists, checking group memberships")

      # get groups
      groups_req = crowd.get_user_groups(user['name'])
      if groups_req['status']:
        new = []
        for usergroup in user['groups']:
          if not usergroup in groups_req['groups']:
            # add user to group
            group_req = crowd.add_user_to_group(user['name'], usergroup)
            if group_req['status']:
              logger.info("User " + user['name'] + " added to group " + usergroup)
            else:
              logger.info("Failed to add user " + user['name'] + " to group " + usergroup + " (" + crowd_groups['reason'] + ")")
    else:
      logger.info("Creating user " + user['name'])
      create_req = crowd.create_user({"name": user['name'], "last-name": user['last-name'], "first-name": user['first-name'], "display-name": user['display-name'], "email": user['email']})
      if create_req['status']:
        if 'password' in create_req:
          user['password'] = create_req['password']

        logger.info(user)

        for usergroup in user['groups']:
          group_req = crowd.add_user_to_group(user['name'], usergroup)
          if group_req['status']:
            logger.info("User " + user['name'] + " added to group " + usergroup)
          else:
            logger.error("Failed to add user " + user['name'] + " to group " + usergroup + " (" + group_req['reason'] + ")")

        if opts.notify_email:
          logger.info("Notify user " + user['name'] + " via E-Mail")
          template_loader = jinja2.FileSystemLoader(searchpath = "./templates")
          template_env = jinja2.Environment(loader = template_loader )
          template = template_env.get_template("new_user.jinja")
          template_vars = {}
          template_vars['opts'] = opts
          template_vars['user'] = user

          sendmail(server = opts.mail_server, sender = opts.mail_sender, recipient = user['email'], cc = opts.mail_recipients_cc, bcc = opts.mail_recipients_bcc, subject =  "Crowd account setup", body = template.render(template_vars))
      else:
        logger.error("Failed to create user " + user['name'] + " (" + create_req['reason'] + ")")
