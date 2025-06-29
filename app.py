### app.py
from flask import Flask, redirect
from customer import create_customer_dashboard
from transaction import create_trans_dashboard

# Create Flask server\ nserver = Flask(__name__)
server = Flask(__name__)
# Mount each Dash app
create_customer_dashboard(server)
create_trans_dashboard(server)

@server.route('/')
def index():
    return redirect('/customer/')

if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=5000)