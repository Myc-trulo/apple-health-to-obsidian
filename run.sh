#!/bin/bash

# Health to Obsidian - Run Script
# Converts Health Auto Export JSON files to Obsidian Daily Notes

echo "🏥 Health to Obsidian - Starting..."
echo "=================================="
echo ""

# Change to script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/python"

# Check if config exists
if [ ! -f "config.json" ]; then
    echo "❌ config.json nicht gefunden!"
    echo "Bitte erstelle config.json basierend auf config.json.example:"
    echo "  cp config.json.example config.json"
    echo "  vim config.json  # Passe obsidian_vault_path an"
    exit 1
fi

# Run converter script
python3 convert_health_export.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ Erfolgreich abgeschlossen!"
    echo ""
    echo "📍 Öffne Obsidian um deine Daily Note zu sehen"
else
    echo ""
    echo "=================================="
    echo "❌ Fehler beim Ausführen"
    echo ""
    echo "Troubleshooting:"
    echo "1. Prüfe HealthKit Berechtigungen in Systemeinstellungen"
    echo "2. Stelle sicher, dass Health Daten verfügbar sind"
    echo "3. Validiere config.json"
    exit 1
fi
