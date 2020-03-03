from flask import Flask, request, render_template, redirect, url_for, flash
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from BrachioGraph.linedraw import vectorise
from threading import Thread

import os

app = Flask(__name__)
app.secret_key = 'drawingbot'
socketio = SocketIO(app)
step = -1
file_to_convert = ''

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
thread = Thread()


class DrawThread(Thread):
    """Draw routine thread based on basic Thread class """

    def __init__(self):
        """init """
        self.file = ''
        super(DrawThread, self).__init__()


    def doPrintStuff(self):
        try:
            # while True:
            print('FINISHED CONVERTING TO SVG')

            print(UPLOAD_FOLDER + '/' + self.file)
            lines = vectorise(UPLOAD_FOLDER + '/' + self.file, resolution=800, draw_contours=True, contour_simplify=1)
            print('FINISHED CONVERTING TO SVG')

            os.system('gcodeplot/gcodeplot.py ' + UPLOAD_FOLDER + '/' + self.file + '.svg > 5.ngc')
            print('FINISHED CONVERTING TO GCODE')

            os.system('python serial_read.py')
            print('FINISHED CONVERTING TO DRAWING')

        except TypeError as e:
            print(e)
        except (KeyboardInterrupt):
            pass

    def run(self):
        self.doPrintStuff()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@socketio.on('drawgcode')
def handle_send(data):
    #ser.on_send(data['img'])
    print('GOT THE MESSAGE')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print("sdf")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_to_convert = filename
            global thread
            thread = DrawThread()
            thread.file = file_to_convert
            thread.start()


    return '''
    <!doctype html>
    <title>Upload new File</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type="file" name="file" accept="image/*"/>
      <input type=submit value=Upload>
      
    </form>
    '''



if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0', port=7000)