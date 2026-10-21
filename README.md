# ⛏️ EnderScope — Minecraft Analytics

**A dark cyberpunk analytics dashboard for Minecraft Java Edition player statistics.**

EnderScope turns Minecraft's local player-statistics JSON into readable metrics, charts, and CSV exports. It runs locally with Python and does not require a paid API or a Minecraft account connection.

> **Project status:** Version 1.0 — first working dashboard  
> **Important:** Demo mode uses fictional sample data. Upload a real statistics JSON file to analyze your own gameplay.

## Features

- Cyberpunk-inspired dark UI with neon cyan and magenta accents
- Demo mode for immediate testing
- Upload a Minecraft Java Edition statistics JSON file
- Mining analytics and per-mob kill charts
- Play time, walking/sprinting distance, jumps, deaths, and other available custom statistics
- Item activity tables for broken, crafted, used, picked-up, and dropped items
- Searchable mining table
- CSV export
- Basic JSON structure and numeric-value validation
- Local processing with no paid API

## Screenshots

These are **illustrative UI previews** using fictional demo values, included so the repository has a visual preview before you run the app. The live dashboard renders its charts and tables from the bundled demo data or an uploaded Minecraft statistics JSON file.

![EnderScope dashboard overview](docs/enderscope-dashboard.png)

![EnderScope mining and inventory details](docs/enderscope-details.png)

## Requirements

- Windows 10 or 11
- Python 3.10 or newer (Python 3.11 or 3.12 recommended)
- Internet connection only for installing dependencies
- No GPU required

## Windows setup

Open **PowerShell** or **Command Prompt** and run:

```powershell
mkdir EnderScope
cd EnderScope
```

If you downloaded or cloned this repository, open the terminal in the existing `EnderScope` folder instead; do not create a second folder.

Create and activate a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

Start the dashboard:

```powershell
py -m streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`. Open it in your browser.

### Quick start without Git

1. Download the repository as a ZIP from GitHub.
2. Extract it.
3. Open a terminal in the extracted `EnderScope` folder.
4. Follow the virtual-environment, install, and run commands above.

## Use real Minecraft data

Minecraft Java Edition stores player statistics as JSON files inside a world's `stats` folder. For a single-player world, the file is commonly located at:

```text
%APPDATA%\.minecraft\saves\<world-name>\stats\<player-uuid>.json
```

To open the Minecraft folder on Windows, press `Win + R`, enter:

```text
%APPDATA%\.minecraft
```

Then open `saves`, your world folder, and `stats`. Back up the file before moving or sharing it. In EnderScope, choose **Upload JSON** in the sidebar and select the player statistics file.

**Privacy note:** the file can reveal gameplay habits and identifiers. Do not commit your personal world statistics to a public repository. Use demo data for screenshots and examples.

## What the metrics mean

- **Play time:** Minecraft's `minecraft:play_time` custom statistic is measured in ticks. The dashboard converts ticks to hours using 20 ticks per second.
- **Walking distance:** `minecraft:walk_one_cm` converted to kilometres.
- **Sprint distance:** `minecraft:sprint_one_cm` converted to kilometres.
- **Damage dealt:** Minecraft's damage statistic is shown divided by 10, matching the game's half-heart unit convention.
- **Blocks mined:** sum of the entries in `minecraft:mined`.
- **Mob kills:** sum of the entries in `minecraft:killed`. This may not exactly match the separate `minecraft:mob_kills` custom statistic.

Not every statistic is present in every file or Minecraft version. A missing statistic is treated as unavailable/zero for display, not as proof the activity never occurred.

## Project structure

```text
EnderScope/
├── app.py
├── enderscope_core.py
├── tests/
│   └── test_core.py
├── requirements.txt
├── README.md
├── .gitignore
└── sample_stats.json
```

## Tech stack

- Python
- Streamlit
- Pandas
- JSON

## Roadmap

- [x] Add automated tests for parsing and conversions
- [ ] Add a world-statistics comparison view
- [ ] Add downloadable summary reports
- [ ] Add optional historical snapshots for tracking progress over time
- [ ] Improve accessibility and responsive layout
- [ ] Add screenshots and a short demo GIF

## Run the tests

The project includes standard-library `unittest` tests for parsing, conversions, empty data, and invalid values. After installing requirements, run:

```powershell
py -m unittest discover -s tests -v
```

## Troubleshooting

**`py` is not recognized:** install Python from [python.org](https://www.python.org/downloads/windows/) and enable the option to add Python to PATH. Reopen your terminal.

**`git` is not recognized:** install [Git for Windows](https://git-scm.com/downloads) and reopen your terminal.

**`streamlit` command is not recognized:** activate `.venv` and run `py -m pip install -r requirements.txt`; then use `py -m streamlit run app.py`.

**The dashboard shows no stats:** verify that you uploaded the player `.json` file from the world's `stats` folder, not a different Minecraft JSON file.

## License

This project is released under the MIT License. See `LICENSE` if you add one before publishing.
