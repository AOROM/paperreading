# Security Policy

This project processes local papers and Excel workbooks. Treat those files as confidential unless their owner explicitly authorizes publication.

## Reporting

Use GitHub private vulnerability reporting when it is available. Otherwise, open a minimal issue that contains no exploit secret, real workbook, copyrighted paper, credential, email address, or personal filesystem path, and ask the maintainer for a private channel.

## Safety expectations

- Never commit API keys, tokens, real research workbooks, or unpublished papers.
- Test workbook mutations on synthetic data.
- Preserve the backup, temporary-save validation, and atomic-replacement safeguards.
- Treat journal rankings and other external classifications as versioned evidence, not timeless facts.
