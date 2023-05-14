

def pytest_addoption(parser):
    parser.addoption(
        "--standalone",
        action="store_true",
        default=False,
        help="Run standalone",
    )
