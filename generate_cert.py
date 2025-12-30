from OpenSSL import crypto
import os

def generate_self_signed_cert():
    # 鍵ペアを生成
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    # 証明書を生成
    cert = crypto.X509()
    cert.get_subject().C = "JP"
    cert.get_subject().ST = "Tokyo"
    cert.get_subject().L = "Tokyo"
    cert.get_subject().O = "Ticket Service"
    cert.get_subject().OU = "Development"
    cert.get_subject().CN = "localhost"
    
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # 1年間有効
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')

    # ファイルに保存
    with open("cert.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open("key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    
    print("SSL証明書を生成しました: cert.pem, key.pem")

if __name__ == "__main__":
    if not os.path.exists("cert.pem") or not os.path.exists("key.pem"):
        try:
            generate_self_signed_cert()
        except ImportError:
            print("pyOpenSSLがインストールされていません")
            print("pip install pyOpenSSL を実行してください")
    else:
        print("証明書は既に存在します")
