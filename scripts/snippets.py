# UK mask
uk_nuts = ct.shapes.catalogue.nuts(nuts_id='UK')
uk_mask_style = {
    'fillColor': '#ffffff',
    'fillOpacity': 1,
    'color': '#000000',
    'weight': 1,
}
uk_mask = {
    'data': ct.shapes.get_geojson(uk_nuts),
    'style': uk_mask_style,
    'style_selected': uk_mask_style,
    'label_template': ' ',
}

# horizontale legende onder plot:
'legend': {
    'xanchor': 'center',
    'yanchor': 'top',
    'orientation': 'v',
    'y': -0.15,
    'x': 0.1
},

# Kosovo nuts mask:
NON_NUTS = ['Kosovo', 'Bosnia and Herzegovina']
KOSOVO_ATTRIBUTES = {
    '_cds_toolbox_aux_wms_filters': "{'NAME_EN': ['Kosovo']}",
}
NON_KOSOVO = ', '.join('"{}"'.format(c) for c in NON_NUTS if c != 'Kosovo')
NON_KOSOVO_ATTRIBUTES = {
    '_cds_toolbox_aux_wms_filters': f"{{'NAME_EN': [{NON_KOSOVO}]}}",
}


def avg_nuts():
    # .... #
    non_nuts = ct.shapes.catalogue.countries(name=NON_NUTS)
    data_year_nuts_non = ct.shapes.average(data, non_nuts)

    return data_nuts_mean, data_year_nuts_non


def plot_shapes():
    # plot animated series of maps if required, otherwise the temporal average
    if create_anim == True:
        mapdata = darray[0]
        mapdata_non_nuts = darray[3]
    else:
        mapdata = ct.cube.average(darray[0], dim='time')
        mapdata_non_nuts = ct.cube.average(darray[3], dim='time')

    mapdata_non_nuts = ct.cdm.update_attributes(mapdata_non_nuts,
                                                {'cds_magics_style_name': mystyle, })

    #get countries
    countries = ct.cdm.get_coordinates(mapdata_non_nuts)['countries']['data']
    # kosovo without coutnries
    kosovo_mask = mapdata_non_nuts - mapdata_non_nuts + \
        [c == 'KOS' for c in countries]
    # countries without kosovo
    non_kosovo_mask = mapdata_non_nuts - \
        mapdata_non_nuts + [c != 'KOS' for c in countries]

    kosovo = ct.cube.where(kosovo_mask, mapdata_non_nuts, drop=True)
    kosovo = ct.cdm.update_attributes(kosovo, KOSOVO_ATTRIBUTES)

    mapdata_non_nuts = ct.cube.where(
        non_kosovo_mask, mapdata_non_nuts, drop=True)

    mapdata_non_nuts = ct.cdm.update_attributes(
        mapdata_non_nuts, NON_KOSOVO_ATTRIBUTES)

    livemap_data = [
            ...
            {
            'data': mapdata_non_nuts,  # darray[0],
            "click_kwargs": {
                "ensarray1": darray[3],
                "ensarray2": darray[4],
                "ensarray3": darray[5],
                "climarray1":darray2[4],
                "climarray2":darray2[5],
                "climarray3":darray2[6],
                "climarray4":darray2[7],
                # "nutslev":nutslevel,
                "var":var,
                "scen":exp,
                "mon":mon
            },
            'label': var,
            'label_template': '%{name} %{value:.1f}',
            # 'cmap': 'viridis',
            # 'bins': 25,
            'checked': True,
            'zoom_to_selected':False,
            'date_format':'yyyy',
            'type':'layer',
        },
        {
            'data': kosovo,  # darray[0],
            "click_kwargs": {
                "ensarray1": darray[3],
                "ensarray2": darray[4],
                "ensarray3": darray[5],
                "climarray1":darray2[4],
                "climarray2":darray2[5],
                "climarray3":darray2[6],
                "climarray4":darray2[7],
                # "nutslev":nutslevel,
                "var":var,
                "scen":exp,
                "mon":mon
            },
            'label': var,
            'label_template': 'Kosovo (under UNSCR 1244/99) %{value:.1f}',
            # 'cmap': 'viridis',
            # 'bins': 25,
            'checked': True,
            'zoom_to_selected':False,
            'date_format':'yyyy',
            'type':'layer',
        },
    ]



    fig = ct.livemap.plot(livemap_data+[uk_mask, legend_data], show_legend=True,  # _enable_geoserver=True,
                          date_format='yyyy', crs='EPSG3857', min_zoom=3, zoom=3,)

    return fig