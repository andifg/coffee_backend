from unittest.mock import MagicMock

import pytest
from minio import Minio  # type: ignore
from minio import S3Error  # type: ignore

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.s3.object import ObjectCRUD
from tests.conftest import DummyImages


def test_object_create(
    init_minio: Minio, dummy_coffee_images: DummyImages
) -> None:
    """Test ObjectCRUD create method for S3 object creation.

    Args:
        init_minio (Minio): The initialized Minio client for S3 interactions.
        dummy_coffee_images (DummyImages): An instance providing dummy coffee
            image data.
    """
    test_object_crud = ObjectCRUD(
        minio_client=init_minio, bucket_name="coffee-images"
    )

    assert test_object_crud.bucket_name == "coffee-images"

    test_object_crud.create(
        filepath="original",
        filename="uploaded_file.jpeg",
        file=dummy_coffee_images.image_1.file,
        file_type="jpeg",
    )

    response = init_minio.get_object(
        "coffee-images", "original/uploaded_file.jpeg"
    )

    file_type_metadata = response.headers.get("x-amz-meta-filetype")

    assert file_type_metadata == "jpeg"

    returned_object = response.data

    assert returned_object == dummy_coffee_images.image_1_bytes


def test_object_create_second_version(
    init_minio: Minio, dummy_coffee_images: DummyImages
) -> None:
    """Test the ObjectCRUD create method for uploading multiple S3 objects.

    Args:
        init_minio (Minio): The initialized Minio client for S3 interactions.
        dummy_coffee_images (DummyImages): An instance providing dummy coffee
            image data.
    """

    test_object_crud = ObjectCRUD(
        minio_client=init_minio, bucket_name="coffee-images"
    )

    assert test_object_crud.bucket_name == "coffee-images"

    test_object_crud.create(
        filepath="original",
        filename="uploaded_file.jpeg",
        file=dummy_coffee_images.image_1.file,
        file_type="jpeg",
    )

    test_object_crud.create(
        filepath="original",
        filename="uploaded_file.jpeg",
        file=dummy_coffee_images.image_2.file,
        file_type="jpeg",
    )

    response = init_minio.get_object(
        "coffee-images", "original/uploaded_file.jpeg"
    )

    file_type_metadata = response.headers.get("x-amz-meta-filetype")

    assert file_type_metadata == "jpeg"

    returned_object = response.data

    assert returned_object == dummy_coffee_images.image_2_bytes


def test_object_read(
    init_minio: Minio, dummy_coffee_images: DummyImages
) -> None:
    """Test the ObjectCRUD read method for retrieving S3 objects.

    Args:
        init_minio (Minio): The initialized Minio client for S3 interactions.
        dummy_coffee_images (DummyImages): An instance providing dummy coffee
            image data.
    """
    test_object_crud = ObjectCRUD(
        minio_client=init_minio, bucket_name="coffee-images"
    )

    assert test_object_crud.bucket_name == "coffee-images"

    test_object_crud.create(
        filepath="original",
        filename="uploaded_file.jpeg",
        file=dummy_coffee_images.image_1.file,
        file_type="jpeg",
    )

    returned_object, filetype = test_object_crud.read(
        filename="uploaded_file.jpeg", filepath="original"
    )

    assert filetype == "jpeg"

    assert returned_object == dummy_coffee_images.image_1_bytes


def test_object_read_nonexisting_image(init_minio: Minio) -> None:
    """Test the ObjectCRUD read method for a non-existing S3 object.

    Args:
        init_minio (Minio): The initialized Minio client for S3 interactions.
    """
    test_object_crud = ObjectCRUD(
        minio_client=init_minio, bucket_name="coffee-images"
    )

    assert test_object_crud.bucket_name == "coffee-images"

    with pytest.raises(ObjectNotFoundError):
        test_object_crud.read(
            filename="nonexisting_object", filepath="original"
        )


