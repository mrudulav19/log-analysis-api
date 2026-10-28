
import io


SAMPLE_LOG = (
    "2026-10-28 09:15:21 INFO auth_service User login successful\n"
    "2026-10-28 09:16:02 WARNING payment_service Retry attempt 2\n"
    "This line is malformed\n"
    "2026-10-28 09:17:01 ERROR database Connection timeout\n"
)


def upload_sample(client, filename="test.log", content=SAMPLE_LOG):
    return client.post(
        "/api/v1/files",
        data={
            "file": (io.BytesIO(content.encode("utf-8")), filename)
        },
        content_type="multipart/form-data",
    )


def test_upload_file(client):
    response = upload_sample(client)

    assert response.status_code == 201

    data = response.get_json()
    assert data["file"]["filename"] == "test.log"
    assert data["file"]["total_lines"] == 4
    assert data["file"]["parsed_lines"] == 3
    assert data["file"]["failed_lines"] == 1


def test_list_files(client):
    upload_sample(client)

    response = client.get("/api/v1/files")

    assert response.status_code == 200
    files = response.get_json()["files"]

    assert len(files) == 1
    assert files[0]["filename"] == "test.log"


def test_get_parsed_entries(client):
    upload_response = upload_sample(client)
    file_id = upload_response.get_json()["file"]["id"]

    response = client.get(f"/api/v1/files/{file_id}/entries")

    assert response.status_code == 200

    data = response.get_json()
    assert data["filename"] == "test.log"
    assert data["total_entries"] == 3
    assert len(data["entries"]) == 3
    assert data["entries"][0]["level"] == "INFO"
    assert data["entries"][1]["level"] == "WARNING"
    assert data["entries"][2]["level"] == "ERROR"


def test_missing_file_returns_404(client):
    response = client.get("/api/v1/files/999/entries")

    assert response.status_code == 404
    assert response.get_json()["error"] == "File not found."


def test_delete_file(client):
    upload_response = upload_sample(client)
    file_id = upload_response.get_json()["file"]["id"]

    response = client.delete(f"/api/v1/files/{file_id}")

    assert response.status_code == 200

    detail_response = client.get(f"/api/v1/files/{file_id}")
    assert detail_response.status_code == 404

    entries_response = client.get(
        f"/api/v1/files/{file_id}/entries"
    )
    assert entries_response.status_code == 404

def test_upload_unsupported_file_type(client):
    response = client.post(
        "/api/v1/files",
        data={
            "file": (
                io.BytesIO(b"some content"),
                "notes.pdf",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 415
    assert "error" in response.get_json()


def test_upload_empty_file(client):
    response = client.post(
        "/api/v1/files",
        data={
            "file": (
                io.BytesIO(b""),
                "empty.log",
            )
        },
        content_type="multipart/form-data",
    )

    # An empty file may be accepted by the current implementation.
    # Confirm its behavior without assuming a new validation rule.
    assert response.status_code in (201, 400, 415)

    if response.status_code == 201:
        data = response.get_json()["file"]
        assert data["total_lines"] == 0
        assert data["parsed_lines"] == 0
        assert data["failed_lines"] == 0


def test_upload_file_too_large(client):
    # Create a payload larger than the configured 5 MiB limit.
    oversized_content = b"a" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/api/v1/files",
        data={
            "file": (
                io.BytesIO(oversized_content),
                "oversized.log",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 413
    assert "error" in response.get_json()
