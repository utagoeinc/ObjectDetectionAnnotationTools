# python3 yolo_boundingbox_checker.py -i images -l labels -o output -c predefined_classes.txt


import os
import imghdr
import argparse
import colorsys
import random
import numpy as np

from PIL import Image, ImageDraw, ImageFont, ImageFilter

parser = argparse.ArgumentParser(description='...')
parser.add_argument(
    '-i',
    '--image_path',
    help='path to input images, defaults to images/',
    default='images/')
parser.add_argument(
    '-l',
    '--label_path',
    help='path to input lebals, defaults to lebals/',
    default='labels/')
parser.add_argument(
    '-o',
    '--output_path',
    help='path to output for images with bounding boxes, defaults to output/',
    default='output/')
parser.add_argument(
    '-c',
    '--classes_path',
    help='path to classes, default is classes.txt',
    default='classes.txt')

def _main(args):
    image_path = os.path.expanduser(args.image_path)
    label_path = os.path.expanduser(args.label_path)
    output_path = os.path.expanduser(args.output_path)
    classes_path = os.path.expanduser(args.classes_path)

    if not os.path.exists(image_path):
        print('Image path not found.{}'.format(image_path))

    if not os.path.exists(label_path):
        print('Label path not found.{}'.format(label_path))

    if not os.path.exists(label_path):
        print('Claases path not found.{}'.format(classes_path))

    if not os.path.exists(output_path):
        print('Creating output path {}'.format(output_path))
        os.mkdir(output_path)

    # Generate colors for drawing bounding boxes.
    classes_file = open(classes_path)
    calsses_data = classes_file.read()
    classes_file.close()
    class_names = calsses_data.split('\n')
    hsv_tuples = [(x / len(class_names), 1., 1.)
                  for x in range(len(class_names))]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(
        map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
            colors))
    random.seed(10101)  # Fixed seed for consistent colors across runs.
    random.shuffle(colors)  # Shuffle colors to decorrelate adjacent classes.
    random.seed(None)  # Reset seed to default.

    error_count = 0

    for image_file in os.listdir(image_path):
        try:
            image_type = imghdr.what(os.path.join(image_path, image_file))
            if not image_type:
                continue
        except IsADirectoryError:
            continue

        root, ext = os.path.splitext(image_file)
        label_file_path = os.path.join(label_path, root+'.txt')
        if not os.path.exists(label_file_path):
            print('Label file path not found.{}'.format(label_file_path))
            error_count = error_count + 1
            continue

        image = Image.open(os.path.join(image_path, image_file))
        image = image.convert("RGB")
        output_image = image.copy()
        draw = ImageDraw.Draw(output_image)

        font = ImageFont.truetype(
            font='font/FiraMono-Medium.otf',
            size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
        thickness = (image.size[0] + image.size[1]) // 300
        print(image.width, image.height)

        f = open(label_file_path)
        label_data = f.read()
        f.close()
        lines = label_data.split('\n')

        for line in lines:
            print('\t'+line)
            boxdata = line.split(' ')
            if len(boxdata) < 5 :
                continue

            class_id = int(boxdata[0])
            predicted_class = class_names[class_id]
            label = '{} {:.2f}'.format(predicted_class, 1.00)
            label_size = draw.textsize(label, font)

            center_x = float(boxdata[1])*image.width
            center_y = float(boxdata[2])*image.height
            w = float(boxdata[3])*image.width
            h = float(boxdata[4])*image.height

            left = center_x - w/2
            top = center_y - h/2
            right = left + w
            bottom = top + h

            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=colors[class_id])
                draw.rectangle(
                    [tuple(text_origin), tuple(text_origin + label_size)],
                    fill=colors[class_id])
                draw.text(text_origin, label, fill=(0, 0, 0), font=font)

        del draw
        output_image.save(os.path.join(output_path, image_file), quality=90)

    print("errors:{}".format(error_count))

if __name__ == '__main__':
    _main(parser.parse_args())
