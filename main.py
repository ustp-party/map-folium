import folium
import geopandas
from bs4 import BeautifulSoup
from folium.plugins import MousePosition, Search

from src.config import DATA_DIR, PROJECT_ROOT
from src.matplotlib import Color as c

USTP = [8.484975, 124.656662]
HTML_FILE = PROJECT_ROOT / "index.html"

ustp_buildings = geopandas.read_file(DATA_DIR / "ustp-buildings.geojson")
parking_spaces = geopandas.read_file(DATA_DIR / "parking-spaces.geojson")
benches = geopandas.read_file(DATA_DIR / "benches.geojson")


def main():
    m = folium.Map(location=USTP, zoom_start=19, max_zoom=22)
    folium.TileLayer("CartoDB Positron").add_to(m)
    # folium.TileLayer('CartoDB dark_matter').add_to(m)

    MousePosition(
        position="bottomleft",  # Position of coordinate box
        separator=" | ",  # Separator between lat/lon
        prefix="Coordinates:",  # Text prefix before coordinates
        num_digits=8,  # Decimal places
        lng_first=False,  # Lat first if False
    ).add_to(m)

    buildingsgeo = folium.GeoJson(
        ustp_buildings,
        name="Buildings",
        weight=0.5,
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "addr:housenumber", "building:levels"],
            aliases=["Name", "Building Number", "Levels"],
            localize=True,
        ),
    ).add_to(m)

    parkinggeo = folium.GeoJson(
        parking_spaces,
        name="Parking Spaces",
        weight=0,
        color=c.PURPLE.value,
        tooltip=folium.GeoJsonTooltip(
            fields=["vehicles"],
            aliases=["Vehicles Allowed"],
            localize=True,
        ),
    ).add_to(m)

    benchesgeo = folium.GeoJson(
        benches,
        name="Benches",
        weight=0,
        color=c.RED.value,
        tooltip=folium.GeoJsonTooltip(
            fields=["Estimated Capacity", "Has roofing", "Has backrest"],
            localize=True,
        ),
    ).add_to(m)

    buildingsearch = Search(
        layer=buildingsgeo,
        geom_type="Polygon",
        placeholder="Search for buildings",
        collapsed=False,
        search_label="name",
        position="topright",
    ).add_to(m)

    buildingsearch_no = Search(
        layer=buildingsgeo,
        geom_type="Polygon",
        placeholder="Search for building numbers",
        collapsed=False,
        search_label="addr:housenumber",
        position="topright",
    ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save(HTML_FILE)

    # Load the saved HTML
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Set the <title>
    title = soup.new_tag("title")
    title.string = "USTP-CDO Campus Map"
    soup.head.append(title)

    # Add <link rel="icon"> for the favicon
    favicon_link = soup.new_tag(
        "link",
        rel="icon",
        href="./public/ustp.map.party-64x64.png",
        type="image/png",
    )
    soup.head.append(favicon_link)

    # Save the modified HTML
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup))


if __name__ == "__main__":
    main()
