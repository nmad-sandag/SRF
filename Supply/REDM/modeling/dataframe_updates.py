
import utils.config as config
from utils.constants import MGRA, DEVELOPED_ACRES, VACANT_ACRES, \
    HOUSING_UNITS, JOB_SPACES_PER_BUILDING_POSTFIX, TOTAL_JOB_SPACES


def update_acreage(mgras, selected_ID, new_acreage,
                   product_type_developed_key, product_type_vacant_key):
    mgras.loc[mgras[MGRA] == selected_ID, [
        product_type_developed_key, DEVELOPED_ACRES]] += new_acreage
    mgras.loc[mgras[MGRA] == selected_ID, [
        product_type_vacant_key, VACANT_ACRES]] -= new_acreage
    return mgras


def add_to_columns(mgras, selected_ID, value, columns):
    '''
        value: number to add to the current values of columns
        columns: list of column labels
    '''
    mgras.loc[mgras[MGRA] == selected_ID, columns] += value
    return mgras


def update_mgra(mgras, selected_ID, square_feet_per_unit, acreage_per_unit,
                new_units, product_type_labels):
    # update acreages
    mgras = update_acreage(mgras, selected_ID,
                           acreage_per_unit * new_units,
                           product_type_labels.developed_acres,
                           product_type_labels.vacant_acres)
    # update unit counts
    columns_needing_new_units = []
    if product_type_labels.is_residential():
        columns_needing_new_units.append(HOUSING_UNITS)
        columns_needing_new_units.append(product_type_labels.total_units)
    else:
        columns_needing_new_units.append(product_type_labels.buildings)
        new_job_spaces = new_units * \
            config.parameters[product_type_labels.product_type +
                              JOB_SPACES_PER_BUILDING_POSTFIX]
        mgras = add_to_columns(
            mgras, selected_ID, new_job_spaces,
            [product_type_labels.total_units, TOTAL_JOB_SPACES]
        )
    mgras = add_to_columns(mgras, selected_ID, new_units,
                           columns_needing_new_units)
    # update square footages
    return add_to_columns(mgras, selected_ID, new_units * acreage_per_unit,
                          product_type_labels.square_footage)
