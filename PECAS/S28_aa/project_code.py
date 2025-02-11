# Code specific to this project. Copy this and rename it project_code.py, then fill in any function implementations
# you need, leaving the rest blank.

import aa_routines as pr
import os
import dump2csv as dc
_ps = pr._ps


# Called at the start of the run, after any resetting.
def before_run(ps=_ps):
    if ps.update_techopt:
        dc.dump_techopt(lambda: pr.connect_to_aa(ps), ps.scendir)
    if ps.update_inputs:
        dc.dump_pg_tbls(lambda: pr.connect_to_aa(ps), ps.scendir, ps.aa_schema, '^Inputs_')


# Called at the start of each model year, before any modules have run in that year.
def start_of_year(year,ps=_ps):
    dc.dump_pg_tbls(lambda: pr.connect_to_aa(ps),  ps.scendir, ps.aa_schema, '^'+str(year))
    syntar_f = '{}\\PopSynTargets.csv'.format(year)

    if not(os.path.exists(syntar_f)):
        cmd = 'copy /Y AllYears\\Working\\PopulationSynthesis\\PopSynTargets.csv {}\\PopSynTargets.csv'.format(year)
        print(cmd)
        os.system(cmd)
    skimyear = pr.get_skim_year(year, ps.skimyears)
    if skimyear<year:
        skimfilename = ps.skim_fname.format(yr=skimyear)
        if skimyear<ps.earliest_squeeze_year:
            dc.dump_pg_tbls(lambda: pr.connect_to_aa(ps), ps.scendir, ps.aa_schema, str(skimyear)+'_'+skimfilename[0:-4])

    if year==ps.baseyear:
        prev_year=year-1
        dc.dump_pg_tbls(lambda: pr.connect_to_aa(ps), ps.scendir, ps.aa_schema, '^'+str(prev_year))

    if year==2013:
        y13_smain_input='..\\..\\Supply\\data\\supply_input_{}.csv'.format(year)
        dc.dump_a_table(lambda: pr.connect_to_aa(ps), 'srf', '_supply_input',y13_smain_input)


def before_aa(year,ps=_ps):
    import sys
    os.chdir('..\\..\\Supply')
    sys.path.insert(0, '')

    # load dataframe(s)
    combined_rent = '..\\Demand\\{}\\combined_rents.csv'.format(year-1)
    combined_location = '..\\Demand\\{}\\combined_location.csv'.format(year-1)
    #old_supply_output = 'data\\output\\forecasted_year_{}.csv'.format(year-1)
    old_supply_output = '..\\PostProcessor\\data\\forecasted_year_{}.csv'.format(year-1)
    new_supply_input = 'data\\supply_input_{}.csv'.format(year)

    if os.path.exists(combined_rent) :
        from updatesupply import updateSupply
        updateSupply(combined_location,combined_rent,old_supply_output, new_supply_input)

    if os.path.exists(new_supply_input) :
        cmd='python main.py -f {} -y {}'.format(new_supply_input,year)
        print(cmd)
        os.system(cmd)
    else:
        #cmd='python main.py -y {}'.format(year)
        # CMB debug edit: force crash if supply/demand outputs not found
        raise SystemExit("Supply and/or demand outputs not found!")

    cmd = 'copy /Y data\\output\\FloorspaceI.csv ..\\PECAS\\S28_aa\\{}\\FloorspaceI.csv'.format(year)
    print(cmd)
    os.system(cmd)
    os.chdir('..\\PECAS\\S28_aa')

# Called after the AA module finishes.
def after_aa(year, ps):
    import os
    act_location_file = '..\\PECAS\\S28_aa\\'+str(year)+'\\ActivityLocations.csv'
    os.chdir('..\\..\\Demand')
    if (os.path.exists(act_location_file)):
        cmd = 'rscript .\\R\\aa2demand.R ' + act_location_file + ' .. '+str(year-ps.baseyear+1)
    else:
        cmd = 'rscript .\\R\\aa2demand.R ..\\PECAS\\S28_aa\\2011\\ActivityLocations.csv  .. '+str(year-ps.baseyear+1)
    print(cmd)
    os.system(cmd)
    cmd = 'copy /Y ..\\Supply\\data\\output\\forecasted_year_{}.csv ..\\PostProcessor\\Data\\forecasted_year_{}.csv'.format(year,year)
    print(cmd)
    os.system(cmd)
    cmd = 'rscript .\\R\\evalDemand.R .. '+str(year)
    print(cmd)
    os.system(cmd)
    if (year>2012):
        os.chdir('..\\PostProcessor')
        cmd = 'python mergeOutputs.py {}'.format(year)
        print(cmd)
        os.system(cmd)
        mgra13_based_update = os.path.join("Data","mgra13_based_input"+str(year)+".csv")
        if not(os.path.exists(mgra13_based_update)): raise SystemExit("MGRA summry file update unsuccessful")
    os.chdir('..\\PECAS\\S28_aa')


# Called after the ED module finishes.

def after_ed(year, ps=_ps):
    pass


# Called after the TM module finishes.
def after_tm(year, ps=_ps):
    pass


# Called after the SD module finishes.
def after_sd(year, ps=_ps):
    pass
