install:
    uv sync --dev --extra streamlit --extra jupyter --frozen
    npm --prefix frontend install

test:
    uv run pytest tests/unit && uv run pytest tests/integration

playground:
    PYTHONPATH=. uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
    PYTHONPATH=. uv run streamlit run frontend/streamlit_app.py --browser.serverAddress=localhost --server.enableCORS=false --server.enableXsrfProtection=false

backend:
    uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload

ui:
    uv run streamlit run frontend/streamlit_app.py --browser.serverAddress=localhost --server.enableCORS=false --server.enableXsrfProtection=false

lint:
    uv run codespell
    uv run ruff check . --diff
    uv run ruff format . --check --diff
    uv run mypy .

logs:
    PYTHONPATH=. uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload --log-level debug --log-file logs/app.log
    PYTHONPATH=. uv run streamlit run frontend/streamlit_app.py --browser.serverAddress=localhost --server.enableCORS=false --server.enableXsrfProtection=false --log.level debug --log.file logs/streamlit.log
	


