from __future__ import print_function
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os
from apiclient import errors
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
CLIENT_SECRET_FILE = "client_id.json"


class EmailInteraction:
    def authorization():
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("google_email_api/token.pickle"):
            with open("google_email_api/token.pickle", "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "google_email_api/credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("google_email_api/token.pickle", "wb") as token:
                pickle.dump(creds, token)
        service = build("gmail", "v1", credentials=creds)
        return service

    def SendMessage(service, user_id, message):
        """Send an email message.

      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

      Returns:
        Sent Message.
      """
        try:
            message = (
                service.users()
                .messages()
                .send(userId=user_id, body=message)
                .execute()
            )
            print("Message Id: %s" % message["id"])
            return message
        except errors.HttpError as error:
            print("An error occurred: %s" % error)

    def CreateMessage(sender, to, subject, message_text):
        """Create a message for an email.

      Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

      Returns:
        An object containing a base64url encoded email object.
      """
        message = MIMEText(message_text)
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject
        return {
            "raw": base64.urlsafe_b64encode(
                message.as_string().encode()
            ).decode()
        }

    def CreateMessageWithAttachment(
        sender, to, subject, message_text, file_dir, filename
    ):
        """Create a message for an email.

      Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        file_dir: The directory containing the file to be attached.
        filename: The name of the file to be attached.

      Returns:
        An object containing a base64url encoded email object.
      """
        message = MIMEMultipart()
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        msg = MIMEText(message_text)
        message.attach(msg)

        for file in filename:

            path = os.path.join(file_dir, file)
            content_type, encoding = mimetypes.guess_type(path)

            if content_type is None or encoding is not None:
                content_type = "application/octet-stream"
            main_type, sub_type = content_type.split("/", 1)
            if main_type == "text":
                fp = open(path, "rb")
                msg = MIMEText(fp.read(), _subtype=sub_type)
                fp.close()
            elif main_type == "image":
                fp = open(path, "rb")
                msg = MIMEImage(fp.read(), _subtype=sub_type)
                fp.close()
            elif main_type == "audio":
                fp = open(path, "rb")
                msg = MIMEAudio(fp.read(), _subtype=sub_type)
                fp.close()
            else:
                fp = open(path, "rb")
                msg = MIMEBase(main_type, sub_type)
                msg.set_payload(fp.read())
                fp.close()

            msg.add_header("Content-Disposition", "attachment", filename=file)
            message.attach(msg)

        return {
            "raw": base64.urlsafe_b64encode(
                message.as_string().encode()
            ).decode()
        }