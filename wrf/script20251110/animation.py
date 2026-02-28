#surf_bin.pyで出力されたpng画像データをつなげてgif形式に保存する
#参考https://emotionexplorer.blog.fc2.com/blog-entry-356.html
from PIL import Image
import glob
import pprint

fig_dir="/DATA/USER/ozeki/MyWRF/fig/200912low_ensemble/ano/n1"

var_name="anomaly_dT850_dy"

files=sorted(glob.glob(f"{fig_dir}/{var_name}*.png"))
pprint.pprint(files)

images=list(map(lambda file : Image.open(file),files))
images[0].save(f"{fig_dir}/animation_{var_name}.gif",save_all=True,append_images=images[1:],optimize=True,duration=4000,loop=0)
print("Create Animation")
