import argparse
import os

from PIL import Image
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('input_dir',
    help='Path to the YOLO dataset directory, which contains classes, images/ and labels/')

def _main(args):
    input_dir = os.path.expanduser(args.input_dir)

    for path in os.listdir(input_dir):
        tmp_path = os.path.join(input_dir, path)

        if os.path.isfile(tmp_path):
            classes_path = tmp_path
        else:
            if path == 'images':
                images_path = tmp_path
            elif path == 'labels':
                labels_path = tmp_path

    output_dir = os.path.join(input_dir, 'out')
    output_labels_dir = os.path.join(output_dir, 'labels')
    os.makedirs(output_labels_dir, exist_ok=True)

    classes = get_classes_list(classes_path)
    save_pbtxt(classes, output_dir)

    for image_file in os.listdir(images_path):
        image = np.array(Image.open(os.path.join(images_path, image_file)))
        height, width, channels = image.shape

        basename, _ = os.path.splitext(image_file)
        boxes = []

        with open(os.path.join(labels_path, basename + '.txt'), 'r') as label_file:
            for line in label_file:
                tmp_list = line.strip().split(' ')

                tmp_list[0] = classes[int(tmp_list[0])]             # class
                tmp_list[1] = round(float(tmp_list[1]) * width)     # x
                tmp_list[2] = round(float(tmp_list[2]) * height)    # y
                tmp_list[3] = round(float(tmp_list[3]) * width)     # w
                tmp_list[4] = round(float(tmp_list[4]) * height)    # h

                boxes.append(tmp_list)

        save_xml(image_file, output_labels_dir, height, width, channels, boxes)

    print('Done!!!')

def get_classes_list(classes_path):
    classes_list = []

    with open(classes_path, 'r') as classes_file:
        for class_name in classes_file:
            classes_list.append(class_name.strip())

    return classes_list

def save_pbtxt(classes, output_dir):
    with open(os.path.join(output_dir, 'label_map.pbtxt'), 'w') as pbtxt:
        for id, name in enumerate(classes):
            pbtxt.write("item {\n"
                        + "  id: {}\n".format(id)
                        + "  name: '{}'\n".format(name)
                        + "}\n")

def save_xml(filename, output_dir, height, width, channels, boxes):
    xml_text = ''

    xml_text += '<annotation>\n'
    xml_text += '  <filename>{}</filename>\n'.format(filename)
    xml_text += '  <size>\n'
    xml_text += '    <width>{}</width>\n'.format(width)
    xml_text += '    <height>{}</height>\n'.format(height)
    xml_text += '    <depth>{}</depth>\n'.format(channels)
    xml_text += '  </size>\n'

    for name, x, y, w, h in boxes:
        xmin = round(x - w/2)
        ymin = round(y - h/2)
        xmax = round(x + w/2)
        ymax = round(y + h/2)

        xml_text += '  <object>\n'
        xml_text += '    <name>{}</name>\n'.format(name)
        xml_text += '    <bndbox>\n'
        xml_text += '      <xmin>{}</xmin>\n'.format(xmin)
        xml_text += '      <ymin>{}</ymin>\n'.format(ymin)
        xml_text += '      <xmax>{}</xmax>\n'.format(xmax)
        xml_text += '      <ymax>{}</ymax>\n'.format(ymax)
        xml_text += '    </bndbox>\n'
        xml_text += '  </object>\n'

    xml_text += '</annotation>\n'

    basename, _ = os.path.splitext(filename)
    with open(os.path.join(output_dir, basename + '.xml'), 'w') as xml:
        xml.write(xml_text)

if __name__ == '__main__':
    _main(parser.parse_args())
