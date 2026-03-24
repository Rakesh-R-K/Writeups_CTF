import numpy as np
from PIL import Image
import os
import sys

def get_paths_from_args():
    if len(sys.argv) != 3:
        print("Usage: python retrieve_kernel.py <input_name> <output_name>")
        sys.exit(1)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(base_dir, ".", "images")

    inp_name = sys.argv[1]
    out_name = sys.argv[2]

    input_path = os.path.join(images_dir, inp_name.split('.')[0] + ".jpg")
    output_path = os.path.join(images_dir, out_name.split('.')[0] + ".jpg")
    processed_numpy = os.path.join(images_dir, out_name.split('.')[0] + ".npy")

    if not os.path.isfile(input_path):
        print("Input image not found:", input_path)
        sys.exit(1)

    if not os.path.isdir(images_dir):
        print("Images directory not found:", images_dir)
        sys.exit(1)

    return input_path, output_path, processed_numpy

def recover_kernel(input_ch, output_ch, ksize=3):
    h, w = input_ch.shape
    pad = ksize // 2

    X = []
    Y = []

    for i in range(pad, h - pad):
        for j in range(pad, w - pad):
            patch = input_ch[i - pad:i + pad + 1,
                              j - pad:j + pad + 1]
            X.append(patch.flatten())
            Y.append(output_ch[i, j])

    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)

    k, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)

    return k.reshape(ksize, ksize)


if __name__ == "__main__":

    INPUT_IMAGE, OUTPUT_IMAGE, PROCESSED_NUMPY = get_paths_from_args()
    original_img = Image.open(INPUT_IMAGE).convert("RGB")
    original = np.asarray(original_img, dtype=np.float64)

    processed = np.load(PROCESSED_NUMPY).astype(np.float64)

    if original.shape != processed.shape:
        print("The vessels do not align.")
        raise SystemExit

    r_in = original[:, :, 0]
    g_in = original[:, :, 1]
    b_in = original[:, :, 2]

    r_out = processed[:, :, 0]
    g_out = processed[:, :, 1]
    b_out = processed[:, :, 2]

    kr = recover_kernel(r_in, r_out)
    kg = recover_kernel(g_in, g_out)
    kb = recover_kernel(b_in, b_out)

    print("\nKernel for the Red layer:\n")
    print(np.rint(kr).astype(int))

    print("\nKernel for the Green layer:\n")
    print(np.rint(kg).astype(int))

    print("\nKernel for the Blue layer:\n")
    print(np.rint(kb).astype(int))