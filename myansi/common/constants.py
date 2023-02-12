NAME = 'myansi'

AUTH = 'fjboy'
REPO = 'my-ansible-dashboard'
RELEASES_API = f'https://api.github.com/repos/{AUTH}/{REPO}/releases'

IMAGE_NAMESPACE = 'fjboy'
IMAGE_TAGS_API = f'https://hub.docker.com/v2/namespaces/{IMAGE_NAMESPACE}' \
                 f'/repositories/{NAME}/tags'

ANSIBLE_HOSTS = '/etc/ansible/hosts'
