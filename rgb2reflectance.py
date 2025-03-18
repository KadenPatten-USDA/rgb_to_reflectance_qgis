import rasterio
import os, sys, shutil
import multiprocessing
import numpy as np

helpScreen = """fail"""
valid_types = ["jpg","tif","tiff"]


def rgb2reflectance(img_folder):
    img_folder = os.path.abspath(img_folder)
    images = [i for i in os.listdir(img_folder) if i.split(".")[-1].lower() in valid_types]
    out_folder = os.path.join(img_folder,"../",f"{os.path.basename(img_folder)}_reflectance")
    try:
        os.mkdir(out_folder)
    except FileExistsError:
        None

    for i in images:
        with rasterio.open(os.path.join(img_folder,i)) as src:
            meta = src.meta.copy()
            data = src.read().astype(np.float32)

            data[0] = (((data[0]*0.0006) - 0.0249) / 0.1281 * 99) +1
            data[1] = (((data[1]*0.0010) - 0.0388) / 0.2162 * 99) +1
            data[2] = (((data[2]*0.0014) - 0.0509) / 0.3061 * 99) +1
            data[data < 0] = 1
            data = np.rint(data)
            meta.update({"dtype":np.uint8})

        with rasterio.open(os.path.join(out_folder,i),"w",**meta) as dst:
            dst.write(data.astype(np.uint8))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(helpScreen)
        sys.exit(-1)
    else:
        toRemove = []
        for n,a in enumerate(sys.argv):
            if a[0] == "-":
                flag = False
                if not flag:
                    print("Flag "+a+" unrecognized",file=sys.stderr)
                    sys.exit(-1)
                toRemove.append(a)
        for i in toRemove:
            sys.argv.remove(i)
        if len(sys.argv) < 2:
            print(helpScreen)
            sys.exit(-1)
        else:
            rgb2reflectance(sys.argv[1])