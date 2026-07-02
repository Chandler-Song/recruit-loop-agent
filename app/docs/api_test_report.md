# Recruit Loop Agent API 测试报告

**生成时间**: 2026-07-01 08:17:41

## 测试环境说明

- **测试框架**: pytest + pytest-asyncio
- **HTTP 客户端**: httpx.AsyncClient
- **数据库**: SQLite (内存模式)
- **测试目标**: FastAPI 应用所有 API 接口

## 测试执行摘要

- **总测试用例数**: 0
- **通过**: 0
- **失败**: 0
- **跳过**: 0
- **通过率**: 0.00%

## 各模块测试详情

## 完整测试输出

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Users/a1-6/Downloads/2026/202607/20260701/recruit-loop-agent/venv/bin/python3
cachedir: .pytest_cache
rootdir: /Users/a1-6/Downloads/2026/202607/20260701/recruit-loop-agent/app
plugins: asyncio-1.2.0, anyio-3.7.1
asyncio: mode=strict, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 0 items

=============================== warnings summary ===============================
database/base.py:4
  /Users/a1-6/Downloads/2026/202607/20260701/recruit-loop-agent/app/database/base.py:4: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base: DeclarativeMeta = declarative_base()

../venv/lib/python3.9/site-packages/pydantic/_internal/_config.py:268
../venv/lib/python3.9/site-packages/pydantic/_internal/_config.py:268
../venv/lib/python3.9/site-packages/pydantic/_internal/_config.py:268
../venv/lib/python3.9/site-packages/pydantic/_internal/_config.py:268
  /Users/a1-6/Downloads/2026/202607/20260701/recruit-loop-agent/venv/lib/python3.9/site-packages/pydantic/_internal/_config.py:268: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.5/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

main.py:66
  /Users/a1-6/Downloads/2026/202607/20260701/recruit-loop-agent/app/main.py:66: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

../venv/lib/python3.9/site-packages/fastapi/applications.py:4547
  /Users/a1-6/Downloads/2026/202607/20260701/recruit-loop-agent/venv/lib/python3.9/site-packages/fastapi/applications.py:4547: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================= 7 warnings in 0.00s ==============================

```
