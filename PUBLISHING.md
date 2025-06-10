# Publishing Guide for OpenCar

## Prerequisites

1. **Create PyPI accounts:**
   - Test PyPI: https://test.pypi.org/account/register/
   - PyPI: https://pypi.org/account/register/

2. **Generate API tokens:**
   - Go to Account Settings → API tokens
   - Create tokens for both Test PyPI and PyPI
   - Store them securely

3. **Configure credentials:**
   Edit `~/.pypirc` file with your API tokens:
   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   repository = https://upload.pypi.org/legacy/
   username = __token__
   password = pypi-YOUR_API_TOKEN_HERE

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-YOUR_TEST_API_TOKEN_HERE
   ```

## Quick Publishing

### Option 1: Use the automated script
```bash
./scripts/publish.sh
```

### Option 2: Manual publishing

1. **Build the package (if not already built):**
   ```bash
   python -m build
   ```

2. **Check package integrity:**
   ```bash
   twine check dist/*
   ```

3. **Publish to Test PyPI (recommended first):**
   ```bash
   twine upload --repository testpypi dist/*
   ```

4. **Test installation from Test PyPI:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ opencar
   ```

5. **Publish to PyPI:**
   ```bash
   twine upload dist/*
   ```

## Post-Publishing

1. **Create GitHub release:**
   ```bash
   gh release create v1.0.0 dist/* --title "OpenCar v1.0.0" --notes "Production-ready autonomous vehicle perception system"
   ```

2. **Update documentation:**
   - Update installation instructions
   - Add changelog entry
   - Update version badges

3. **Announce the release:**
   - Social media
   - Developer communities
   - Project documentation

## Verification

After publishing, verify your package:

1. **Check PyPI page:** https://pypi.org/project/opencar/
2. **Test installation:** `pip install opencar`
3. **Test functionality:** `opencar --version`

## Troubleshooting

### Common Issues:

1. **Package name already exists:**
   - Change package name in `pyproject.toml`
   - Rebuild package

2. **Authentication failed:**
   - Verify API tokens
   - Check `~/.pypirc` configuration

3. **Upload failed:**
   - Ensure package passes `twine check`
   - Check network connection
   - Verify file permissions

### Support

For issues with publishing:
- Check the [PyPI documentation](https://packaging.python.org/)
- Review [Twine documentation](https://twine.readthedocs.io/)
- Contact support at nikjois@llamasearch.ai

## Security Notes

- Never commit API tokens to version control
- Use environment variables for CI/CD
- Regularly rotate API tokens
- Use 2FA on PyPI accounts 