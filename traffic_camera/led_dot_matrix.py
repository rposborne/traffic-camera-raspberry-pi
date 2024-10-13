
import os
from time import sleep
import board
import busio

# Import the HT16K33 LED matrix module.
from adafruit_ht16k33 import matrix
from PIL import Image, ImageDraw, ImageFont

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create the matrix class.
# This creates a 16x8 matrix:
# matrix = matrix.Matrix16x8(i2c)
# Or this creates a 8x8 matrix:
matrix = matrix.Matrix8x8(i2c, auto_write=False)
# Or this creates a 8x8 bicolor matrix:
#matrix = matrix.Matrix8x8x2
# Finally you can optionally specify a custom I2C address of the HT16k33 like:
#matrix = matrix.Matrix16x8(i2c, address=0x70)


# Change the brightness
matrix.brightness = 1


def display_text(text_1, time_on=0):
  """Displays 'text_1' onto the LED ht16k33 for 'time_on' seconds.

  If time_on is '0', the text will be displayed indefinitely."""
  matrix.fill(0)
  # Create an image with the text
  image = Image.new('1', (8 * len(text_1), 8))
  draw = ImageDraw.Draw(image)
  font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),  "fonts" , "pixelmix.ttf"))
  font = font = ImageFont.truetype(font_path, 8)
  char_display_time = 0.3
  timer = 0
  # while timer < time_on:
  for i, char in enumerate(text_1):
    matrix.fill(0)
    # Create an image with the character
    image = Image.new('1', (8, 8))
    draw = ImageDraw.Draw(image)
    draw.text((1, -1), char, font=font, fill=1)

    # Rotate the image by 90 degrees
    rotated_image = image.rotate(-90, expand=True)

    # Convert rotated image to matrix format
    for x in range(rotated_image.width):
      for y in range(rotated_image.height):
        if x < 8 and y < 8:  # Ensure we don't go out of bounds
          matrix[x, y] = rotated_image.getpixel((x, y))
    matrix.show()
    sleep(char_display_time)
    timer += char_display_time
  matrix.fill(0)
  matrix.show()
  sleep(char_display_time)




def flash_text(text_1, time_on, flashes):
  """Flashes 'text_1' for a number 'flashes' of flashes
  with a delay of 'time_on' seconds."""
  for _ in range(flashes):
    display_text(text_1, time_on)
    matrix.fill(0)
    matrix.show()
    sleep(time_on)



def alarm(time_on, rate=0.1):
  """Flashes 'ALARM' for a number 'flashes' of flashes
  with a delay of 'time_on' seconds."""
  timer = 0

  while timer < time_on:
    matrix.fill(1)
    matrix.show()
    sleep(rate)
    matrix.fill(0)
    matrix.show()
    sleep(rate)
    timer += (2 * rate)

class led_matrix():

  def clear(self):
    matrix.fill(0)
    matrix.show()

led = led_matrix()


if __name__ == "__main__":

  display_text("26", 0)

  # display_text("52", 0)
  alarm(10)

