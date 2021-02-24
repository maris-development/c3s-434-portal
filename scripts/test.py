# UK mask
uk_mask = ct.shapes.catalogue.nuts(nuts_id='UK')
uk_mask_style = {
    'fillColor': '#ffffff',
    'fillOpacity': 1,
    'color': '#000000',
    'weight': 1,
}
uk_mask = {
    'data': ct.shapes.get_geojson(uk_mask),
    'style': uk_mask_style,
    'style_selected': uk_mask_style,
    'label_template': ' ',
}

#horizontale legende onder plot:
'legend': {
    'xanchor':'center',
    'yanchor':'top',
    'orientation':'v',
    'y':-0.15,
    'x':0.1
},