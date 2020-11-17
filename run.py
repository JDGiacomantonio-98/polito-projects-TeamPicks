from app import create_app
from config import set_config

app = create_app(config=set_config())

if __name__ == '__main__':
	app.run()
