def decode_s3_file_url(file_url: str):
    filename = file_url.strip("/")[1]
    return filename
