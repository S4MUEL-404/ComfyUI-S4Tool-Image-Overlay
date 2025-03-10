print("Loading ComfyUI-S4Tool nodes...")

# 导入所有节点类
from .ImageOverlay import ImageOverlay
from .ImageBlendWithAlpha import ImageBlendWithAlpha
from .ImageSelector import ImageSelector
from .ImageColor import ImageColor

# 节点映射
NODE_CLASS_MAPPINGS = {
    "ImageOverlay": ImageOverlay,
    "ImageBlendWithAlpha": ImageBlendWithAlpha,
    "ImageSelector": ImageSelector,
    "ImageColor": ImageColor  # 新增节点映射
}

# 节点显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageOverlay": "💀Image Overlay",
    "ImageBlendWithAlpha": "💀Image Blend with Alpha",
    "ImageSelector": "💀Image Selector",
    "ImageColor": "💀Image Color"
}