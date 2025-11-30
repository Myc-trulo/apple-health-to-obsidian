# Health Auto Export → Obsidian Guide

## ✅ What's Working Now

You're using **Health Auto Export** app on your iPhone, which exports data to iCloud Drive. This is the BEST solution because:

✅ **Automatic export** from iPhone (the only place HealthKit data exists)
✅ **iCloud sync** to your Mac
✅ **Complete data** including sleep stages, HRV, steps, everything
✅ **Works perfectly** - no macOS HealthKit limitations

## 📂 How It Works

```
iPhone (Health Auto Export App)
    ↓
Exports JSON daily
    ↓
iCloud Drive sync to Mac
    ↓
Python converter script
    ↓
Beautiful Obsidian daily notes ✨
```

## 🚀 Daily Usage

### Option 1: Run Manually (Simple)

```bash
cd ~/Developer/Obsidian/health-to-obsidian
./run.sh
```

This converts the latest Health Auto Export file to an Obsidian note.

### Option 2: Convert All Available Days

```bash
cd ~/Developer/Obsidian/health-to-obsidian/python
python3 convert_health_export.py --all
```

This converts ALL available Health Auto Export files (great for catching up!).

### Option 3: Automate It (Recommended!)

Add to cron to run automatically every morning:

```bash
# Edit crontab
crontab -e

# Add this line (runs at 8 AM daily)
0 8 * * * cd ~/Developer/Obsidian/health-to-obsidian && ./run.sh

# Or if you prefer afternoon (2 PM)
0 14 * * * cd ~/Developer/Obsidian/health-to-obsidian && ./run.sh
```

**Note:** Make sure Health Auto Export on iPhone is set to export daily (check the app settings).

## 📊 What Gets Extracted

Your daily notes now include:

### Sleep Data
- Total duration
- Deep sleep hours
- REM sleep hours
- Core sleep hours
- Awake time
- Sleep score (calculated)

### Activity Data
- Steps (with goal tracking)
- Exercise minutes
- Active calories
- Stand time
- Flights climbed

### Vitals
- HRV (Heart Rate Variability)
- Resting heart rate
- Respiratory rate
- Blood oxygen saturation

### Body Metrics
- Weight
- BMI
- Body temperature (when available)

### Calculated Scores
- **Sleep Score** (0-100): Based on duration vs. optimal 7-8h
- **Recovery Score** (0-100): Weighted combination of sleep (40%), HRV (30%), resting HR (30%)
- **Readiness Level**: HIGH / MODERATE / LOW

## 🎯 Personalized Recommendations

Each note includes:

1. **Training recommendations** based on recovery level
   - HIGH: Intense training recommended
   - MODERATE: Moderate training, listen to your body
   - LOW: Light training or rest day

2. **Sleep optimization tips**
   - Suggestions based on your actual sleep duration

3. **Blueprint Protocol checklists**
   - Supplements
   - Meal planning

## 📈 Using Dataview Queries

Your notes include a Dataview query that shows 7-day trends. In Obsidian, this will display a table with:

- Sleep score
- Recovery score
- Steps
- HRV

Over the last 7 days!

## 🔧 Configuration

Edit `python/config.json` to customize:

```json
{
  "obsidian_vault_path": "/Users/YOUR_USERNAME/Documents/ObsidianVault",
  "daily_notes_path": "1. Daily Notes"
}
```

## 🐛 Troubleshooting

### "No health export files found"
→ Check Health Auto Export app on iPhone is exporting
→ Check iCloud Drive is syncing
→ Path: `~/Library/Mobile Documents/iCloud~com~ifunography~HealthExport/Documents/New Automation`

### "Missing sleep data"
→ Some days might not have sleep data if you didn't wear your Apple Watch
→ The script handles this gracefully with "—" placeholders

### "Wrong vault path"
→ Update `config.json` with your correct Obsidian vault path

### "Dataview not working"
→ Install Dataview plugin in Obsidian
→ Settings → Community Plugins → Browse → Search "Dataview" → Install & Enable

## 🎨 Customization

Want to modify the notes? Edit:

`python/convert_health_export.py`

Look for the `generate_daily_note()` function around line 190.

You can:
- Add more health metrics
- Change the scoring formulas
- Modify the template layout
- Add custom recommendations

## 📊 Example Health Note

Your generated notes look like this:

```markdown
---
date: 2025-11-29
type: daily-health
sleep_score: 66
recovery_score: 73
readiness: MODERATE
---

# 2025-11-29 - Saturday

## 💪 Recovery & Readiness
**Recovery Score:** 73/100
**Readiness Level:** 💪 MODERATE

### Vitals
- **HRV:** 39.3 ms
- **Resting HR:** 54 bpm

## 🌙 Schlaf (Letzte Nacht)
**Score:** 66/100 🟡
**Dauer:** 5.3 Stunden

### Schlafphasen
- **Tiefschlaf:** 0.8h
- **REM:** 1.9h
- **Kernschlaf:** 2.6h

## 📊 Aktivität (Gestern)
**Schritte:** 14,539 / 10,000 ✅
**Training:** 55 Minuten
**Aktive Kalorien:** 3,320 kcal

[... and more ...]
```

## 🚀 Next Steps

1. **Open Obsidian** and check out your 7 new daily notes!
2. **Set up automation** (cron job) for daily conversion
3. **Install Dataview plugin** to see the trend table
4. **Customize the template** to your preferences
5. **Track your progress** over time!

## 💡 Pro Tips

- **Morning routine**: Set cron to run at 8 AM, then check your Obsidian note during coffee
- **Track patterns**: Use the Dataview table to spot trends in sleep/recovery
- **Adjust baselines**: Modify the scoring formulas based on YOUR personal baselines (not everyone is the same!)
- **Add custom notes**: Each generated note has sections for reflection - fill these out!

---

**You're all set!** Your health data is now flowing automatically into Obsidian. 🎉
