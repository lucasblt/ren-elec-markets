import pulp as plp
import pandas as pd

def solver(up_df, down_df, delta):
    #Initializing variables
    power_up = {}
    cost_up = {}
    power_down = {}
    cost_down = {}

    nup = {}
    ndown = {}

    set_nup = {}
    set_ndown = {}

    cup = {}
    pup = {}

    cdown = {}
    pdown = {}

    yup = {}
    ydown = {}

    opt_up_df = {}
    opt_down_df = {}

    constraint = {}

    theta = {}

    ids_up = {}
    ids_down = {}

    #Name of unique regions used for iteration

    regions = up_df.region.unique()

    #Creating model

    opt_model = plp.LpProblem(name="Model")

    #Creating variables

    i = 0

    for reg in regions:
                power_up[reg] = up_df[up_df['region']==reg].values[:,2].T.tolist()
                cost_up[reg] = up_df[up_df['region']==reg].values[:,3].T.tolist()
                power_down[reg] = down_df[down_df['region']==reg].values[:,2].T.tolist()
                cost_down[reg] = down_df[down_df['region']==reg].values[:,3].T.tolist()
                ids_down[reg] = down_df[down_df['region']==reg].values[:,0].T.tolist()
                ids_up[reg] = up_df[up_df['region']==reg].values[:,0].T.tolist()

                nup[reg] = len(power_up[reg])
                ndown[reg] = len(power_down[reg])

                set_nup[reg] = range(1, nup[reg] + 1)
                set_ndown[reg] = range(1, ndown[reg] + 1)

                cup[reg] = {(i): cost_up[reg][i-1] for i in set_nup[reg]}
                pup[reg] = {(i): power_up[reg][i-1] for i in set_nup[reg]}
                cdown[reg] = {(i): cost_down[reg][i-1] for i in set_ndown[reg]}
                pdown[reg] = {(i): power_down[reg][i-1] for i in set_ndown[reg]}

                yup[reg]  = {(i): plp.LpVariable(cat=plp.LpContinuous,
                                                lowBound=0,
                                                upBound=pup[reg][i],
                                                name="{}_up".format(ids_up[reg][i-1])) for i in set_nup[reg]}

                ydown[reg]  = {(i): plp.LpVariable(cat=plp.LpContinuous,
                                                lowBound=0,
                                                upBound=pdown[reg][i],
                                                name="{}_down".format(ids_down[reg][i-1])) for i in set_ndown[reg]}

                #Creating constraints
                constraint[reg] = plp.LpConstraint(
                                 e = plp.lpSum(yup[reg][j] for j in set_nup[reg]) - plp.lpSum(ydown[reg][j] for j in set_ndown[reg]) -22,
                                 sense=plp.LpConstraintEQ,
                                 rhs=delta,
                                 name="constraint_eq_{}".format(reg))

                opt_model += constraint[reg], "{}".format(reg)
                i += 1

    #Defining objective function
    objective = plp.lpSum(yup[reg][i]*cup[reg][i] for reg in regions for i in set_nup[reg])- plp.lpSum(ydown[reg][i]*cdown[reg][i] for reg in regions for i in set_ndown[reg])

    #Solving optimization problem

    opt_model.sense = plp.LpMinimize
    opt_model.setObjective(objective)
    opt_model.solve()

    price = {}

    for name, c in list(opt_model.constraints.items()):
        price[name] = c.pi

    #Extracting results
    for reg in regions:
            opt_up_df[reg] = pd.DataFrame.from_dict(yup[reg], orient="index", columns = ["ID"])
            opt_down_df[reg] = pd.DataFrame.from_dict(ydown[reg], orient="index", columns = ["ID"])

            opt_up_df[reg]['Region'] = reg
            opt_down_df[reg]['Region'] = reg

            opt_up_df[reg]['Market Price'] = price[reg]
            opt_down_df[reg]['Market Price'] = price[reg]

    schedule_up = pd.concat(opt_up_df.values(), ignore_index=True)
    schedule_down = pd.concat(opt_down_df.values(), ignore_index=True)

    schedule_up["Scheduled Pg"] = schedule_up["ID"].apply(lambda item: item.varValue)
    schedule_down["Scheduled Pd"] = schedule_down["ID"].apply(lambda item: item.varValue)

    return schedule_up, schedule_down, price
