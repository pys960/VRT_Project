from flask import Flask, request, jsonify
from flask_cors import CORS
import imaplib
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

app = Flask(__name__)
CORS(app) # 웹앱에서 접근 가능하게 허용

def create_draft_logic(recipient, doc_type, sender_name):
    """실제로 메일을 만드는 로직 (함수화)"""
    try:
        msg = MIMEMultipart('related')
        msg['To'] = recipient
        msg['Subject'] = f"[{doc_type}] 요청하신 서류 안내드립니다."
        msg['From'] = "pys@vertexid.com"

        # HTML 본문 (가로 309, 세로 177 고정)
        html_body = f"""
        <html>
            <body style="font-family: 'Malgun Gothic', sans-serif;">
                <p>안녕하세요, <b>{sender_name}</b>입니다.</p>
                <p>요청하신 <b>{doc_type}</b> 관련하여 안내드립니다.</p>
                <p>현재 초안이 작성되었습니다. 그룹웨어에서 확인 후 발송 부탁드립니다.</p>
                <br>
                <div style="margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                    <p>감사합니다.</p>
                    <img src="cid:sig_img" width="309" height="177" style="display:block; width:309px; height:177px;">
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # 이미지 처리 (상대 경로)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(current_dir, "mail_sign.png")
        with open(img_path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<sig_img>')
            msg.attach(img)

        # IMAP 저장
        imap = imaplib.IMAP4("mail.vertexid.com", 143)
        imap.login("pys@vertexid.com", "vertex1q2w3e!") 
        imap.append("DRAFTS", '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        imap.logout()
        return True, "성공"
    except Exception as e:
        return False, str(e)

# --- 외부에서 접속하는 통로 ---
@app.route('/make-draft', methods=['POST'])
def make_draft_api():
    data = request.get_json() # 웹앱에서 보낸 데이터를 읽음
    
    success, message = create_draft_logic(
        recipient=data.get('recipient'),
        doc_type=data.get('doc_type'),
        sender_name=data.get('sender_name', '관리자')
    )

    if success:
        return jsonify({"status": "success", "message": "작성 완료"}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500

if __name__ == '__main__':
    # 서버 실행
    print("메일 작성 API 서버가 가동되었습니다!")
    app.run(host='0.0.0.0', port=5000)