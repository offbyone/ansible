# Justfile for offbyone.ansible collection

# Default recipe
default:
    @just --list

# Install development dependencies
setup:
    mise install
    uv venv
    uv pip install -r requirements.txt
    uv pip install ${PIP_TOOLS:-ansible-lint yamllint}

# Run all tests
test: lint sanity

# Run linting checks
lint:
    yamllint .
    ansible-lint

# Run sanity checks
sanity:
    #!/bin/bash
    set -eux -o pipefail
    tempdir=$(mktemp -d)
    mkdir -p "$tempdir/ansible_collections/offbyone/ansible"
    trap 'rm -rf "$tempdir"' EXIT
    rsync -a --exclude .git --exclude .venv --exclude .jj . "$tempdir/ansible_collections/offbyone/ansible/"
    cd "$tempdir/ansible_collections/offbyone/ansible" && ansible-test sanity --docker -v

# Build the collection
build:
    ansible-galaxy collection build --force

# Install the collection locally
install: build
    @echo "Installing collection locally..."
    @ls -1 offbyone-ansible-*.tar.gz | xargs -I{} ansible-galaxy collection install {} --force

# Clean up build artifacts
clean:
    rm -rf *.tar.gz

# Validate galaxy.yml
validate-metadata:
    ansible-galaxy collection build --force --output-path /tmp/validate-build
    rm -rf /tmp/validate-build

# Release to Ansible Galaxy (requires ANSIBLE_GALAXY_API_KEY env var)
release: validate-metadata
    ansible-galaxy collection publish --api-key ${ANSIBLE_GALAXY_API_KEY} $(ls -1 offbyone-ansible-*.tar.gz | sort -V | tail -n 1)

# Check if the release would work without actually releasing
release-check: validate-metadata
    ansible-galaxy collection publish --api-key ${ANSIBLE_GALAXY_API_KEY} $(ls -1 offbyone-ansible-*.tar.gz | sort -V | tail -n 1) --dry-run

pin-actions:
    mise exec ubi:suzuki-shunsuke/pinact -- pinact run
