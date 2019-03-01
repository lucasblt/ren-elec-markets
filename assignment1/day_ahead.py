def solver(g_df, d_df, limit):
    #Initializing variables
    power_g = {}
    cost_g = {}
    power_d = {}
    cost_d = {}

    ng = {}
    nd = {}

    set_ng = {}
    set_nd = {}

    cg = {}
    pg = {}

    cd = {}
    pd = {}

    yg = {}
    yd = {}

    opt_g_df = {}
    opt_d_df = {}

    constraint = {}

    theta = {}

    ids_g = {}
    ids_d = {}

    #Name of unique regions used for iteration

    regions = d_df.region.unique()

    #Creating model

    opt_model = plp.LpProblem(name="Model")

    #Creating variables

    theta = plp.LpVariable(cat=plp.LpContinuous, lowBound=-limit, upBound=limit, name="theta")

    i = 0
    for reg in regions:
            power_g[reg] = g_df[g_df['region']==reg].values[:,2].T.tolist()
            cost_g[reg] = g_df[g_df['region']==reg].values[:,3].T.tolist()
            power_d[reg] = d_df[d_df['region']==reg].values[:,2].T.tolist()
            cost_d[reg] = d_df[d_df['region']==reg].values[:,3].T.tolist()
            ids_d[reg] = d_df[d_df['region']==reg].values[:,0].T.tolist()
            ids_g[reg] = g_df[g_df['region']==reg].values[:,0].T.tolist()


            ng[reg] = len(power_g[reg])
            nd[reg] = len(power_d[reg])

            set_ng[reg] = range(1, ng[reg] + 1)
            set_nd[reg] = range(1, nd[reg] + 1)

            cg[reg] = {(i): cost_g[reg][i-1] for i in set_ng[reg]}
            pg[reg] = {(i): power_g[reg][i-1] for i in set_ng[reg]}
            cd[reg] = {(i): cost_d[reg][i-1] for i in set_nd[reg]}
            pd[reg] = {(i): power_d[reg][i-1] for i in set_nd[reg]}

            yg[reg]  = {(i): plp.LpVariable(cat=plp.LpContinuous,
                                            lowBound=0,
                                            upBound=pg[reg][i],
                                            name="{}".format(ids_g[reg][i-1])) for i in set_ng[reg]}

            yd[reg]  = {(i): plp.LpVariable(cat=plp.LpContinuous,
                                            lowBound=0,
                                            upBound=pd[reg][i],
                                            name="{}".format(ids_d[reg][i-1])) for i in set_nd[reg]}

            #Creating constraints
            constraint[reg] = plp.LpConstraint(
                             e=plp.lpSum(yd[reg][j] for j in set_nd[reg]) - plp.lpSum(yg[reg][j] for j in set_ng[reg]) + ((-1)**i)*theta,
                             sense=plp.LpConstraintEQ,
                             rhs=0,
                             name="constraint_eq_{}".format(reg))

            opt_model += constraint[reg], "{}".format(reg)
            i += 1

    #Defining objective function

    objective = plp.lpSum(yd[reg][i]*cd[reg][i] for reg in regions for i in set_nd[reg]) - plp.lpSum(yg[reg][i]*cg[reg][i] for reg in regions for i in set_ng[reg])

    #Solving optimization problem

    opt_model.sense = plp.LpMaximize
    opt_model.setObjective(objective)
    opt_model.solve()

    price = {}
    for name, c in list(opt_model.constraints.items()):
        price[name] = c.pi

    #Extracting results
    for reg in regions:
        opt_g_df[reg] = pandas.DataFrame.from_dict(yg[reg], orient="index", columns = ["ID"])
        opt_d_df[reg] = pandas.DataFrame.from_dict(yd[reg], orient="index", columns = ["ID"])

        opt_g_df[reg]['Region'] = reg
        opt_d_df[reg]['Region'] = reg

        opt_g_df[reg]['Market Price'] = price[reg]
        opt_d_df[reg]['Market Price'] = price[reg]

    schedule_g = pandas.concat(opt_g_df.values(), ignore_index=True)
    schedule_d = pandas.concat(opt_d_df.values(), ignore_index=True)

    schedule_g["Scheduled Pg"] = schedule_g["ID"].apply(lambda item: item.varValue)
    schedule_d["Scheduled Pd"] = schedule_d["ID"].apply(lambda item: item.varValue)

    schedule_g["Revenue"] = schedule_g["Market Price"]*schedule_g["Scheduled Pg"]
    schedule_d["Payment"] = schedule_d["Market Price"]*schedule_d["Scheduled Pd"]

    return schedule_g, schedule_d
