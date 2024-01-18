from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transfer')
def transfer():
    return render_template('transfer.html')

@app.route('/pman/push', methods=['POST'])
def pmanPush():
    pass
    
@app.route('/pman/pull', methods=['POST'])
def pmanPull():
    pass

if __name__ == '__main__':
    app.run(debug=True)
