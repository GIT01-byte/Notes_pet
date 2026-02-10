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
    "max_size": 2 * 1024 * 1024 * 1024  # 4GB
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
    "max_size": 30 * 1024 * 1024  # 30MB
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
    "max_size": 5 * 1024 * 1024  # 5MB
}

AUDIO = {
    "content_types": [
        "audio/mpeg",  # mp3
        "audio/wav",
        "audio/wave",  # wav
        "application/ogg",
    ],
    "max_size": 30 * 1024 * 1024  # 30MB
}
