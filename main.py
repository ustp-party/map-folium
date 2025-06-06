import folium
import geopandas
import polars as pl
from bs4 import BeautifulSoup
from folium.plugins import MousePosition, Search
from shapely.geometry import Polygon

from src.config import DATA_DIR, PROJECT_ROOT
from src.matplotlib import Color as c

USTP = [8.484975, 124.656662]
HTML_FILE = PROJECT_ROOT / "index.html"
ASSETS_DIR = PROJECT_ROOT / "src" / "assets"

ustp_buildings = geopandas.read_file(DATA_DIR / "ustp-buildings.geojson")
parking_spaces = geopandas.read_file(DATA_DIR / "parking-spaces.geojson")
benches = geopandas.read_file(DATA_DIR / "benches.geojson")
pois = pl.read_csv(DATA_DIR / "points-of-interest.csv")


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

    ## USTP Buildings
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

    ## Parking Spaces
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
    )

    for row in parking_spaces.itertuples():
        location = Polygon(row[-1]).centroid
        parkinggeo.add_child(
            folium.Marker(
                location=[location.y, location.x],
                icon=folium.CustomIcon(
                    str(ASSETS_DIR / "flaticon" / "parking.png"), icon_size=(24, 24)
                ),
                tooltip=folium.Tooltip(
                    f"<b>Parking Space</b><br><b>Vehicles Allowed:</b> {row.vehicles}",
                    sticky=True,
                ),
            )
        )

    parkinggeo.add_to(m)

    ## Benches
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

    ## Points of Interest (POI) Groups
    def make_group(
        group_name: str, data: pl.DataFrame, color, poi_type, icon, show=True
    ):

        group = folium.FeatureGroup(name=group_name, show=show)

        filtered_data = data.filter(pl.col("type") == poi_type)
        for row in filtered_data.iter_rows():

            tooltip_html = f"""
            <div style="width: fit-content; text-align: left;">
                <div style="text-decoration: underline; font-weight: bold;">{group_name}</div><br>
                <div style="width: 100%; display: grid; grid-template-columns: 1fr 1fr; gap: 1em;">
                    <div style="display: flex; flex-direction: column;">
                        <span><b>Description</b></span>
                        <span><b>Level</b></span>
                    </div>
                    <div style="display: flex; flex-direction: column;">
                        <span>{row[1]}</span>
                        <span>{row[3]}</span>
                    </div>
                </div>
            </div>
            """

            if type(icon) is str:
                icon = folium.Icon(
                    icon=icon,
                    color=color,
                    prefix="fa",
                )

            group.add_child(
                folium.Marker(
                    location=[row[-2], row[-1]],
                    icon=icon,
                    tooltip=folium.Tooltip(
                        tooltip_html,
                        sticky=True,
                    ),
                )
            )

        return group

    make_group("Services", pois, "gray", "Printing Service", "print", show=True).add_to(
        m
    )

    make_group(
        "Landmarks",
        pois,
        "red",
        "Landmark",
        "star",
    ).add_to(m)

    make_group(
        "Public Restrooms",
        pois,
        "red",
        "Restroom",
        folium.CustomIcon(
            str(ASSETS_DIR / "flaticon" / "sign.png"), icon_size=(24, 24)
        ),
    ).add_to(m)

    ### SEARCH

    ## Search for buildings and building numbers
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

    ## Appending custom HTML elements
    # Load the saved HTML
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Set the <title>
    title = soup.new_tag("title")
    title.string = "USTP-CDO Campus Map"
    soup.head.append(title)

    # Add <link rel="icon"> for the favicon
    favicon_link = soup.new_tag(
        "link", rel="icon", href="./public/ustp.map.party-64x64.png", type="image/png"
    )
    soup.head.append(favicon_link)

    # Save the modified HTML
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup))


if __name__ == "__main__":
    main()
