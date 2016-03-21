#http://stackoverflow.com/questions/2363490/limit-characters-tesseract-is-looking-for
import pytesseract
from PIL import Image
print pytesseract.image_to_string(Image.open('Captcha_gcjwazwmwn.jpg'))
print pytesseract.image_to_string(Image.open('Captcha_qrdiqokdiw.jpg'))
print pytesseract.image_to_string(Image.open('Captcha_mobwoaprwv.jpg'))

