import board
import busio
import digitalio
import adafruit_pcd8544

from PIL import Image, ImageDraw, ImageFont

spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)
dc = digitalio.DigitalInOut(board.D6) # data/command
cs = digitalio.DigitalInOut(board.D8) # Chip select
reset = digitalio.DigitalInOut(board.D5) # reset

display = adafruit_pcd8544.PCD8544(spi, dc, cs, reset)

#Notes: looks like Board knows GPIO by actual pin names, not just numbers

#backlight controls for later

"""
BORDER = 5
FONTSIZE = 10

display.bias = 5
display.contrast = 60
display.fill(0)
display.show()

image = Image.new("1", (display.width, display.height))
draw = ImageDraw.Draw(image)

# Draw a black background
draw.rectangle((0, 0, display.width, display.height), outline=255, fill=255)

# Draw a smaller inner rectangle
draw.rectangle(
            (BORDER, BORDER, display.width - BORDER - 1, display.height - BORDER - 1),
            outline=0,
            fill=0,
        )
# Load a TTF font.
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', FONTSIZE)

# Draw Some Text
text = "Hello World!"
(font_width, font_height) = font.getsize(text)
draw.text((display.width//2 - font_width//2, display.height//2 - font_height//2),
                  text, font=font, fill=255)

display.image(image)
display.show()
"""
