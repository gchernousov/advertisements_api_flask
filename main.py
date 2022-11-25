from flask import Flask
from views import check


app = Flask('advert_app')

app.add_url_rule('/check/', view_func=check, methods=['GET'])


if __name__ == "__main__":

    app.run()