from os import environ

# If you're looking at this file it should mean 1 of 2 things:
# 1) Pure Curiousity - Congratulations!
# 2) Confirmation of the necessary credentials and other required singletons exist within the app context
SMTP_CREDENTIALS = {
    "host": environ.get("hostname"),
    "port": environ.get("port"),
    "username": environ.get("username"),
    "password": environ.get("password"),
}
