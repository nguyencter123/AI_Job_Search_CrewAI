# File: services/image_service.py
"""
Xử lý ảnh đại diện: Validate, Crop, Resize, Nén.
"""
from __future__ import annotations

from io import BytesIO
from PIL import Image

# Kích thước chuẩn ảnh thẻ 3x4 (tỉ lệ 3:4 ở 150 DPI)
AVATAR_WIDTH = 413
AVATAR_HEIGHT = 531
AVATAR_MAX_SIZE_MB = 2
AVATAR_ALLOWED_TYPES = ["image/jpeg", "image/png"]


def validate_avatar(file_data: bytes, mimetype: str) -> str | None:
    """Kiểm tra file ảnh hợp lệ. Trả về lỗi nếu không hợp lệ, None nếu OK."""
    if mimetype not in AVATAR_ALLOWED_TYPES:
        return "Chỉ chấp nhận file .jpg hoặc .png!"

    size_mb = len(file_data) / (1024 * 1024)
    if size_mb > AVATAR_MAX_SIZE_MB:
        return f"Dung lượng ảnh tối đa {AVATAR_MAX_SIZE_MB}MB! (Ảnh hiện tại: {size_mb:.1f}MB)"

    return None


def process_avatar(file_data: bytes) -> tuple[bytes, str]:
    """
    Xử lý ảnh: Crop giữa theo tỉ lệ 3:4 → Resize → Nén JPEG 85%.
    Trả về (bytes đã xử lý, mimetype).
    """
    img = Image.open(BytesIO(file_data))

    # Chuyển sang RGB (phòng trường hợp ảnh PNG có kênh alpha)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # --- Crop giữa theo tỉ lệ 3:4 ---
    target_ratio = AVATAR_WIDTH / AVATAR_HEIGHT  # 0.778
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Ảnh quá rộng → cắt bớt 2 bên
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    elif img_ratio < target_ratio:
        # Ảnh quá cao → cắt bớt trên/dưới
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop((0, top, img.width, top + new_height))

    # --- Resize về kích thước chuẩn ---
    img = img.resize((AVATAR_WIDTH, AVATAR_HEIGHT), Image.LANCZOS)

    # --- Nén JPEG 85% ---
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85, optimize=True)
    return buffer.getvalue(), "image/jpeg"