def test_object_read_uncatched_error(init_minio: Minio) -> None:
    """Test the ObjectCRUD read method for an unhandled S3 error.

    This test verifies that when the ObjectCRUD read method encounters an
    unhandled S3 error, it raises the expected S3Error exception.
    """
    minio_mock = MagicMock()

    minio_mock.get_object.side_effect = S3Error(
        code="non handled error code",
        message="error message",
        resource="resource",
        request_id="request_id",
        host_id="host_id",
        response=None,
    )

    test_object_crud = ObjectCRUD(
        minio_client=minio_mock, bucket_name="coffee-images"
    )

    assert test_object_crud.bucket_name == "coffee-images"

    with pytest.raises(S3Error, match="^S3 operation failed.*"):
        test_object_crud.read(
            filename="nonexisting_object", filepath="original"
        )


def test_object_delete(
    init_minio: Minio, dummy_coffee_images: DummyImages
) -> None:
    """Test the ObjectCRUD delete method for deleting S3 objects.

    Test the deletion of an S3 object by first creating two versions of a
    single object, then deleting the object. This test verifies that the
    deletion of the object is successful and that the object is no longer
    retrievable.

    Args:
        init_minio (Minio): The initialized Minio client for S3 interactions.
        dummy_coffee_images (DummyImages): An instance providing dummy coffee
            image data.
    """
    test_object_crud = ObjectCRUD(
        minio_client=init_minio, bucket_name="coffee-images"
    )

    test_object_crud.create(
        filepath="original",
        filename="uploaded_file.jpeg",
        file=dummy_coffee_images.image_1.file,
        file_type="jpeg",
    )

    test_object_crud.create(
        filepath="original",
        filename="uploaded_file.jpeg",
        file=dummy_coffee_images.image_2.file,
        file_type="jpeg",
    )

    test_object_crud.delete(filename="uploaded_file.jpeg", filepath="original")

    with pytest.raises(ObjectNotFoundError):
        test_object_crud.read(
            filename="uploaded_file.jpeg", filepath="original"
        )


def test_object_delete_verify_other_objects_stay_untouched(
    init_minio: Minio, dummy_coffee_images: DummyImages
) -> None:
    """Test the ObjectCRUD delete method for deleting S3 objects to not
    influence other objects.

    Args:
        init_minio (Minio): The initialized Minio client for S3 interactions.
        dummy_coffee_images (DummyImages): An instance providing dummy coffee
            image data.
    """
    test_object_crud = ObjectCRUD(
        minio_client=init_minio, bucket_name="coffee-images"
    )

    test_object_crud.create(
        filename="uploaded_file.jpeg",
        filepath="original",
        file=dummy_coffee_images.image_1.file,
        file_type="jpeg",
    )

    test_object_crud.create(
        filename="uploaded_file_2.jpeg",
        filepath="original",
        file=dummy_coffee_images.image_2.file,
        file_type="jpeg",
    )

    test_object_crud.delete(filename="uploaded_file.jpeg", filepath="original")

    with pytest.raises(ObjectNotFoundError):
        test_object_crud.read(
            filename="uploaded_file.jpeg", filepath="original"
        )

    returned_object, filetype = test_object_crud.read(
        filename="uploaded_file_2.jpeg", filepath="original"
    )

    assert filetype == "jpeg"

    assert returned_object == dummy_coffee_images.image_2_bytes


def test_object_delete_nonexisting_image(init_minio: Minio) -> None:
    """Test the ObjectCRUD delete method for a non-existing S3 object.

    Make sure that the ObjectCRUD delete method works without an erorr when
    deleting a non-existing S3 object.

    Args:
        init_minio (Minio): The initialized Minio client for S3 interactions.
    """
    test_object_crud = ObjectCRUD(
        minio_client=init_minio, bucket_name="coffee-images"
    )

    assert test_object_crud.bucket_name == "coffee-images"

    test_object_crud.delete(filename="nonexisting_object", filepath="original")
