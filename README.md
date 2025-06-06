<h1 align="center"> map.ustp.party </h1>
<h3 align="center"> Folium Edition </h3>

This project serves as a prototype to the actual, more featured, map.ustp.party
[implementation](https://github.com/ustp-party/map) using React and Pocketbase.


# Setup 
Install `uv` for dependency management.
```bash
pip install uv
```

Install dependencies
```bash
uv sync
```

# How to Use

Create the static website as `index.html`.
```bash
uv run main.py
```

Then, open the file `index.html` or run it as a webserver.


## Customization

> [!NOTE]
> Knowledge of Python and [Folium](https://python-visualization.github.io/folium/latest/) is recommended

To customize the output, you can experiment using the provided Jupyter notebook `/notebooks/1.0-test-folium.ipynb`.
Then you can turn it into a script inside `/main.py`.
