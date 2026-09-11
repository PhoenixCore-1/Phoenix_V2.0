from phoenix_core.runtime import CoreRuntime, build_runtime


def test_build_runtime_composes_core_boundaries(tmp_path):
    runtime = build_runtime(tmp_path / "core.db")

    try:
        assert isinstance(runtime, CoreRuntime)
        assert runtime.db is not None
        assert runtime.service.db is runtime.db
        assert runtime.api.db is runtime.db
        assert runtime.api.core_service is runtime.service
        assert runtime.integration.api is runtime.api
        assert runtime.db.integrity_check() is True
    finally:
        runtime.close()
