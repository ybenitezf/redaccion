# search

Un servicio de busqueda para la redacción interna

## Ambiente de desarrollo

Config virtualenv:

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
pip install pytest pytest-cov
```

Run tests:

```bash
pytest --cov
```

Run the app:

```bash
python app.py
```
