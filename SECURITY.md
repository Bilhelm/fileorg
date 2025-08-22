# Security Policy

## Verifying Code Authenticity

This project is maintained by William Cloutman. To ensure you're running authentic, unmodified code:

### 1. Verify File Checksums

Check that downloaded files match the expected checksums:

```bash
# Download the checksums file
curl -O https://raw.githubusercontent.com/Bilhelm/fileorg/master/checksums.txt

# Verify the main script
sha256sum -c checksums.txt
```

Expected checksums (as of last update):
- `file_organizer.py`: f3df860539c90f3ccd6818c0bd8cc12a9e29df2cb3b00ac070c3dd70eb58b2c9

### 2. Use the Secure Installer

The `install_secure.sh` script includes built-in checksum verification:

```bash
curl -O https://raw.githubusercontent.com/Bilhelm/fileorg/master/install_secure.sh
chmod +x install_secure.sh
./install_secure.sh
```

### 3. Verify Git Commits (Once GPG is Set Up)

When GPG signing is enabled, verify commits with:

```bash
git log --show-signature
```

## Security Considerations

### What This Tool Does
- ✅ Reads file metadata in specified directories
- ✅ Moves files to organized folders
- ✅ Creates log files for audit trails
- ✅ Provides dry-run mode for safe testing

### What This Tool Does NOT Do
- ❌ No network connections
- ❌ No data collection or telemetry
- ❌ No modification of system files
- ❌ No execution of external commands
- ❌ No reading of file contents (only names/types)

### Safe Usage Guidelines

1. **Always use dry-run mode first**
   ```bash
   python3 file_organizer.py
   # Choose option 1 (Preview)
   ```

2. **Review the source code**
   - The script is under 200 lines
   - All operations are clearly documented
   - No obfuscated or suspicious code

3. **Check file permissions**
   - The script only needs read/write access to the target directory
   - No elevated privileges required

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email: wcloutman@hotmail.com
3. Include:
   - Description of the issue
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Update Policy

- Checksums are updated with each release
- Security patches are prioritized
- Breaking changes are clearly documented

## Author

William Cloutman
- Email: wcloutman@hotmail.com
- GitHub: @Bilhelm

---

Last Security Review: August 2025
Next Scheduled Review: February 2026