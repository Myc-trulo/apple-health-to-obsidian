# Health to Obsidian 🏥 → 📝

Automatic import of Apple Health data into Obsidian - using Health Auto Export app.

## ✅ Current Setup

This project converts Health Auto Export JSON files into clean, summarized health data notes in Obsidian.

### What It Does

- Reads daily health exports from Health Auto Export (iPhone app)
- Extracts key metrics: sleep, activity, vitals, body measurements
- **Includes workout details** from workout exports (duration, distance, calories, heart rate)
- Creates simple, data-only notes in Obsidian's `3. Health Data` folder
- No analysis, no scores - just raw data for you to use

## 📊 Tracked Metrics

### Sleep
- Duration, Deep, REM, Core, Awake time

### Activity
- Steps, Exercise minutes, Active calories, Flights climbed

### Vitals
- Resting heart rate, HRV, Respiratory rate, Blood oxygen

### Body
- Weight, BMI

### Workouts
- Workout name/type, Start time, Duration
- Distance (if applicable), Calories burned
- Average & max heart rate (when available)

## 🚀 Usage

### Daily Use

```bash
./run.sh
```

This converts the latest Health Auto Export file to an Obsidian note in `3. Health Data/`.

### Convert All Available Days

```bash
cd python
python3 convert_health_export.py --all
```

### Automate (Recommended)

Set up a cron job to run automatically:

```bash
crontab -e

# Add this line (runs daily at 8 AM):
0 8 * * * cd ~/Developer/Obsidian/health-to-obsidian && ./run.sh
```

## ⚙️ Configuration

Copy the example config and edit it:

```bash
cd python
cp config.json.example config.json
vim config.json  # or your preferred editor
```

Configure your settings in `python/config.json`:

```json
{
  "obsidian_vault_path": "/Users/YOUR_USERNAME/Documents/ObsidianVault",
  "health_data_path": "3. Health Data"
}
```

## 📋 Prerequisites

1. **iPhone** with Health Auto Export app installed
2. **Health Auto Export** configured to export:
   - Daily health metrics to `Gesundheitsmetriken` folder
   - Workouts to `Workouts` folder
3. **Python 3** on your Mac
4. **Obsidian** vault

## 📁 Project Structure

```
health-to-obsidian/
├── python/
│   ├── convert_health_export.py  # Main converter script
│   ├── config.json                # Configuration
│   └── requirements.txt           # Python dependencies
├── run.sh                         # Easy run script
├── README.md                      # This file
└── HEALTH_AUTO_EXPORT_GUIDE.md   # Detailed guide
```

## 📝 Output Format

Each daily note looks like this:

```markdown
---
date: 2025-11-28
type: health-data
---

# Health Data - 2025-11-28

## 🌙 Sleep
- Duration: 7.0h
- Deep Sleep: 1.3h
- REM Sleep: 1.5h
- Core Sleep: 4.3h
- Awake: 0.0h

## 👟 Activity
- Steps: 6,413
- Exercise: 88 min
- Active Calories: 3,883 kcal
- Flights Climbed: 12

## ❤️ Vitals
- Resting Heart Rate: 54 bpm
- HRV: 113.6 ms
- Respiratory Rate: 14.3 breaths/min
- Blood Oxygen: 97.5%

## 📏 Body
- Weight: 71.3 kg
- BMI: 23.6

## 🏃 Workouts

### 1. Outdoor Radfahren
- **Time:** 2025-11-28 20:10:40 +0100
- **Duration:** 5 min
- **Distance:** 1.18 km
- **Calories:** 99 kcal

### 2. Traditionelles Krafttraining
- **Time:** 2025-11-28 19:02:40 +0100
- **Duration:** 65 min
- **Calories:** 1,608 kcal
```

## 🔧 How It Works

```
Health Auto Export (iPhone)
    ↓
Exports JSON to iCloud Drive
    ↓
Mac reads from:
- ~/Library/.../HealthExport/Documents/Gesundheitsmetriken/ (health metrics)
- ~/Library/.../HealthExport/Documents/Workouts/ (workout data)
    ↓
Python script converts to markdown
    ↓
Saves to: Obsidian vault/3. Health Data/
```

## 🐛 Troubleshooting

**No health export files found?**
- Check Health Auto Export is running on iPhone
- Verify iCloud Drive is syncing
- Check path: `~/Library/Mobile Documents/iCloud~com~ifunography~HealthExport/Documents/Gesundheitsmetriken/`

**Wrong vault path?**
- Edit `python/config.json` with correct Obsidian vault location

**Missing data in notes?**
- Some metrics might not have data (e.g., no Apple Watch worn)
- Script handles this with "—" placeholders

## 💡 Notes

- **Daily notes not affected**: Health data goes to separate `3. Health Data` folder
- **Simple format**: Just raw data, no analysis or recommendations
- **Non-destructive**: Safe to run multiple times (overwrites with latest data)

## 📖 More Info

See `HEALTH_AUTO_EXPORT_GUIDE.md` for detailed setup and usage instructions.

---

**Status:** ✅ Working
**Last Updated:** 2025-11-29
