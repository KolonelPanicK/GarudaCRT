# Validation

The source preset was exported from the original working Garuda installation.

Installer checks passed in an isolated temporary-data test with mocked system dependencies:
- Installs the named profile and launcher.
- Retains an existing custom profile and unrelated settings.
- Applies exported 60% scale.
- Generated launcher passes shell syntax validation.
- Refuses a duplicate managed install.
- Restores the original settings exactly.
- Removes only the managed launcher/assets and retains recovery backups.

No graphical Garuda session was available for end-to-end installer testing. Use the README verification steps after installation.
