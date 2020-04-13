#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: le4f.net

from server import *
from server.func import *


@app.route('/')
def index():
    return redirect(url_for('upload'), 302)



@app.route('/upload',methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        CapFiles = []
        list_file(CapFiles)
        return render_template('upload.html',CapFiles=show_entries())
    elif request.method == 'POST':
        file = request.files['pcapfile']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)     
            filename = time.strftime('%Y%m%d_%H%M_',time.localtime(time.time()))+filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            size = os.path.getsize(UPLOAD_FOLDER+filename)
            result = (filename, 'PCAP', size)
            return simplejson.dumps({"files": [result]})
        else:
            pass


@app.route('/download/<id>',methods=['GET'])
def download(id):
    id = int(id)
    db = get_connection()
    pcapfile = get_pcap_entries()
    file = pcapfile[0]['filename']
    return send_file("../"+UPLOAD_FOLDER+file, attachment_filename=file, as_attachment=True)


@app.route('/analyze/<id>',methods= ["GET"])
def analyze(id):
    id = int(id)
    db = get_connection()
    pcapfile = get_pcap_entries(id)
    file = pcapfile[0]['filename']
    filter = request.args.get('filter')
    details = decode_capture_file(file,filter)
    pcapstat = get_statistics(file)
    ipsrc = get_ip_src(file)
    ipdst = get_ip_dst(file)
    dstport = get_port_dst(file)
    
    pcapstat['mail'] = get_mail(file)
    pcapstat['web'] = get_web(file)
    dns,pcapstat['dnstable'] = get_dns(file)
    pcapstat['ipsrc']=dict(ipsrc)
    pcapstat['ipdst']=dict(ipdst)
    pcapstat['dstport']=dict(dstport)
    pcapstat['dns']=dict(dns)
    try:
        return render_template('analyze.html', pcapfile = pcapfile[0], details = details , pcapstat = pcapstat)
    except:
        details = decode_capture_file(file)
        return render_template('analyze.html', pcapfile = pcapfile[0], details = details , pcapstat = pcapstat)


@app.route('/packetdetail/<id>/<num>',methods= ["GET"])
def packetdetail(id,num):
    id = int(id)
    db = get_connection()
    pcapfile = get_pcap_entries(id)
    file = pcapfile[0]['filename']
    try:
        num = int(num)
        return get_packet_detail(file, num), 200
    except:
        return 0


@app.route('/delete/<id>',methods= ["POST"])
def delete_file(id):
    delids = id.split(',')
    db = get_connection()
    for delid in delids:
        try:
            delid = int(delid)
        except:
            print 'Notice : You are being attacked.'
            exit()
        cur = db.execute('select file from pcap where id = '+ str(delid) + ';') 
        sql_exec('delete from pcap where id = '+ str(delid) +';')
        os.remove(UPLOAD_FOLDER+cur.fetchall()[0][0]);
    return 'ok'


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()
