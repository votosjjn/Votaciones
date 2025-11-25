# necesita qrcode: pip install qrcode[pil]
import qrcode
url = 'http://127.0.0.1:5000/'
img = qrcode.make(url)
img.save('static/qr_acceso.png')
print('QR guardado en static/qr_acceso.png ->', url)
