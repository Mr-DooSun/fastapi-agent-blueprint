import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

_REQUIRED_VARS = {
    "ADMIN_ID": "admin",
    "ADMIN_PASSWORD": "admin",
    "ADMIN_STORAGE_SECRET": "change-me-in-production",
    "DATABASE_ENGINE": "postgresql",
    "DATABASE_USER": "postgres",
    "DATABASE_PASSWORD": "postgres",
    "DATABASE_HOST": "localhost",
    "DATABASE_PORT": "5432",
    "DATABASE_NAME": "postgres",
    "AWS_SQS_ACCESS_KEY": "test-key",
    "AWS_SQS_SECRET_KEY": "test-secret",
    "AWS_SQS_URL": "https://sqs.ap-northeast-2.amazonaws.com/123/test",
}


def _make_safe_env(env_name: str = "prod") -> dict[str, str]:
    return {
        **_REQUIRED_VARS,
        "ENV": env_name,
        "ADMIN_ID": "prod-admin",
        "ADMIN_PASSWORD": "s3cure-p@ss!",
        "ADMIN_STORAGE_SECRET": "a-real-secret-key-here",
        "DATABASE_USER": "app_user",
        "DATABASE_PASSWORD": "db-s3cure-p@ss",
        "DATABASE_HOST": "db.internal.example.com",
        "DATABASE_NAME": "myapp_db",
        "TASK_NAME_PREFIX": "myapp",
    }


def _create_settings():
    from src._core.config import Settings

    return Settings()


class TestLocalEnv:
    def test_local_env_accepts_required_fields(self):
        env = {"ENV": "local", **_REQUIRED_VARS}
        with patch.dict(os.environ, env, clear=True):
            s = _create_settings()
            assert s.env == "local"
            assert s.database_engine == "postgresql"
            assert s.database_host == "localhost"

    def test_dev_env_accepts_required_fields(self):
        env = {"ENV": "dev", **_REQUIRED_VARS}
        with patch.dict(os.environ, env, clear=True):
            s = _create_settings()
            assert s.env == "dev"

    def test_test_env_is_rejected(self):
        env = {"ENV": "test", **_REQUIRED_VARS}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValidationError, match="Unknown environment"):
                _create_settings()


class TestStrictEnvRejectsUnsafeDefaults:
    @pytest.mark.parametrize("env_name", ["prod", "stg"])
    @pytest.mark.parametrize(
        "field_name,unsafe_value",
        [
            ("ADMIN_PASSWORD", "admin"),
            ("ADMIN_STORAGE_SECRET", "change-me-in-production"),
            ("DATABASE_PASSWORD", "postgres"),
            ("DATABASE_HOST", "localhost"),
        ],
    )
    def test_strict_env_rejects_each_unsafe_default(
        self, env_name, field_name, unsafe_value
    ):
        safe_env = _make_safe_env(env_name)
        safe_env[field_name] = unsafe_value
        with patch.dict(os.environ, safe_env, clear=True):
            with pytest.raises(ValidationError, match=field_name.lower()):
                _create_settings()

    @pytest.mark.parametrize("env_name", ["prod", "stg"])
    def test_strict_env_passes_with_safe_values(self, env_name):
        with patch.dict(os.environ, _make_safe_env(env_name), clear=True):
            s = _create_settings()
            assert s.env == env_name

    def test_all_errors_reported_at_once(self):
        env = {"ENV": "prod", **_REQUIRED_VARS}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                _create_settings()
            error_message = str(exc_info.value)
            assert "4 error(s)" in error_message


class TestUnknownEnv:
    def test_unknown_env_rejected(self):
        env = {"ENV": "production", **_REQUIRED_VARS}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValidationError, match="Unknown environment"):
                _create_settings()

    @pytest.mark.parametrize("env_val", ["PROD", "Prod", "prod"])
    def test_env_case_insensitive(self, env_val):
        safe = _make_safe_env()
        safe["ENV"] = env_val
        with patch.dict(os.environ, safe, clear=True):
            s = _create_settings()
            assert s.env == env_val


class TestPartialConfigGroups:
    def test_partial_s3_rejected(self):
        env = {"ENV": "local", "S3_ACCESS_KEY": "foo", **_REQUIRED_VARS}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValidationError, match=r"S3.*Partial configuration"):
                _create_settings()

    def test_complete_s3_accepted(self):
        env = {
            "ENV": "local",
            "S3_ACCESS_KEY": "key",
            "S3_SECRET_KEY": "secret",
            "S3_REGION": "us-east-1",
            "S3_BUCKET_NAME": "bucket",
            **_REQUIRED_VARS,
        }
        with patch.dict(os.environ, env, clear=True):
            s = _create_settings()
            assert s.s3_access_key == "key"

    def test_partial_minio_rejected(self):
        env = {"ENV": "local", "MINIO_HOST": "localhost", **_REQUIRED_VARS}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValidationError, match=r"MinIO.*Partial configuration"):
                _create_settings()

    def test_complete_minio_accepted(self):
        env = {
            "ENV": "local",
            "MINIO_HOST": "localhost",
            "MINIO_PORT": "9000",
            "MINIO_ACCESS_KEY": "key",
            "MINIO_SECRET_KEY": "secret",
            "MINIO_BUCKET_NAME": "bucket",
            **_REQUIRED_VARS,
        }
        with patch.dict(os.environ, env, clear=True):
            s = _create_settings()
            assert s.minio_host == "localhost"

    def test_no_s3_no_minio_accepted(self):
        env = {"ENV": "local", **_REQUIRED_VARS}
        with patch.dict(os.environ, env, clear=True):
            s = _create_settings()
            assert s.s3_access_key is None
            assert s.minio_host is None

    def test_partial_dynamodb_rejected(self):
        env = {"ENV": "local", "DYNAMODB_REGION": "ap-northeast-2", **_REQUIRED_VARS}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(
                ValidationError, match=r"DynamoDB.*Partial configuration"
            ):
                _create_settings()

    def test_complete_dynamodb_accepted(self):
        env = {
            "ENV": "local",
            "DYNAMODB_REGION": "ap-northeast-2",
            "DYNAMODB_ACCESS_KEY": "key",
            "DYNAMODB_SECRET_KEY": "secret",
            **_REQUIRED_VARS,
        }
        with patch.dict(os.environ, env, clear=True):
            s = _create_settings()
            assert s.dynamodb_region == "ap-northeast-2"

    def test_no_dynamodb_accepted(self):
        env = {"ENV": "local", **_REQUIRED_VARS}
        with patch.dict(os.environ, env, clear=True):
            s = _create_settings()
            assert s.dynamodb_region is None


class TestWarnDefaults:
    def test_task_name_prefix_warns_in_strict_env(self):
        safe = _make_safe_env("prod")
        safe["TASK_NAME_PREFIX"] = "my-project"
        with patch.dict(os.environ, safe, clear=True):
            with pytest.warns(UserWarning, match="task_name_prefix"):
                _create_settings()

    def test_task_name_prefix_no_warn_in_local(self):
        env = {"ENV": "local", **_REQUIRED_VARS}
        with patch.dict(os.environ, env, clear=True):
            import warnings

            with warnings.catch_warnings():
                warnings.simplefilter("error")
                _create_settings()
