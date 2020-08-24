from utils.access_labels import mgra_labels


def update_acreage(mgras, selected_ID, new_acreage,
                   product_type_developed_key, product_type_vacant_key):

    mgras.loc[
        mgras[mgra_labels.MGRA] == selected_ID, [
            product_type_developed_key, mgra_labels.DEVELOPED_ACRES
        ]
    ] += new_acreage
    mgras.loc[
        mgras[mgra_labels.MGRA] == selected_ID, [
            product_type_vacant_key, mgra_labels.VACANT_ACRES]
    ] -= new_acreage


def add_to_columns(mgras, selected_ID, value, columns):
    '''
        value: number to add to the current values of columns
        columns: list of column labels
    '''
    mgras.loc[mgras[mgra_labels.MGRA] == selected_ID, columns] += value


def update_mgra(mgras, selected_ID,
                new_units, product_type_labels):
    square_feet_per_unit = product_type_labels.unit_sqft_parameter()
    acreage_per_unit = product_type_labels.land_use_per_unit_parameter()
    # update unit counts
    columns_needing_new_units = []
    columns_needing_new_units.append(product_type_labels.total_units)
    if product_type_labels.is_residential():
        columns_needing_new_units.append(mgra_labels.HOUSING_UNITS)
    else:  # product type is non-residential
        columns_needing_new_units.append(mgra_labels.TOTAL_JOB_SPACES)
    add_to_columns(mgras, selected_ID, new_units,
                   columns_needing_new_units)
    # update acreages
    update_acreage(mgras, selected_ID,
                   acreage_per_unit * new_units,
                   product_type_labels.developed_acres,
                   product_type_labels.vacant_acres)
    # update square footages
    add_to_columns(mgras, selected_ID, new_units * square_feet_per_unit,
                   product_type_labels.square_footage)
