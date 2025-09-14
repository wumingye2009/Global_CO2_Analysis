# CO₂ Emissions Visualization — Data Analyst 

####
A complete, reproducible mini-project for Course 8: Data Visualization with Python.
We analyze global CO₂ emissions by country and year, build multiple visualizations (histograms, maps), and ship an interactive dashboard.
A complete, reproducible mini-project for Global CO₂ emissions by country and year, build multiple visualizations (histograms, maps), and ship an interactive dashboard.
####

##🌍 Dataset
####
Source: Kaggle (Our World in Data–style CO₂ time series)

Content: Country/year CO₂ totals with optional per-capita & sector fields

Unit: co2 is measured in million tonnes of CO₂ (MtCO₂)

Column names may vary across CSVs (e.g., Name vs Entity, co2 vs co2_including_luc). We make the notebook robust to these differences.
####

##📁 Repository Structure

####
.
├─ data/
│  ├─ co2_emissions.csv
│  └─ world-countries.json        # auto-downloaded if missing
├─ notebooks/
│  └─ Global_CO2_Analysis         # main notebook
└─ README.md
└─ requirement.txt

####

##🧰 Environment
####
*Option A: conda
conda create -n co2viz python=3.10 -y
conda activate co2viz
pip install -r requirements.txt

*Option B: pip only
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt
####

##requirements.txt
pandas
numpy
matplotlib
seaborn
plotly
jupyter-dash
dash
folium
requests

