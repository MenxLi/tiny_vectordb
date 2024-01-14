THIS_DIR=$(dirname $(realpath $0))

# Somehow pytest does not work if we run it with a single command...
# Will seek a better solution later.
pytest -s ${THIS_DIR}/test_0.py
pytest -s ${THIS_DIR}/test_encoding.py
pytest -s ${THIS_DIR}/test_io.py