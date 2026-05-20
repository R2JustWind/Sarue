import geopandas as gpd
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def normalize(text):
    return unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8").lower()

def load_sectors():
    gdf = gpd.read_file(BASE_DIR / "rag" / "setoresDF.json")

    gdf["NM_SUBDIST_NORM"] = gdf["NM_SUBDIST"].fillna("").apply(normalize)
    return gdf