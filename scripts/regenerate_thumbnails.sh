#!/bin/bash

# Regenerate invalid thumbnail images for rose-blog
# Invalid files are JSON (rate limit errors from Pollinations.ai)

THUMBNAILS_DIR="/home/scottishfoldbrothers/.openclaw/workspace/rose-blog/assets/img/thumbnails"
POSTS_DIR="/home/scottishfoldbrothers/.openclaw/workspace/rose-blog/content/posts"

# Find all invalid (non-JPEG) jpg files, excluding hello-world
INVALID_FILES=$(file "$THUMBNAILS_DIR"/*.jpg | grep -v "JPEG" | awk -F: '{print $1}' | xargs -I{} basename {})

echo "=== Invalid files to regenerate ==="
echo "$INVALID_FILES"
echo ""
echo "Total: $(echo "$INVALID_FILES" | wc -l) files"
echo ""

SUCCESS=0
FAILED=0
FAILED_LIST=""

for jpg_file in $INVALID_FILES; do
    # Extract slug (filename without .jpg)
    slug="${jpg_file%.jpg}"

    # Skip hello-world (already successful)
    if [ "$slug" = "2026-02-22-hello-world" ]; then
        echo "SKIP: $slug (hello-world excluded)"
        continue
    fi

    # Find corresponding markdown file
    md_file="$POSTS_DIR/${slug}.md"
    if [ ! -f "$md_file" ]; then
        echo "WARN: No markdown file found for $slug, skipping"
        continue
    fi

    # Extract title and tags from frontmatter
    title=$(grep '^title:' "$md_file" | head -1 | sed 's/^title: *"//' | sed 's/"$//' | sed 's/[🌹📈💰📊🔑💡⚡🏆🎯🌟]//g' | tr -d '\n')
    tags=$(grep '^tags:' "$md_file" | head -1 | sed 's/^tags: *\[//' | sed 's/\]$//' | tr -d '"' | tr ',' ' ')

    # Generate English prompt from slug keywords
    # Convert slug to readable form (remove date prefix, replace hyphens with spaces)
    slug_words=$(echo "$slug" | sed 's/^[0-9-]*-//' | tr '-' ' ')

    # Build a concise English prompt
    prompt="professional finance investment blog thumbnail, ${slug_words}, stock market chart data visualization, modern clean design, blue purple gradient, 1200x630"

    echo "=== Processing: $slug ==="
    echo "  Prompt: $prompt"

    # URL encode the prompt
    encoded_prompt=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$prompt'))")

    # Generate seed from slug for reproducibility
    seed=$(echo "$slug" | cksum | awk '{print $1}')

    output_file="$THUMBNAILS_DIR/${slug}.jpg"

    # Try up to 3 times
    MAX_RETRIES=3
    attempt=1
    success=false

    while [ $attempt -le $MAX_RETRIES ]; do
        echo "  Attempt $attempt/$MAX_RETRIES (sleeping 5s before request)..."
        sleep 5

        curl -sL \
            "https://image.pollinations.ai/prompt/${encoded_prompt}?width=1200&height=630&seed=${seed}&nologo=true" \
            -o "$output_file" \
            --max-time 60

        # Check if downloaded file is actually JPEG
        file_type=$(file "$output_file" | grep -o "JPEG\|PNG\|GIF")
        if [ -n "$file_type" ]; then
            echo "  SUCCESS: $slug ($file_type)"
            success=true
            break
        else
            echo "  FAILED attempt $attempt: got $(file "$output_file" | cut -d: -f2 | head -c 50)"
            if [ $attempt -lt $MAX_RETRIES ]; then
                echo "  Waiting 10s before retry..."
                sleep 10
            fi
        fi

        attempt=$((attempt + 1))
    done

    if $success; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
        FAILED_LIST="$FAILED_LIST $slug"
        echo "  GIVING UP on $slug after $MAX_RETRIES attempts"
    fi

    echo ""
done

echo "==================================="
echo "DONE: Success=$SUCCESS, Failed=$FAILED"
if [ -n "$FAILED_LIST" ]; then
    echo "Failed slugs:"
    for f in $FAILED_LIST; do
        echo "  - $f"
    done
fi
