import pytest

from services.utils import extract_bucket_and_object_from_url


class TestExtractBucketAndObjectFromUrl:
    def test_valid_minio_url(self):
        """Test valid MinIO URL extraction."""
        url = "http://localhost:9000/my-bucket/path/to/file.webp"
        bucket, object_name = extract_bucket_and_object_from_url(url)

        assert bucket == "my-bucket"
        assert object_name == "path/to/file.webp"

    def test_valid_https_url(self):
        """Test HTTPS MinIO URL."""
        url = "https://minio.example.com:9000/bucket-name/folder/image.jpg"
        bucket, object_name = extract_bucket_and_object_from_url(url)

        assert bucket == "bucket-name"
        assert object_name == "folder/image.jpg"

    def test_root_bucket_object(self):
        """Test object in bucket root."""
        url = "http://localhost:9000/bucket/file.txt"
        bucket, object_name = extract_bucket_and_object_from_url(url)

        assert bucket == "bucket"
        assert object_name == "file.txt"

    def test_nested_paths(self):
        """Test deeply nested paths."""
        url = "http://localhost:9000/bucket/folder1/folder2/folder3/file.png"
        bucket, object_name = extract_bucket_and_object_from_url(url)

        assert bucket == "bucket"
        assert object_name == "folder1/folder2/folder3/file.png"

    def test_with_query_params(self):
        """Test URL with query parameters."""
        url = "http://localhost:9000/bucket/image.jpg?version=123&token=abc"
        bucket, object_name = extract_bucket_and_object_from_url(url)

        assert bucket == "bucket"
        assert object_name == "image.jpg"

    def test_invalid_url_no_path(self):
        """Test invalid URL without path."""
        url = "http://localhost:9000"
        with pytest.raises(ValueError, match="Invalid MinIO URL format"):
            extract_bucket_and_object_from_url(url)

    def test_invalid_url_only_slash(self):
        """Test URL with only slash."""
        url = "http://localhost:9000/"
        with pytest.raises(ValueError, match="Invalid MinIO URL format"):
            extract_bucket_and_object_from_url(url)

    def test_invalid_url_only_bucket(self):
        """Test URL with only bucket name."""
        url = "http://localhost:9000/bucket"
        with pytest.raises(ValueError, match="Invalid MinIO URL format"):
            extract_bucket_and_object_from_url(url)

    def test_empty_url(self):
        """Test empty URL."""
        url = ""
        with pytest.raises(ValueError, match="Failed to parse MinIO URL"):
            extract_bucket_and_object_from_url(url)

    def test_malformed_url(self):
        """Test malformed URL."""
        url = "not-a-url"
        with pytest.raises(ValueError, match="Failed to parse MinIO URL"):
            extract_bucket_and_object_from_url(url)

    def test_url_with_auth(self):
        """Test URL with authentication."""
        url = "http://user:password@localhost:9000/bucket/file.txt"
        bucket, object_name = extract_bucket_and_object_from_url(url)

        assert bucket == "bucket"
        assert object_name == "file.txt"
