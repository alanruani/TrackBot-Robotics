#!/usr/bin/env python

from flask import Flask, render_template, Response, request
import camera_processing
import subprocess
import atexit
import time

app = Flask(__name__)
webcam_process = None
webcam_ip = ''

@app.route('/')
def index():
	global webcam_ip
	webcam_ip = str(request.args.get('webcam_ip'))
	# webcam_ip = '192.168.0.13'
	# print()
	# print(str(webcam_ip))
	# print()
	# global webcam_process
	webcam_process = subprocess.Popen(['./prepare-videochat.sh {}'.format(webcam_ip)], shell=True)
	time.sleep(5)
	return render_template('index.html')

def gen():
	global webcam_ip
	while True:
		frame = camera_processing.process_video(ip=webcam_ip)
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
	return Response(gen(),
					mimetype='multipart/x-mixed-replace; boundary=frame')

def finish_webcam_process():
	print('finishing subprocesses')
	global webcam_process
	webcam_process.communicate(input='\n')
	webcam_process.terminate()

atexit.register(finish_webcam_process)

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)