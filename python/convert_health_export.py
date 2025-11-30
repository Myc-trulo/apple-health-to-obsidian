#!/usr/bin/env python3
"""
Convert Health Auto Export JSON files to Obsidian Daily Notes
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import re


class HealthAutoExportConverter:
    def __init__(self, config_path: str = "config.json"):
        """Initialize converter"""
        self.config = self.load_config(config_path)
        self.health_export_path = Path.home() / "Library/Mobile Documents/iCloud~com~ifunography~HealthExport/Documents/Gesundheitsmetriken"
        self.workouts_export_path = Path.home() / "Library/Mobile Documents/iCloud~com~ifunography~HealthExport/Documents/Workouts"
        self.use_summary_format = True  # Use simplified summary format

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "obsidian_vault_path": "~/Documents/Obsidian/MyVault",
                "daily_notes_path": "Daily Notes",
                "health_data_path": "3. Health Data",
            }

    def find_latest_export(self) -> Optional[Path]:
        """Find the most recent health export file"""
        if not self.health_export_path.exists():
            print(f"❌ Health Export path not found: {self.health_export_path}")
            return None

        json_files = list(self.health_export_path.glob("HealthAutoExport-*.json"))
        if not json_files:
            print("❌ No health export files found")
            return None

        # Sort by date in filename
        json_files.sort(reverse=True)
        return json_files[0]

    def get_export_for_date(self, date: datetime) -> Optional[Path]:
        """Get export file for specific date"""
        date_str = date.strftime("%Y-%m-%d")
        export_file = self.health_export_path / f"HealthAutoExport-{date_str}.json"

        if export_file.exists():
            return export_file
        return None

    def get_workout_export_for_date(self, date: datetime) -> Optional[Path]:
        """Get workout export file for specific date"""
        date_str = date.strftime("%Y-%m-%d")
        export_file = self.workouts_export_path / f"HealthAutoExport-{date_str}.json"

        if export_file.exists():
            return export_file
        return None

    def load_health_data(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse health export JSON"""
        with open(file_path, 'r') as f:
            data = json.load(f)

        return data

    def extract_metric_sum(self, metrics: List[Dict], metric_name: str) -> Optional[float]:
        """Extract and sum all values for a metric"""
        for metric in metrics:
            if metric.get('name') == metric_name:
                total = sum(item.get('qty', 0) for item in metric.get('data', []))
                return total if total > 0 else None
        return None

    def extract_metric_average(self, metrics: List[Dict], metric_name: str) -> Optional[float]:
        """Extract average value for a metric"""
        for metric in metrics:
            if metric.get('name') == metric_name:
                data = metric.get('data', [])
                if data:
                    values = [item.get('qty', 0) for item in data]
                    return sum(values) / len(values)
        return None

    def extract_metric_latest(self, metrics: List[Dict], metric_name: str) -> Optional[float]:
        """Extract latest value for a metric"""
        for metric in metrics:
            if metric.get('name') == metric_name:
                data = metric.get('data', [])
                if data:
                    # Assuming data is chronologically ordered
                    return data[-1].get('qty')
        return None

    def extract_sleep_data(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Extract sleep-related data"""
        sleep_data = {}

        for metric in metrics:
            if metric.get('name') == 'sleep_analysis':
                data = metric.get('data', [])
                if data:
                    # Health Auto Export provides pre-calculated sleep data
                    item = data[0]  # Usually one entry per day

                    sleep_data['duration_hours'] = item.get('totalSleep')
                    sleep_data['deep_sleep_hours'] = item.get('deep')
                    sleep_data['rem_sleep_hours'] = item.get('rem')
                    sleep_data['core_sleep_hours'] = item.get('core')
                    sleep_data['awake_hours'] = item.get('awake')
                    sleep_data['sleep_start'] = item.get('sleepStart')
                    sleep_data['sleep_end'] = item.get('sleepEnd')

        return sleep_data

    def calculate_sleep_score(self, sleep_hours: Optional[float]) -> Optional[int]:
        """Calculate sleep score (0-100)"""
        if sleep_hours is None:
            return None

        # Optimal sleep: 7-8 hours = 100
        # 6 hours = 75, 9 hours = 90, <5 hours = 50
        if sleep_hours >= 7 and sleep_hours <= 8:
            return 100
        elif sleep_hours >= 6 and sleep_hours < 7:
            return int(75 + (sleep_hours - 6) * 25)
        elif sleep_hours > 8 and sleep_hours <= 9:
            return int(100 - (sleep_hours - 8) * 10)
        elif sleep_hours > 9:
            return int(90 - (sleep_hours - 9) * 5)
        else:  # < 6 hours
            return int(max(30, sleep_hours / 6 * 75))

    def calculate_recovery_score(self, sleep_hours: Optional[float], hrv: Optional[float],
                                 resting_hr: Optional[float]) -> Optional[int]:
        """Calculate recovery score based on multiple factors"""
        scores = []

        # Sleep component (40%)
        if sleep_hours:
            sleep_score = self.calculate_sleep_score(sleep_hours)
            if sleep_score:
                scores.append(sleep_score * 0.4)

        # HRV component (30%)
        if hrv:
            # Assume baseline HRV of 60ms, higher is better
            hrv_score = min(100, (hrv / 60) * 100)
            scores.append(hrv_score * 0.3)

        # Resting HR component (30%)
        if resting_hr:
            # Lower is better, assume baseline of 60bpm
            hr_score = max(0, 100 - ((resting_hr - 50) * 2))
            scores.append(hr_score * 0.3)

        if scores:
            return int(sum(scores))
        return None

    def determine_readiness(self, recovery_score: Optional[int]) -> str:
        """Determine readiness level"""
        if recovery_score is None:
            return "UNKNOWN"

        if recovery_score >= 80:
            return "HIGH"
        elif recovery_score >= 60:
            return "MODERATE"
        else:
            return "LOW"

    def format_number(self, value: Optional[float], decimals: int = 0) -> str:
        """Format number for display"""
        if value is None:
            return "—"
        if decimals == 0:
            return f"{int(value):,}"
        return f"{value:.{decimals}f}"

    def extract_workouts(self, workout_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract workout summaries from workout export data"""
        workouts = []

        raw_workouts = workout_data.get('data', {}).get('workouts', [])

        for workout in raw_workouts:
            # Calculate total active energy
            active_energy_data = workout.get('activeEnergy', [])
            total_calories = sum(item.get('qty', 0) for item in active_energy_data) if active_energy_data else None

            # Parse duration (convert seconds to minutes)
            duration_seconds = workout.get('duration')
            duration_minutes = int(duration_seconds / 60) if duration_seconds else None

            # Get distance
            distance_data = workout.get('distance', {})
            distance_km = distance_data.get('qty') if isinstance(distance_data, dict) else None

            # Get heart rate data
            hr_data = workout.get('heartRateData', [])
            if hr_data:
                hr_values = [item.get('qty', 0) for item in hr_data if isinstance(item, dict)]
                avg_hr = sum(hr_values) / len(hr_values) if hr_values else None
                max_hr = max(hr_values) if hr_values else None
            else:
                avg_hr = None
                max_hr = None

            workout_summary = {
                'name': workout.get('name', 'Unknown'),
                'start': workout.get('start'),
                'duration_minutes': duration_minutes,
                'distance_km': distance_km,
                'calories': int(total_calories) if total_calories else None,
                'avg_heart_rate': int(avg_hr) if avg_hr else None,
                'max_heart_rate': int(max_hr) if max_hr else None,
            }

            workouts.append(workout_summary)

        return workouts

    def generate_summary_note(self, health_data: Dict[str, Any], date: datetime, workouts: Optional[List[Dict[str, Any]]] = None) -> str:
        """Generate simplified health data summary (no analysis)"""
        metrics = health_data.get('data', {}).get('metrics', [])
        workouts = workouts or []

        # Extract key metrics
        sleep_data = self.extract_sleep_data(metrics)
        sleep_hours = sleep_data.get('duration_hours')

        steps = self.extract_metric_sum(metrics, 'step_count')
        active_calories = self.extract_metric_sum(metrics, 'active_energy')
        exercise_minutes = self.extract_metric_sum(metrics, 'apple_exercise_time')
        flights_climbed = self.extract_metric_sum(metrics, 'flights_climbed')

        resting_hr = self.extract_metric_latest(metrics, 'resting_heart_rate')
        hrv = self.extract_metric_latest(metrics, 'heart_rate_variability')
        respiratory_rate = self.extract_metric_average(metrics, 'respiratory_rate')
        blood_oxygen = self.extract_metric_average(metrics, 'blood_oxygen_saturation')

        weight = self.extract_metric_latest(metrics, 'weight_body_mass')
        bmi = self.extract_metric_latest(metrics, 'body_mass_index')

        # Build simplified summary note
        date_str = date.strftime("%Y-%m-%d")

        note = f"""---
date: {date_str}
type: health-data
---

# Health Data - {date_str}

## 🌙 Sleep

- **Duration:** {self.format_number(sleep_hours, 1)}h
- **Deep Sleep:** {self.format_number(sleep_data.get('deep_sleep_hours'), 1)}h
- **REM Sleep:** {self.format_number(sleep_data.get('rem_sleep_hours'), 1)}h
- **Core Sleep:** {self.format_number(sleep_data.get('core_sleep_hours'), 1)}h
- **Awake:** {self.format_number(sleep_data.get('awake_hours'), 1)}h

## 👟 Activity

- **Steps:** {self.format_number(steps)}
- **Exercise:** {self.format_number(exercise_minutes)} min
- **Active Calories:** {self.format_number(active_calories)} kcal
- **Flights Climbed:** {self.format_number(flights_climbed)}

## ❤️ Vitals

- **Resting Heart Rate:** {self.format_number(resting_hr)} bpm
- **HRV:** {self.format_number(hrv, 1)} ms
- **Respiratory Rate:** {self.format_number(respiratory_rate, 1)} breaths/min
- **Blood Oxygen:** {self.format_number(blood_oxygen, 1)}%

## 📏 Body

- **Weight:** {self.format_number(weight, 1)} kg
- **BMI:** {self.format_number(bmi, 1)}
"""

        # Add workouts section if available
        if workouts:
            note += "\n## 🏃 Workouts\n\n"
            for i, workout in enumerate(workouts, 1):
                note += f"### {i}. {workout['name']}\n\n"
                note += f"- **Time:** {workout['start']}\n"
                note += f"- **Duration:** {self.format_number(workout['duration_minutes'])} min\n"

                if workout['distance_km'] is not None:
                    note += f"- **Distance:** {self.format_number(workout['distance_km'], 2)} km\n"

                note += f"- **Calories:** {self.format_number(workout['calories'])} kcal\n"

                if workout['avg_heart_rate']:
                    note += f"- **Avg HR:** {self.format_number(workout['avg_heart_rate'])} bpm\n"
                if workout['max_heart_rate']:
                    note += f"- **Max HR:** {self.format_number(workout['max_heart_rate'])} bpm\n"

                note += "\n"

        note += f"""---
*Auto-generated from Health Auto Export • {datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""

        return note

    def generate_daily_note(self, health_data: Dict[str, Any], date: datetime) -> str:
        """Generate Obsidian daily note content"""
        metrics = health_data.get('data', {}).get('metrics', [])

        # Extract key metrics
        sleep_data = self.extract_sleep_data(metrics)
        sleep_hours = sleep_data.get('duration_hours')

        steps = self.extract_metric_sum(metrics, 'step_count')
        active_calories = self.extract_metric_sum(metrics, 'active_energy')
        exercise_minutes = self.extract_metric_sum(metrics, 'apple_exercise_time')

        resting_hr = self.extract_metric_latest(metrics, 'resting_heart_rate')
        hrv = self.extract_metric_latest(metrics, 'heart_rate_variability')
        respiratory_rate = self.extract_metric_average(metrics, 'respiratory_rate')
        blood_oxygen = self.extract_metric_average(metrics, 'blood_oxygen_saturation')

        weight = self.extract_metric_latest(metrics, 'weight_body_mass')
        bmi = self.extract_metric_latest(metrics, 'body_mass_index')

        # Calculate scores
        sleep_score = self.calculate_sleep_score(sleep_hours)
        recovery_score = self.calculate_recovery_score(sleep_hours, hrv, resting_hr)
        readiness = self.determine_readiness(recovery_score)

        # Determine emojis
        readiness_emoji = {"HIGH": "🔥", "MODERATE": "💪", "LOW": "😴", "UNKNOWN": "❓"}[readiness]
        sleep_emoji = "✅" if sleep_score and sleep_score >= 80 else ("🟡" if sleep_score and sleep_score >= 60 else "🔴")
        steps_emoji = "✅" if steps and steps >= 10000 else ("🟡" if steps and steps >= 5000 else "🔴")

        # Build note
        date_str = date.strftime("%Y-%m-%d")
        day_name = date.strftime("%A")

        note = f"""---
date: {date_str}
type: daily-health
sleep_score: {sleep_score or 0}
recovery_score: {recovery_score or 0}
readiness: {readiness}
hrv: {self.format_number(hrv, 1)}
resting_hr: {self.format_number(resting_hr)}
steps: {self.format_number(steps)}
---

# {date_str} - {day_name}

## 💪 Recovery & Readiness

**Recovery Score:** {recovery_score or '—'}/100
**Readiness Level:** {readiness_emoji} {readiness}

### Vitals
- **HRV:** {self.format_number(hrv, 1)} ms
- **Resting HR:** {self.format_number(resting_hr)} bpm
- **Respiratory Rate:** {self.format_number(respiratory_rate, 1)} breaths/min
- **Blood Oxygen:** {self.format_number(blood_oxygen, 1)}%

## 🌙 Schlaf (Letzte Nacht)

**Score:** {sleep_score or '—'}/100 {sleep_emoji}
**Dauer:** {self.format_number(sleep_hours, 1)} Stunden

### Schlafphasen
- **Tiefschlaf:** {self.format_number(sleep_data.get('deep_sleep_hours'), 1)}h
- **REM:** {self.format_number(sleep_data.get('rem_sleep_hours'), 1)}h
- **Kernschlaf:** {self.format_number(sleep_data.get('core_sleep_hours'), 1)}h
- **Wach:** {self.format_number(sleep_data.get('awake_hours'), 1)}h

## 📊 Aktivität (Gestern)

**Schritte:** {self.format_number(steps)} / 10,000 {steps_emoji}
**Training:** {self.format_number(exercise_minutes)} Minuten
**Aktive Kalorien:** {self.format_number(active_calories)} kcal

## 📏 Körper

- **Gewicht:** {self.format_number(weight, 1)} kg
- **BMI:** {self.format_number(bmi, 1)}

## 🎯 Heute's Empfehlungen

### 💪 Training
"""

        if readiness == "HIGH":
            note += """- Intensives Training empfohlen - Du bist gut erholt! 🔥
- Ideal für: HIIT, Heavy Lifting, Long Runs
"""
        elif readiness == "MODERATE":
            note += """- Moderates Training empfohlen - Höre auf deinen Körper 💪
- Ideal für: Techniktraining, moderates Cardio
"""
        else:
            note += """- Leichtes Training oder Ruhetag empfohlen 😴
- Fokus auf Recovery: Mobility, Yoga, Spaziergang
"""

        note += """
### 🌙 Schlaf Optimierung
"""

        if sleep_hours and sleep_hours < 7:
            note += f"- Ziel: Früher ins Bett (aktuell {self.format_number(sleep_hours, 1)}h → Ziel: 7-8h)\n"
        elif sleep_hours and sleep_hours > 9:
            note += f"- Du hast viel geschlafen ({self.format_number(sleep_hours, 1)}h) - Achte auf Schlafqualität\n"
        else:
            note += "- Schlaf war gut - Routine beibehalten ✅\n"

        note += """
### 💊 Supplements (Blueprint)

- [ ] Blueprint Essentials (morgens)
- [ ] Omega-3 EPA/DHA (2g)
- [ ] Vitamin D3 (2000 IU)
- [ ] Magnesium (400mg, abends)
- [ ] Kreatin (5g)

### 🥗 Ernährung

**Meal 1 (7:00)** - Super Veggie
- [ ] 500g Gemüse
- [ ] Olivenöl extra virgin
- [ ] Nüsse & Samen

**Meal 2 (11:00)** - Nutty Pudding
- [ ] Walnüsse
- [ ] Leinsamen
- [ ] Beeren

**Meal 3 (17:00)** - Hauptmahlzeit
- [ ] Gemüse (500g+)
- [ ] Hülsenfrüchte/Tofu
- [ ] Vollkorngetreide

## 📊 7-Tage Trends

```dataview
TABLE
    sleep_score as "💤 Schlaf",
    recovery_score as "🎯 Recovery",
    steps as "👟 Schritte",
    hrv as "❤️ HRV"
FROM "Daily Notes"
WHERE type = "daily-health"
SORT date DESC
LIMIT 7
```

## 📝 Notizen & Reflexionen

### Wie fühle ich mich heute?


### Was ist heute wichtig?


### Learnings


---
*Automatisch generiert von Health Auto Export → Obsidian*
*Exportiert: {datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""

        return note

    def convert_latest(self):
        """Convert the latest health export to Obsidian note"""
        print("🏥 Health Auto Export → Obsidian Converter")
        print("=" * 60)

        # Find latest export
        export_file = self.find_latest_export()
        if not export_file:
            return

        print(f"📂 Found export: {export_file.name}")

        # Extract date from filename
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', export_file.name)
        if not date_match:
            print("❌ Could not extract date from filename")
            return

        date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
        print(f"📅 Date: {date.strftime('%Y-%m-%d')}")

        # Load health data
        health_data = self.load_health_data(export_file)
        print(f"✅ Loaded health data")

        # Load workout data if available
        workouts = []
        workout_file = self.get_workout_export_for_date(date)
        if workout_file:
            workout_data = self.load_health_data(workout_file)
            workouts = self.extract_workouts(workout_data)
            print(f"✅ Loaded {len(workouts)} workout(s)")
        else:
            print(f"ℹ️  No workout data found")

        # Generate note
        note_content = self.generate_summary_note(health_data, date, workouts)

        # Save to Obsidian Health Data folder
        vault_path = Path(self.config['obsidian_vault_path']).expanduser()
        health_data_path = vault_path / self.config.get('health_data_path', '3. Health Data')
        health_data_path.mkdir(parents=True, exist_ok=True)

        filename = date.strftime("%Y-%m-%d") + ".md"
        note_path = health_data_path / filename

        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note_content)

        print(f"✅ Health Data created: {note_path}")
        print("\n" + "=" * 60)
        print("🎉 Done! Check your Obsidian vault.")

    def convert_all(self):
        """Convert all available health exports"""
        print("🏥 Converting ALL Health Auto Export files")
        print("=" * 60)

        json_files = list(self.health_export_path.glob("HealthAutoExport-*.json"))
        print(f"📂 Found {len(json_files)} export files\n")

        for export_file in sorted(json_files):
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', export_file.name)
            if not date_match:
                continue

            date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
            print(f"Processing {date.strftime('%Y-%m-%d')}...", end=" ")

            try:
                health_data = self.load_health_data(export_file)

                # Load workout data if available
                workouts = []
                workout_file = self.get_workout_export_for_date(date)
                if workout_file:
                    workout_data = self.load_health_data(workout_file)
                    workouts = self.extract_workouts(workout_data)

                note_content = self.generate_summary_note(health_data, date, workouts)

                vault_path = Path(self.config['obsidian_vault_path']).expanduser()
                health_data_path = vault_path / self.config.get('health_data_path', '3. Health Data')
                health_data_path.mkdir(parents=True, exist_ok=True)

                filename = date.strftime("%Y-%m-%d") + ".md"
                note_path = health_data_path / filename

                with open(note_path, 'w', encoding='utf-8') as f:
                    f.write(note_content)

                print("✅")
            except Exception as e:
                print(f"❌ {e}")

        print("\n" + "=" * 60)
        print(f"🎉 Done! Converted {len(json_files)} files.")


def main():
    converter = HealthAutoExportConverter()

    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        converter.convert_all()
    else:
        converter.convert_latest()


if __name__ == "__main__":
    main()
