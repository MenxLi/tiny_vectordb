THIS_DIR=$(dirname $(realpath $0))
PYTEST_ARGS=$@

# Somehow pytest does not work if we run it with a single command...
# Will seek a better solution later.
pytest ${PYTEST_ARGS} ${THIS_DIR}/test_0.py
pytest ${PYTEST_ARGS} ${THIS_DIR}/test_encoding.py
pytest ${PYTEST_ARGS} ${THIS_DIR}/test_io.py
pytest ${PYTEST_ARGS} ${THIS_DIR}/test_impl.py

python ${THIS_DIR}/_test_speed.py