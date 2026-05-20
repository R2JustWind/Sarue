import pandas as pd
import geopandas as gpd
from load_ubs import load_ubs

def load_ubs_gdf():
    ubs_db = load_ubs()

    df = pd.DataFrame(ubs_db)

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['lng'], df['lat']),
        crs="EPSG:4326"
    )

    return gdf

