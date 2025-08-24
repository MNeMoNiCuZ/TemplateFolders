from .nodes.format_date_time import FormatDateTime
from .nodes.load_text_image_pair_single import LoadTextImagePairSingle

NODE_CLASS_MAPPINGS = {
    "📅 Format Date Time": FormatDateTime,
    "🖼️+📝 Load Text-Image Pair (Single)": LoadTextImagePairSingle,
}
print("\033[34m My Custom Nodes: \033[92mLoaded\033[0m")