# VARIABLE SETUP
width = 1080
height = 2400
blur_radius = 0
point_distance = 350
gradient_start_color = (30, 30, 30)
gradient_stop_color = (180, 180, 180)
noise_strength = 5

# TEMP CANVAS
margin = point_distance * 2
temp_width = width + margin * 2
temp_height = height + margin * 2

import PIL.Image as Image
import PIL.ImageDraw as ImageDraw

temp_image = Image.new("RGBA", (temp_width, temp_height))
temp_draw = ImageDraw.Draw(temp_image)

# POISSON POINTS
import bridson

points = bridson.poisson_disc_samples(
    temp_width,
    temp_height,
    r=point_distance
)

# GRADIENT COLOR
import random

rando = 10
def gradient_color(start_color, stop_color):
    temp = random.random()
    dr = stop_color[0] - start_color[0]
    dg = stop_color[1] - start_color[1]
    db = stop_color[2] - start_color[2]
    r = int(start_color[0] + dr * temp + random.random() * rando)
    g = int(start_color[1] + dg * temp + random.random() * rando)
    b = int(start_color[2] + db * temp + random.random() * rando)
    return (r, g, b, 255)

# TRIANGLE MESH
import scipy.spatial

triangle = scipy.spatial.Delaunay(points)
for simplex in triangle.simplices:
    temp_draw.polygon([points[idx] for idx in simplex], fill=gradient_color(gradient_start_color, gradient_stop_color))

# APPLY BLUR
import PIL.ImageFilter as ImageFilter

temp_image = temp_image.filter(ImageFilter.GaussianBlur(blur_radius))

# NOISE OVERLAY
import PIL.ImageChops

noise_image = Image.effect_noise((temp_width, temp_height), noise_strength).convert("RGBA")
temp_image = PIL.ImageChops.multiply(temp_image, noise_image)

# CROP & SAVE
final_image = temp_image.crop((margin, margin, margin + width, margin + height))
final_image.save("wallpaper.png")