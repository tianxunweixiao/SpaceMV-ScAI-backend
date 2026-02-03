import os
import requests
from tqdm import tqdm

tile_dir = "gaode_tiles"  # Local tiles storage path
os.makedirs(tile_dir, exist_ok=True)

# tk = API_KEY
url_template = "https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "http://www.tianditu.gov.cn/"
}
for z in range(0, 6):
    for x in range(0, 2**z):
        for y in range(0, 2**z):
            path = os.path.join(tile_dir, str(z), str(x))
            os.makedirs(path, exist_ok=True)
            file_path = os.path.join(path, f"{y}.png")
            if os.path.exists(file_path):
                continue
            url = url_template.format(z=z, x=x, y=y)
            try:
                r = requests.get(url, headers=headers, timeout=30)
                if r.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(r.content)
                    print(f"{x},{y},{z}级瓦片下载完毕！")
                else:
                    print(f"下载失败 {url} 状态码 {r.status_code}")
            except Exception as e:
                print(f"下载异常 {url} {e}")
