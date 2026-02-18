VIDEOS = {
    "content_types": [
        "video/mp4",
        "video/mpeg",
        "video/avi",
        "video/x-msvideo",  # avi
        "video/quicktime",  # mov
        "video/x-ms-wmv",  # wmv
        "video/x-flv",  # flv
        "video/webm",
        "video/x-matroska",  # mkv
    ],
    "extensions": [
        "mp4", 
        "mpeg", 
        "avi", 
        "mov", 
        "wmv", 
        "flv", 
        "webm", 
        "mkv"
    ],
    "max_width": 3160,
    "max_height": 3160,
    "max_size": 500 * 1024 * 1024,  # 500MB
    "category_name": "video"
}

IMAGES = {
    "content_types": [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/bmp",
        "image/webp",
        "image/svg+xml",
        "image/x-icon",  # ico
        "image/vnd.microsoft.icon",  # ico
    ],
    "extensions": [
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "webp",
        "svg",
        "ico",
    ],
    "max_width": 3160,
    "max_height": 3160,
    "max_size": 30 * 1024 * 1024,  # 30MB
    "category_name": "image"
}

AUDIO = {
    "content_types": [
        "audio/mpeg",  # mp3
        "audio/wav",
        "audio/wave",  # wav
        "application/ogg",
    ],
    "extensions": [
        "mpeg",
        "mp3",
        "wav",
        "ogg",
    ],
    "max_size": 30 * 1024 * 1024,  # 30MB
    "category_name": "audio"
}

AVATARS = {
    "content_types": [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/bmp",
        "image/webp",
        "image/svg+xml",
        "image/x-icon",  # ico
        "image/vnd.microsoft.icon",  # ico
    ],
    "extensions": [
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "webp",
        "svg",
        "ico",
    ],
    "max_width": 1024,
    "max_height": 1024,
    "max_size": 5 * 1024 * 1024,  # 5MB
    "category_name": "avatar"
}

NOTES_ATTACHMENT_NAME = "post_attachment"
USERS_AVATAR_NAME = "avatar"
