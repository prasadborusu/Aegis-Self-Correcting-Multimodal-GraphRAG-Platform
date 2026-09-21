import boto3

class S3StorageService:
    def __init__(self):
        pass
    def validate_file(self, filename: str, content: bytes):
        if len(content) == 0: return False, 'File is empty'
        return True, None
    # Magic bytes check for PDF and images
