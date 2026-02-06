import uuid

def encode_multipart_formdata(fields, files):
    """
    Manually encodes multipart/form-data for use with urllib.
    """
    boundary = uuid.uuid4().hex.encode('utf-8')
    body = bytearray()
    
    for name, value in fields.items():
        body.extend(b'--' + boundary + b'\r\n')
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode('utf-8'))
        body.extend(str(value).encode('utf-8'))
        body.extend(b'\r\n')
        
    for name, (filename, content, content_type) in files.items():
        body.extend(b'--' + boundary + b'\r\n')
        body.extend(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode('utf-8'))
        if content_type:
            body.extend(f'Content-Type: {content_type}\r\n'.encode('utf-8'))
        body.extend(b'\r\n')
        body.extend(content)
        body.extend(b'\r\n')
        
    body.extend(b'--' + boundary + b'--\r\n')
    
    content_type_header = f'multipart/form-data; boundary={boundary.decode("utf-8")}'
    return bytes(body), content_type_header
