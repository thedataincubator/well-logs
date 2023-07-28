from io import BytesIO
import sys

from PIL import Image
from imagehash import average_hash

Image.MAX_IMAGE_PIXELS = None


def hash_log(byte_string):
    image = Image.open(BytesIO(byte_string))
    hash_val = average_hash(image)

    return str(hash_val)


def main(file_path):
    with open(sys.argv[1], "rb") as f:
        hash_val = hash_log(f.read())

    return hash_val


if __name__ == "__main__":
    print(main(sys.argv[1]))
