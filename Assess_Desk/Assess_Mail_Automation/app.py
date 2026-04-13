from flask import Flask, request, jsonify
from flask_cors import CORS
import imaplib
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# --- 1. 플라스크 웹 서버 초기 세팅 ---
app = Flask(__name__)
CORS(app)

# --- 2. 메일 작성 핵심 로직 ---
def create_draft_logic(recipient, cc, subject):
    try:
        msg = MIMEMultipart('related')
        msg['To'] = recipient
        msg['Cc'] = cc # 참조자 추가
        msg['Subject'] = subject # 시트에서 받아온 제목 사용
        msg['From'] = "pys@vertexid.com"

        # 요청하신 서식, 공백, 표를 HTML로 완벽히 구현했습니다.
        html_body = f"""
        <html>
            <body style="font-family: 'Malgun Gothic', sans-serif; font-size: 10pt; color: black;">
                <br>
                <br>
                안녕하세요 버텍스아이디 박영석입니다.<br>
                <br>
                {subject} 송부드립니다.<br>
                <br>
                <br>
                <span style="color: blue; font-weight: bold;">소견서 및 견적서 요청 외 다른 문의</span>는 아래 연락처로 부탁드립니다.<br>
                <br>
                <table border="1" style="border-collapse: collapse; text-align: center; width: 350px; font-size: 10pt;">
                    <tr>
                        <th colspan="2" style="padding: 5px; font-weight: bold;">버텍스아이디 박용욱 실장</th>
                    </tr>
                    <tr>
                        <td style="padding: 5px; width: 30%;">Phone</td>
                        <td style="padding: 5px;">010-9914-7460</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;">E-mail</td>
                        <td style="padding: 5px;">pyw@vertexid.com</td>
                    </tr>
                </table>
                <br>
                <br>
                감사합니다.<br>
                <br>
                <br>
                <br>
                <br>
                <img src="cid:sig_img" width="309" height="177" style="display:block; width:309px; height:177px; border:none;">
            </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # 이미지 첨부 로직
        current_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(current_dir, "mail_sign.png")
        with open(img_path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<sig_img>')
            msg.attach(img)

        # IMAP 서버 접속 및 저장
        imap = imaplib.IMAP4("mail.vertexid.com", 143)
        imap.login("pys@vertexid.com", "vertex1q2w3e!") 
        imap.append("DRAFTS", '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        imap.logout()
        return True, "성공"
    except Exception as e:
        return False, str(e)

# --- 3. 외부 API 수신 창구 ---
@app.route('/make-draft', methods=['POST'])
def make_draft_api():
    data = request.get_json()
    
    # 웹앱에서 보내준 3가지 핵심 데이터를 받습니다.
    success, message = create_draft_logic(
        recipient=data.get('recipient', ''),
        cc=data.get('cc', ''),
        subject=data.get('subject', '소견서 안내')
    )

    if success:
        return jsonify({"status": "success", "message": "작성 완료"}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500

# --- 4. 서버 실행 엔진 (이 부분이 있어야 Render가 켜집니다) ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
