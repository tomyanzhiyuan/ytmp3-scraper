# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** create a public GitHub issue for security vulnerabilities
2. Email the maintainers directly with details of the vulnerability
3. Include steps to reproduce the issue if possible
4. Allow reasonable time for the issue to be addressed before public disclosure

## Security Considerations

This application:

- Runs locally on your machine
- Does not collect or transmit personal data
- Uses YouTube's public APIs and yt-dlp for video access
- Stores downloaded files only on your local filesystem

### Best Practices

- Keep your YouTube API key private and never commit it to version control
- Use the provided `.env.example` as a template for your `.env` file
- Run the application in a secure network environment
- Keep dependencies updated to patch known vulnerabilities

## Responsible Use

This tool is intended for personal use only. Users are responsible for:

- Respecting YouTube's Terms of Service
- Only downloading content they have rights to access
- Complying with copyright laws in their jurisdiction
