from flask import Flask, render_template, request, send_file
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io

app = Flask(__name__)

URL = "https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/colombia.geo.json"
gdf = gpd.read_file(URL)  # Se carga una sola vez al iniciar

@app.route('/')
def index():
    departamentos = sorted(gdf['NOMBRE_DPT'].tolist())
    return render_template('index.html', departamentos=departamentos)

@app.route('/mapa')
def mapa():
    seleccionados = request.args.getlist('dept')

    gdf['color'] = gdf['NOMBRE_DPT'].apply(
        lambda x: 'red' if x in seleccionados else '#CCCCCC'
    )

    fig, ax = plt.subplots(figsize=(10, 12))
    gdf.plot(ax=ax, color=gdf['color'], edgecolor='black', linewidth=0.5)

    # Nombres en el centroide
    # for _, row in gdf.iterrows():
    #    centroid = row.geometry.centroid
    #   ax.text(centroid.x, centroid.y, row['NOMBRE_DPT'],
    #            fontsize=4.5, ha='center', va='center', color='#333')

    rojo_patch = mpatches.Patch(color='red', label='Seleccionados')
    gris_patch = mpatches.Patch(color='#CCCCCC', label='Otros')
    ax.legend(handles=[rojo_patch, gris_patch], loc='lower left', fontsize=9)
    ax.set_title('Departamentos seleccionados de Colombia',
                 fontsize=14, fontweight='bold', pad=15)
    ax.axis('off')
    plt.tight_layout()

    # Devolver imagen en memoria (sin guardar archivo)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)