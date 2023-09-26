import sys

from minio import Minio  # type: ignore

from coffee_backend.s3.object import ObjectCRUD


def test_object_create(init_minio: Minio) -> None:
    """_summary_

    Args:
        init_minio: _description_
    """
    test_object_crud = ObjectCRUD(
        minio_client=init_minio, bucket_name="coffee-images"
    )

    assert test_object_crud.bucket_name == "coffee-images"

    # pylint: disable=consider-using-with

    test_object = open("tests/s3/testimages/coffee.jpeg", "rb")

    test_objects_bytes = test_object.read()

    test_object.seek(0, 0)

    print("BYTES:")

    test_object_crud.create("uploaded_file.jpeg", test_object)

    response = init_minio.get_object(
        "coffee-images", "original/uploaded_file.jpeg"
    )

    returned_object = response.data
    # pylint: enable=consider-using-with

    assert returned_object == test_objects_bytes


def test_object_create_second_version(init_minio: Minio) -> None:
    """_summary_

    Args:
        init_minio: _description_
    """

    test_object_crud = ObjectCRUD(
        minio_client=init_minio, bucket_name="coffee-images"
    )

    assert test_object_crud.bucket_name == "coffee-images"

    # pylint: disable=consider-using-with
    test_object_one = open("tests/s3/testimages/coffee.jpeg", "rb")
    test_object_one.seek(0, 0)

    test_object_two = open("tests/s3/testimages/coffee2.jpeg", "rb")
    test_object_two_bytes = test_object_two.read()
    test_object_two.seek(0, 0)

    size = sys.getsizeof(test_object_two_bytes)

    print(f"Size of my_bytes: {size} bytes")

    test_object_crud.create("uploaded_file.jpeg", test_object_one)
    test_object_crud.create("uploaded_file.jpeg", test_object_two)

    response = init_minio.get_object(
        "coffee-images", "original/uploaded_file.jpeg"
    )

    returned_object = response.data

    # pylint: enable=consider-using-with

    assert returned_object == test_object_two_bytes
