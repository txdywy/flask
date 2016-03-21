import pytesseract
from PIL import Image
print pytesseract.image_to_string(Image.open('Captcha_qrdiqokdiw.jpg'))

