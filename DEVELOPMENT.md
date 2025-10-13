# Development Guide

## Creating a New Release

To create and publish a new release of the `offby1.ansible` collection:

### 1. Update Version
Edit the version in `galaxy.yml`:
```yaml
version: x.y.z
```

Follow [semantic versioning](https://semver.org/):
- **Major** (x): Breaking changes
- **Minor** (y): New features, backwards compatible  
- **Patch** (z): Bug fixes, backwards compatible

### 2. Update Changelog
Add release notes to `CHANGELOG.md` documenting:
- New features
- Bug fixes
- Breaking changes
- Deprecations

### 3. Test Locally
Run the test suite to ensure everything works:
```bash
just test
```

### 4. Commit and Push
Commit your changes and push to the `main` branch:
```bash
git add galaxy.yml CHANGELOG.md
git commit -m "Release version x.y.z"
git push origin main
```

### 5. Automatic Publication
The GitHub Actions workflow will automatically:
1. Build the collection artifact
2. Publish to Ansible Galaxy
3. Make it available at `ansible-galaxy collection install offby1.ansible`

### Manual Release (if needed)
To release manually with the API key:
```bash
export ANSIBLE_GALAXY_API_KEY="your_api_key"
just release
```

## Development Setup

### Prerequisites
- [mise](https://mise.jdx.dev/) for tool management
- [just](https://github.com/casey/just) for task automation

### Setup
```bash
just setup    # Install dependencies
just test     # Run all tests
just build    # Build collection artifact
just install  # Install locally for testing
```

## Testing

### Lint and Format
```bash
just lint     # YAML and Ansible linting
```

### Sanity Tests
```bash
just sanity   # Ansible sanity tests in Docker
```

### Full Test Suite
```bash
just test     # Run all tests (lint + sanity)
```

## Collection Structure

- `plugins/inventory/` - Inventory plugins (e.g., Tailscale)
- `plugins/modules/` - Ansible modules (e.g., ubi installer)
- `roles/` - Ansible roles
- `examples/` - Example playbooks and requirements
- `meta/runtime.yml` - Collection metadata and Python requirements