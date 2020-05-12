# Usage
#
# CurrentDir/
#   └ convert_annotation_xml_to_yolo.py (this file)
#   └ xml_labels/
#   │   └ (XML files)
#   └ yolo_labels/
#   │   └ (yolo label files)
#   └ predefined_classes.txt
#
# python3 convert_annotation_xml_to_yolo.py -i xml_labels_dir -o yolo_labels_dir -c predefined_classes.txt

import os
import io
import argparse
import xml.etree.ElementTree as ET

classes = {}

def main(args):
    if not os.path.exists(args.input_dir):
        print('No input directory')
        return

    if not os.path.exists(args.classes):
        print('predefined_classes.txt was not found')
        return

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    load_classes(args.classes)
    for file_name in os.listdir(args.input_dir):
        txt_string = convert(os.path.join(args.input_dir, file_name))
        file_name_without_suffix = file_name.split('.')[0]
        with open(os.path.join(args.output_dir, file_name_without_suffix + '.txt'), 'w') as output:
            output.write(txt_string)

def load_classes(file_path):
    with open(file_path, 'r') as classes_file:
        index = 0
        for line in classes_file:
            classes[line.replace('\n','')] = index
            index += 1

def convert(file_path):
    print('processing {}'.format(file_path))

    retval = ''

    tree = ET.parse(file_path)
    root = tree.getroot()

    # 先に画像サイズを取得
    width = 0
    height = 0
    for child in root:
        if child.tag == 'size':
            for element in child:
                if element.tag == 'width':
                    width = int(element.text)
                elif element.tag == 'height':
                    height = int(element.text)
            break

    # 教師データの変換
    for child in root:
        if child.tag == 'object':
            # object毎の処理
            class_id = 0
            x = 0.0 # bounding boxの中心x座標
            y = 0.0 # bounding boxの中心y座標
            w = 0.0 # bounding boxの幅
            h = 0.0 # bounding boxの高さ
            for element in child:
                if element.tag == 'name':
                    # クラス名から対応するidを取得
                    if element.text in classes.keys():
                        class_id = classes[element.text]

                elif element.tag == 'bndbox':
                    # bounding boxの位置と大きさを取得
                    xmin = 0
                    xmax = width
                    ymin = 0
                    ymax = height
                    for val in element:
                        if val.tag == 'xmin':
                            xmin = int(val.text)
                        elif val.tag == 'xmax':
                            xmax = int(val.text)
                        elif val.tag == 'ymin':
                            ymin = int(val.text)
                        elif val.tag == 'ymax':
                            ymax = int(val.text)

                    x = (xmin + xmax) / (2 * xmax)
                    y = (ymin + ymax) / (2 * ymax)
                    w = (xmax - xmin) / xmax
                    h = (ymax - ymin) / ymax

            retval += '{} {} {} {} {}\n'.format(class_id, x, y, w, h)

    return retval

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--input_dir',
        help='path to input lebals, defaults to xml_lebals/',
        default='xml_labels/')
    parser.add_argument(
        '-o',
        '--output_dir',
        help='path to output lebals, defaults to yolo_labels/',
        default='yolo_labels/')
    parser.add_argument(
        '-c',
        '--classes_path',
        help='path to classes, default is classes.txt',
        default='classes.txt')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    main(args)
