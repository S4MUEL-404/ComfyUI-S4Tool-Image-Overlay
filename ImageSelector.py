from .ImageOverlay import pil2tensor  # 导入共享的辅助函数

class ImageSelector:
    """
    一个从插件目录下 images 子目录中选择图片的节点，支持 png、jpg、jpeg、webp、gif 格式。
    提供 image（RGB）和 mask（单通道灰度图）输出，与 ComfyUI 官方 MASK 输出一致。
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        import os
        import glob

        # 获取当前文件的目录（插件目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(current_dir, "images")

        # 如果 images 目录不存在，则创建
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        # 支持的图片格式
        supported_extensions = ["*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif"]
        image_files = []

        # 遍历所有支持的格式，获取图片文件
        for ext in supported_extensions:
            image_files.extend(glob.glob(os.path.join(images_dir, ext)))

        # 提取文件名（不含路径）
        image_names = [os.path.basename(f) for f in image_files]
        if not image_names:  # 如果没有图片，添加占位符
            image_names = ["No images found"]

        return {
            "required": {
                "image_file": (image_names, {
                    "default": image_names[0] if image_names else "No images found"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "select_image"
    CATEGORY = "💀S4Tool"
    OUTPUT_NODE = False

    def select_image(self, image_file):
        import os
        from PIL import Image
        import torch
        import numpy as np

        # 获取插件目录下的 images 子目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(current_dir, "images")
        image_path = os.path.join(images_dir, image_file)

        # 检查文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file {image_path} not found!")

        # 加载图片
        try:
            image = Image.open(image_path)
        except Exception as e:
            raise ValueError(f"Failed to load image {image_path}: {str(e)}")

        # 转换为 RGBA 格式以支持 Alpha 通道
        image = image.convert('RGBA')

        # 提取 RGB 部分
        image_rgb = image.convert('RGB')

        # 提取 Alpha 通道作为蒙版
        alpha_channel = image.split()[3]  # 获取 Alpha 通道
        mask_array = np.array(alpha_channel).astype(np.float32) / 255.0  # 归一化到 0-1

        # 反转蒙版值：与 ComfyUI 官方 MASK 输出一致，黑色（不透明，值 0）对应 0，白色（透明，值 255）对应 1
        mask_array = 1.0 - mask_array  # 反转：0 变为 1，1 变为 0
        mask_tensor = torch.from_numpy(mask_array).unsqueeze(0)  # (1, H, W)，与 ComfyUI 官方 MASK 格式一致

        # 调试信息
        print(f"Selected image: {image_path}, size: {image.size}")
        print(f"Mask tensor shape: {mask_tensor.shape}, min: {mask_tensor.min()}, max: {mask_tensor.max()}")

        # 转换为张量输出（RGB 格式）
        image_tensor = pil2tensor(image_rgb)

        return (image_tensor, mask_tensor)