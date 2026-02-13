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
    "s3_save_path": "notes_media/{note_id}/videos",
    "max_size": 2 * 1024 * 1024 * 1024,  # 4GB
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
    "s3_save_path": "notes_media/{note_id}/images",
    "max_size": 30 * 1024 * 1024,  # 30MB
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
    "s3_save_path": "notes_media/{note_id}/audios",
    "max_size": 30 * 1024 * 1024,  # 30MB
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
    "s3_save_path": "users_media/{user_id}/avatar",
    "max_size": 5 * 1024 * 1024,  # 5MB
}
