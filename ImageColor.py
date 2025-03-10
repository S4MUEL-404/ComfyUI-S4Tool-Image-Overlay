from .ImageOverlay import pil2tensor  # 导入共享的辅助函数
import torch  # 显式导入 torch 以避免 NameError

class ImageColor:
    """
    一个生成自定义颜色图片的节点，支持单一颜色或渐变颜色，无透明度功能。
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 4096,
                    "step": 1,
                    "display": "number"
                }),
                "height": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 4096,
                    "step": 1,
                    "display": "number"
                }),
                "color_hex": ("STRING", {
                    "default": "#FFFFFF",
                    "display": "text"
                }),
                "gradient_enabled": ("BOOLEAN", {
                    "default": False,
                    "display": "toggle"
                }),
                "gradient_start_hex": ("STRING", {
                    "default": "#000000",
                    "display": "text"
                }),
                "gradient_end_hex": ("STRING", {
                    "default": "#FFFFFF",
                    "display": "text"
                }),
                "gradient_angle": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 360.0,
                    "step": 1.0,
                    "display": "number"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)  # 移除 mask 输出
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "💀S4Tool"
    OUTPUT_NODE = False

    def generate_image(self, width, height, color_hex, gradient_enabled, 
                      gradient_start_hex, gradient_end_hex, gradient_angle):
        from PIL import Image
        import colorsys
        import numpy as np

        # 解析 HEX 颜色为 RGB（无透明度，固定为不透明）
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join(c * 2 for c in hex_color)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b)

        # 单一颜色生成
        if not gradient_enabled:
            color = hex_to_rgb(color_hex)
            image = Image.new('RGB', (width, height), color=color)  # 使用 RGB 模式，强制不透明
        else:
            # 渐变颜色生成
            start_color = hex_to_rgb(gradient_start_hex)
            end_color = hex_to_rgb(gradient_end_hex)

            # 创建渐变图像
            image = Image.new('RGB', (width, height))
            pixels = image.load()

            for x in range(width):
                for y in range(height):
                    # 计算渐变比例（基于角度）
                    angle_rad = np.radians(gradient_angle)
                    dx = x - width / 2
                    dy = y - height / 2
                    dist = (dx * np.cos(angle_rad) + dy * np.sin(angle_rad)) / max(width, height)
                    t = (dist + 0.5)  # 归一化到 0-1

                    # 插值计算颜色
                    r = start_color[0] + t * (end_color[0] - start_color[0])
                    g = start_color[1] + t * (end_color[1] - start_color[1])
                    b = start_color[2] + t * (end_color[2] - start_color[2])

                    # 裁剪到有效范围
                    r = np.clip(r, 0, 255)
                    g = np.clip(g, 0, 255)
                    b = np.clip(b, 0, 255)

                    pixels[x, y] = (int(r), int(g), int(b))

        # 调试信息
        print(f"Generated image size: {image.size}, mode: {image.mode}")

        # 转换为张量输出（RGB 格式）
        output_tensor = pil2tensor(image)
        return (output_tensor,)