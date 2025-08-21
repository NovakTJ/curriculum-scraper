#!/bin/bash
# Simple script to upload PDF to Google Drive using rclone

PDF_FILE="merged_document.pdf"
REMOTE_NAME="gdrive"

echo "=== Google Drive PDF Upload ==="

# Check if the PDF file exists
if [ ! -f "$PDF_FILE" ]; then
    echo "❌ Error: $PDF_FILE not found!"
    exit 1
fi

# Check if rclone is configured
if ! rclone listremotes | grep -q "^${REMOTE_NAME}:$"; then
    echo "❌ Error: Google Drive remote '${REMOTE_NAME}' not configured!"
    echo ""
    echo "Please run 'rclone config' first to set up Google Drive access."
    echo "See upload_instructions.sh for detailed steps."
    exit 1
fi

# Get file size
FILE_SIZE=$(ls -lh "$PDF_FILE" | awk '{print $5}')
echo "📄 File: $PDF_FILE ($FILE_SIZE)"

# Upload the file
echo "🚀 Uploading to Google Drive..."
echo ""

if rclone copy "$PDF_FILE" "${REMOTE_NAME}:" --progress; then
    echo ""
    echo "✅ Upload completed successfully!"
    echo ""
    echo "Your file is now available in your Google Drive root folder."
    echo "You can access it at: https://drive.google.com"
    
    # Try to get the file info
    echo ""
    echo "📋 File details on Google Drive:"
    rclone lsl "${REMOTE_NAME}:$PDF_FILE" 2>/dev/null || echo "Use 'rclone ls gdrive:' to see all files"
else
    echo ""
    echo "❌ Upload failed!"
    echo "Please check your internet connection and rclone configuration."
fi
