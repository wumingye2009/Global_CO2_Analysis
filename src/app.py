import pathlib
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

# ---- Config ----
DATA_PATH = pathlib.Path("../data/co2_emissions.csv")  # 放你的 Kaggle CSV（重命名也行）

# 自动识别列名
COLUMN_GUESSES = {
    "country": ["country","Country","entity","Entity","name","Name"],
    "year": ["year","Year","YEAR"],
    "total_co2": ["co2","CO2","total_co2","total_emissions","emissions","Total_CO2","Total Emissions"]
}

def pick_first_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

# —— 读数据
if not DATA_PATH.exists():
    raise FileNotFoundError("Place your Kaggle CSV at ../data/co2_emissions.csv (rename if needed)")

df = pd.read_csv(DATA_PATH)

country_col = pick_first_col(df, COLUMN_GUESSES["country"])
year_col    = pick_first_col(df, COLUMN_GUESSES["year"])
total_col   = pick_first_col(df, COLUMN_GUESSES["total_co2"])
if country_col is None or year_col is None:
    raise ValueError("Could not detect country/year columns — adjust COLUMN_GUESSES")

# —— 选择可用指标
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
preferred = [c for c in [total_col, "co2_per_capita", "share_global_co2",
                         "coal_co2","oil_co2","gas_co2","cement_co2","flaring_co2"]
             if c in numeric_cols]
metrics = preferred if preferred else numeric_cols[:5]

min_year = int(pd.to_numeric(df[year_col], errors="coerce").min())
max_year = int(pd.to_numeric(df[year_col], errors="coerce").max())

# —— App
app = Dash(__name__)
app.title = "CO₂ Emissions Dashboard"

app.layout = html.Div([
    html.H2("CO₂ Emissions Dashboard"),

    html.Div([
        html.Div([
            html.Label("Metric"),
            dcc.Dropdown(
                options=[{"label": m, "value": m} for m in metrics],
                value=metrics[0],
                id="metric",
                clearable=False
            ),
        ], style={"width":"280px"}),

        html.Div([
            html.Label("Year"),
            dcc.Slider(min_year, max_year, 1, value=max_year,
                       marks=None, tooltip={"always_visible": True},
                       id="year", updatemode="drag", included=False)
        ], style={"flex":"1", "padding":"0 16px"}),

        html.Div([
            html.Label("Transform"),
            dcc.RadioItems(
                options=[{"label":"Raw","value":"raw"},
                         {"label":"log1p","value":"log1p"},
                         {"label":"zscore","value":"zscore"},
                         {"label":"minmax","value":"minmax"}],
                value="raw", id="transform", inline=True
            )
        ])
    ], style={"display":"flex","alignItems":"center","gap":"16px","maxWidth":"1000px"}),

    html.Div([
        dcc.Graph(id="hist", style={"width":"49%","display":"inline-block","height":"400px"}),
        dcc.Graph(id="map",  style={"width":"49%","display":"inline-block","height":"400px"})
    ], style={"marginTop":"12px"})
], style={"padding":"16px"})

# —— 交互
@app.callback(
    Output("hist", "figure"),
    Output("map", "figure"),
    Input("metric", "value"),
    Input("year", "value"),
    Input("transform", "value")
)
def update(metric, year, transform):
    # 年份安全转换
    try:
        year = int(year)
    except Exception:
        year = max_year

    dff = df[pd.to_numeric(df[year_col], errors="coerce") == year].copy()

    # 指标安全转换
    series = pd.to_numeric(dff[metric], errors="coerce").replace([np.inf, -np.inf], np.nan)
    dff["_metric_raw_"] = series

    # 变换
    x = series.copy()
    if transform == "log1p":
        x = np.log1p(x.clip(lower=0))
    elif transform == "zscore":
        mu, sd = np.nanmean(x), np.nanstd(x, ddof=0)
        x = (x - mu) / sd if sd > 0 else x*0
    elif transform == "minmax":
        mn, mx = np.nanmin(x), np.nanmax(x)
        x = (x - mn) / (mx - mn) if mx > mn else x*0

    dff["_metric_view_"] = x

    # —— 直方图
    fig_hist = px.histogram(
        dff.dropna(subset=["_metric_view_"]),
        x="_metric_view_", nbins=30,
        title=f"Histogram — {metric} ({year}) [{transform}]"
    )

    # —— 地图（Plotly）
    # 仅保留 country & 值，剔除空值
    map_df = dff[[country_col, "_metric_view_"]].dropna()
    fig_map = px.choropleth(
        map_df, locations=country_col, locationmode="country names",
        color="_metric_view_", hover_name=country_col,
        title=f"Choropleth — {metric} ({year}) [{transform}]",
        color_continuous_scale="YlOrRd"
    )
    fig_map.update_geos(showcountries=True, showcoastlines=True, projection_type="natural earth")
    fig_map.update_layout(margin=dict(l=0, r=0, t=50, b=0))

    return fig_hist, fig_map

if __name__ == "__main__":
    # 本地运行：python app.py
    # 浏览器打开：http://127.0.0.1:8050
    app.run(debug=True, host="127.0.0.1", port=8050)
