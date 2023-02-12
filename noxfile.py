import nox


@nox.session
def flake8(session):
    session.install("flake8")
    session.run("flake8", "myansi", 'noxfile.py', 'install')


@nox.session(name='pytest')
def test(session):
    session.install('pytest')
    session.install('-r', 'requirements.txt', '-r', 'test-requirements.txt')

    test_files = session.posargs or ['tests']
    session.run('pytest', *test_files)
