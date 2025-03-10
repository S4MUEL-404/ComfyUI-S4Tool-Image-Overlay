from .ImageOverlay import pil2tensor, tensor2pil  # 导入共享的辅助函数

class ImageBlendWithAlpha:
    """
    一个将图像与 Alpha 蒙版结合的节点，使用 Alpha 蒙版裁剪输入图像，仅保留 Alpha 不透明的区域。
    输出为 RGBA 格式，模仿 JoinImageWithAlpha 的行为。
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # 输入图像（RGB）
                "alpha": ("MASK",),   # Alpha 蒙版（单通道）
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_with_alpha",)
    FUNCTION = "join_image_with_alpha"
    CATEGORY = "💀S4Tool"
    OUTPUT_NODE = False

    def join_image_with_alpha(self, image, alpha):
        from PIL import Image
        import torch
        import numpy as np

        # 将输入张量转换为 PIL 图像
        image_pil = tensor2pil(image).convert('RGB')  # 确保是 RGB 格式
        alpha_pil = tensor2pil(alpha).convert('L')    # 确保 Alpha 是单通道灰度图

        # 调试信息
        print(f"Image PIL size: {image_pil.size}, mode: {image_pil.mode}")
        print(f"Alpha PIL size: {alpha_pil.size}, mode: {alpha_pil.mode}, min: {np.array(alpha_pil).min()/255}, max: {np.array(alpha_pil).max()/255}")

        # 如果 Alpha 通道尺寸与图像不匹配，则调整 Alpha 大小
        if alpha_pil.size != image_pil.size:
            print(f"Resizing alpha from {alpha_pil.size} to {image_pil.size}")
            alpha_pil = alpha_pil.resize(image_pil.size, Image.Resampling.LANCZOS)

        # 确保 Alpha 值在 0-255 范围内
        alpha_array = np.array(alpha_pil)
        if alpha_array.max() <= 1.0:  # 如果 Alpha 是归一化值 (0-1)
            alpha_array = (alpha_array * 255).astype(np.uint8)
        elif alpha_array.max() > 255:  # 如果值超过 255，裁剪
            alpha_array = np.clip(alpha_array, 0, 255).astype(np.uint8)

        # 反转 Alpha 蒙版：HeaderMask.png 中黑色（值 0）为不透明区域，应保留图像；非黑色（值 255）为透明区域，应移除图像
        alpha_array = 255 - alpha_array
        alpha_pil = Image.fromarray(alpha_array, mode='L')

        # 调试反转后的 Alpha 值
        print(f"Inverted Alpha min: {alpha_array.min()/255}, max: {alpha_array.max()/255}")

        # 创建一个透明的 RGBA 图像
        rgba_image = Image.new('RGBA', image_pil.size, (0, 0, 0, 0))  # 全透明背景
        # 使用反转后的 Alpha 蒙版粘贴图像，保留不透明区域（HeaderMask.png 中黑色部分）
        rgba_image.paste(image_pil, (0, 0), alpha_pil)

        # 调试输出
        rgba_array = np.array(rgba_image)
        print(f"RGBA output shape: {rgba_array.shape}, alpha min: {rgba_array[..., 3].min()/255}, alpha max: {rgba_array[..., 3].max()/255}")

        # 转换为张量输出（保持 RGBA 格式）
        output_tensor = pil2tensor(rgba_image)
        return (output_tensor,)