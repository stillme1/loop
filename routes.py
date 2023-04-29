import datetime
from flask import Flask, jsonify, send_file
import threading

import query as query
import util as util
from const import ROOTPATH

app = Flask(__name__)

# generate report API
@app.route('/generate_report', methods=['POST'])
def generate_report():
    # print current time
    print(datetime.datetime.now())
    # generate report id
    report_id = query.addReport("running")

    # start report generation asynchronously
    thread = threading.Thread(target=util.generate_report, args=(report_id,))
    thread.start()

    # return report id to client
    return jsonify({'reportId': report_id})

# get report API
@app.route('/get_report/<string:report_id>', methods=['GET'])
def get_report(report_id):
    # check if report exists
    status = query.getReportStatus(report_id)
    if status != "done":
        return jsonify({'status': status})

    # generate csv response
    report_path = f'{ROOTPATH}/{report_id}.csv'
    response = send_file(report_path, as_attachment=True, mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename={report_id}.csv'
    return response

if __name__ == '__main__':
    app.run()
