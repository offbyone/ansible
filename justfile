# Justfile for offby1.ansible collection

# Default recipe
default:
    @just --list

# Install development dependencies
setup:
    mise install
    uv venv
    uv pip install -r requirements.txt

# Run all tests
test: lint sanity

# Run linting checks
[parallel]
lint: yamllint ansible-lint

yamllint:
    uv tool run yamllint .

ansible-lint:
    uv tool run ansible-lint

# Run sanity checks
sanity:
    #!/bin/bash
    set -eux -o pipefail
    tempdir=$(mktemp -d)
    mkdir -p "$tempdir/ansible_collections/offby1/ansible"
    trap 'rm -rf "$tempdir"' EXIT
    rsync -a \
        --exclude .git --exclude .venv --exclude .jj --exclude .ansible \
        . "$tempdir/ansible_collections/offby1/ansible/"
    cd "$tempdir/ansible_collections/offby1/ansible" && ansible-test sanity --docker -v

# Build the collection
build:
    ansible-galaxy collection build --force --output-path dist/

# Install the collection locally
install: build
    @echo "Installing collection locally..."
    @ansible-galaxy collection install --force $(ls -1 dist/offby1-ansible-*.tar.gz | sort -V | tail -n 1)

# Clean up build artifacts
clean:
    rm -rf *.tar.gz

# Validate galaxy.yml
validate-metadata:
    ansible-galaxy collection build --force --output-path /tmp/validate-build
    rm -rf /tmp/validate-build

# Release to Ansible Galaxy (requires ANSIBLE_GALAXY_API_KEY env var)
release: build
    ansible-galaxy collection publish --api-key ${ANSIBLE_GALAXY_API_KEY} $(ls -1 dist/offby1-ansible-*.tar.gz | sort -V | tail -n 1)

pin-actions:
    mise exec ubi:suzuki-shunsuke/pinact -- pinact run
