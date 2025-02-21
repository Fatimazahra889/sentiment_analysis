from machine import Pin, SPI, PWM
import time
import math

# Color conversion function (RGB888 to RGB565)
def color565(r, g, b):
    return (r & 0xF8) << 8 | (g & 0xFC) << 3 | (b >> 3)

class ILI9341:
    def __init__(self, spi, dc, cs, rst):
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.rst = rst
        self.dc.init(Pin.OUT)
        self.cs.init(Pin.OUT)
        self.rst.init(Pin.OUT)
        self.reset()
        self.init_display()

    def reset(self):
        self.rst.value(1)
        time.sleep(0.1)
        self.rst.value(0)
        time.sleep(0.1)
        self.rst.value(1)
        time.sleep(0.1)

    def init_display(self):
        self.send_command(0x01)  # Software reset
        time.sleep(0.1)
        self.send_command(0x28)  # Display OFF
        self.send_command(0x3A, [0x55])  # Set color format to 16-bit
        self.send_command(0x36, [0x08])  # Memory access control
        self.send_command(0x11)  # Sleep out
        time.sleep(0.1)
        self.send_command(0x29)  # Display ON

    def send_command(self, cmd, data=None):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytearray([cmd]))
        if data:
            self.dc.value(1)
            self.spi.write(bytearray(data))
        self.cs.value(1)

    def fill_screen(self, color):
        self.fill_rect(0, 0, 240, 320, color)

    def fill_rect(self, x, y, width, height, color):
        self.set_window(x, y, x + width - 1, y + height - 1)
        row_data = bytearray([color >> 8, color & 0xFF] * width)  # One row at a time
        self.dc.value(1)
        self.cs.value(0)
        for _ in range(height):
            self.spi.write(row_data)  # Send row-by-row
        self.cs.value(1)

    def set_window(self, x1, y1, x2, y2):
        self.send_command(0x2A, [x1 >> 8, x1 & 0xFF, x2 >> 8, x2 & 0xFF])
        self.send_command(0x2B, [y1 >> 8, y1 & 0xFF, y2 >> 8, y2 & 0xFF])
        self.send_command(0x2C)

    def fill_circle(self, x0, y0, r, color):
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                if x * x + y * y <= r * r:
                    self.fill_rect(x0 + x, y0 + y, 1, 1, color)

    def fill_arc(self, x, y, r_outer, r_inner, start_angle, end_angle, color):
        """
        Draws a filled arc by drawing multiple lines between two radii.
        :param x: Center X
        :param y: Center Y
        :param r_outer: Outer radius
        :param r_inner: Inner radius (to create a hollow effect)
        :param start_angle: Start angle in degrees
        :param end_angle: End angle in degrees
        :param color: RGB565 color
        """
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)

        for angle in range(start_angle, end_angle, 2):  # Step of 2 degrees for better performance
            rad = math.radians(angle)
            x_outer = int(x + r_outer * math.cos(rad))
            y_outer = int(y + r_outer * math.sin(rad))
            x_inner = int(x + r_inner * math.cos(rad))
            y_inner = int(y + r_inner * math.sin(rad))
            self.draw_line(x_inner, y_inner, x_outer, y_outer, color)

    def draw_line(self, x0, y0, x1, y1, color):
        """Bresenham's line algorithm to draw a line."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self.fill_rect(x0, y0, 1, 1, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_triangle(self, x1, y1, x2, y2, x3, y3, color):
        """
        Fills a triangle defined by the three vertices (x1,y1), (x2,y2), (x3,y3)
        using a scanline fill algorithm.
        """
        # Sort vertices by y-coordinate ascending
        vertices = sorted([(x1, y1), (x2, y2), (x3, y3)], key=lambda v: v[1])
        x1, y1 = vertices[0]
        x2, y2 = vertices[1]
        x3, y3 = vertices[2]

        # For each scanline from y1 to y3, determine the start and end x values
        for y in range(y1, y3 + 1):
            if y < y2:
                if y2 - y1 != 0:
                    xa = x1 + (x2 - x1) * (y - y1) // (y2 - y1)
                else:
                    xa = x1
            else:
                if y3 - y2 != 0:
                    xa = x2 + (x3 - x2) * (y - y2) // (y3 - y2)
                else:
                    xa = x2
            if y3 - y1 != 0:
                xb = x1 + (x3 - x1) * (y - y1) // (y3 - y1)
            else:
                xb = x1
            if xa > xb:
                xa, xb = xb, xa
            self.fill_rect(xa, y, xb - xa + 1, 1, color)


