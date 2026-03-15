# Usage Guide

## Basic Commands

### Shorten a URL

```bash
python main.py shorten "https://example.com/long/path"
# ✓ Created: short.ly/aB3x9Z

# Same URL again returns same code
python main.py shorten "https://example.com/long/path"
# ✓ Already shortened: short.ly/aB3x9Z
```

**URL Requirements:**
- Must start with `http://` or `https://`
- Must contain a dot (valid domain)
- Max 2000 characters

### Resolve a Short Code

```bash
python main.py resolve aB3x9Z
# → https://example.com/long/path
```

Each resolve increments the visit counter.

### List All URLs

```bash
python main.py list

# Output:
# #     LONG URL              SHORT CODE    CREATED AT           VISIT COUNT
# --------------------------------------------------------------------------
# 1     https://example.com   aB3x9Z        15-03-2026T10:30     5
```

## Advanced Usage

### Open URL in Browser

```bash
# macOS
python main.py resolve aB3x9Z | xargs open

# Linux
python main.py resolve aB3x9Z | xargs xdg-open

# Windows PowerShell
python main.py resolve aB3x9Z | %{start $_}
```

### Copy to Clipboard

```bash
# macOS
python main.py resolve aB3x9Z | pbcopy

# Linux
python main.py resolve aB3x9Z | xclip -selection clipboard
```

### Batch Shorten from File

```bash
# urls.txt contains one URL per line
while read url; do
  python main.py shorten "$url"
done < urls.txt
```

### Bash Aliases

Add to `.bashrc` or `.zshrc`:

```bash
alias us='python /path/to/main.py shorten'
alias ur='python /path/to/main.py resolve'
alias ul='python /path/to/main.py list'
```

## Error Handling

### Missing Protocol

```bash
python main.py shorten "example.com"
# ❌ URL must start with 'http://' or 'https://'
```

### URL Too Long

```bash
python main.py shorten "https://example.com/very/long/..."
# ❌ URL too long (max 2000 characters)
```

### Code Not Found

```bash
python main.py resolve "notreal"
# ❌ Short code should be exactly 6 alphanumeric characters

python main.py resolve "zzzzzz"
# ❌ Short code 'zzzzzz' not found
```

## Tips & Tricks

### Search for Specific URL

```bash
python main.py list | grep "github"
```

### Backup Data

```bash
cp urls.json urls_backup_$(date +%Y%m%d).json
```

### Clear All Data

```bash
rm urls.json
```

### View Raw JSON

```bash
cat urls.json | python -m json.tool
```

## Workflow Examples

### Share Documentation Links

```bash
# Shorten API docs
python main.py shorten "https://docs.example.com/api/auth"
# → short.ly/aUth42

# Add to README
echo "Docs: short.ly/aUth42" >> README.md
```

### Track Campaign Links

```bash
# Shorten campaign URLs
python main.py shorten "https://example.com/spring-sale"
# → short.ly/s4L3

# End of day: check visits
python main.py list
```

## Troubleshooting

### File Not Found

Normal on first run - file is created automatically.

### Permission Denied

```bash
chmod 644 urls.json
```

### Visit Count Not Incrementing

Use `resolve` command (not just `list`):

```bash
python main.py resolve aB3x9Z  # This increments
```

### Slow Performance

Check database size:

```bash
ls -lh urls.json
```

If > 2MB, consider archiving old data.

## Getting Help

```bash
python main.py --help
python main.py shorten --help
python main.py resolve --help
python main.py list --help
```

---

Happy URL shortening! 🚀