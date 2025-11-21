# 文生视频
import os

from volcenginesdkarkruntime import Ark


client = Ark(api_key=os.environ.get("ARK_API_KEY"))

if __name__ == "__main__":
    print("----- create request -----")
    resp = client.content_generation.tasks.create(
        model="doubao-seedance-1-0-pro-250528",
        content=[{"text":"多个镜头。一名侦探进入一间光线昏暗的房间。他检查桌上的线索，手里拿起桌上的某个物品。镜头转向他正在思索。 --ratio 16:9","type":"text"}]
    )
    print(resp)

# 图生视频-首帧
import os

from volcenginesdkarkruntime import Ark

client = Ark(api_key=os.environ.get("ARK_API_KEY"))

if __name__ == "__main__":
    print("----- create request -----")
    resp = client.content_generation.tasks.create(
        model="doubao-seedance-1-0-pro-fast-251015",
        content=[{"text":"女孩抱着狐狸，女孩睁开眼，温柔地看向镜头，狐狸友善地抱着，镜头缓缓拉出，女孩的头发被风吹动  --ratio adaptive  --dur 5","type":"text"},{"image_url":{"url":"https://ark-project.tos-cn-beijing.volces.com/doc_image/i2v_foxrgirl.png"},"type":"image_url"}]
    )
    print(resp)

