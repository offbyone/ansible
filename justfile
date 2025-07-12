# Justfile for offbyone.ansible collection

# Default recipe
default:
    @just --list

# Install development dependencies
setup:
    mise install
    uv pip install -r requirements.txt
    uv pip install ${PIP_TOOLS:-ansible-lint yamllint}

# Run all tests
test: lint sanity

# Run linting checks
lint:
    mise run ansible-lint
    mise run yamllint .

# Run sanity checks
sanity:
    mkdir -p /tmp/ansible_collections/offbyone/ansible
    rsync -a --exclude .git --exclude /tmp . /tmp/ansible_collections/offbyone/ansible/
    cd /tmp/ansible_collections/offbyone/ansible && mise run ansible-test sanity --docker -v

# Build the collection
build:
    mise run ansible-galaxy collection build --force

# Install the collection locally
install: build
    @echo "Installing collection locally..."
    @ls -1 offbyone-ansible-*.tar.gz | xargs -I{} mise run ansible-galaxy collection install {} --force

# Clean up build artifacts
clean:
    rm -rf *.tar.gz

# Validate galaxy.yml
validate-metadata:
    mise run ansible-galaxy collection build --force --output-path /tmp/validate-build
    rm -rf /tmp/validate-build

# Release to Ansible Galaxy (requires ANSIBLE_GALAXY_API_KEY env var)
release: validate-metadata
    mise run ansible-galaxy collection publish --api-key ${ANSIBLE_GALAXY_API_KEY} $(ls -1 offbyone-ansible-*.tar.gz | sort -V | tail -n 1)

# Check if the release would work without actually releasing
release-check: validate-metadata
    mise run ansible-galaxy collection publish --api-key ${ANSIBLE_GALAXY_API_KEY} $(ls -1 offbyone-ansible-*.tar.gz | sort -V | tail -n 1) --dry-run