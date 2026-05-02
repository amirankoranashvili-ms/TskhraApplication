"""MinIO client factory.

Provides a convenience function for creating an async MinIO client
with the required credentials and endpoint configuration.
"""

from miniopy_async import Minio


def create_minio_client(
    endpoint: str,
    access_key: str,
    secret_key: str,
    secure: bool = False,
) -> Minio:
    """Create an async MinIO client.

    Args:
        endpoint: The MinIO server endpoint (e.g. ``localhost:9000``).
        access_key: The access key (username).
        secret_key: The secret key (password).
        secure: Whether to use HTTPS for the connection.

    Returns:
        A configured async MinIO client.
    """
    return Minio(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure,
    )