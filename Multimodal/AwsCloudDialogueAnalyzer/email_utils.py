def construct_email_body_html(urls_dict):
    email_body = """
    <html>
        <head>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; color: #333; background-color: #f4f4f4; }
                .container { max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
                h2 { color: #0366d6; text-align: center; }
                .link-title { margin-top: 20px; padding: 10px; background-color: #e9e9e9; border-left: 5px solid #0366d6; font-size: 18px; }
                .graph-link { text-decoration: none; color: #333; font-weight: bold; }
                .graph-link:hover { color: #0366d6; }
                .footer { margin-top: 30px; text-align: center; font-size: 14px; color: #666; }
            </style>
        </head>
        <body>
            <div class='container'>
                <h2>AI Conference WhatsApp Dialogues</h2>
    """
    for file_key, url in urls_dict.items():
        email_body += f"""
                <div class='link-title'>
                    <a href='{url}' class='graph-link' target='_blank'>{file_key.replace('_', ' ').title()}</a>
                </div>
        """
    email_body += """
                <div class='footer'>
                    <p>AOI Emre Turan - All rights reserved © 2024</p>
                </div>
            </div>
        </body>
    </html>
    """
    return email_body

def send_email(ses_client, sender, recipient, subject, body):
    response = ses_client.send_email(
        Source=sender,
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Html': {'Data': body}}
        }
    )
    return response
