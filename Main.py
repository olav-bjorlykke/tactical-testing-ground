import gurobipy as gp
from gurobipy import GRB

import gurobipy as gp
from gurobipy import GRB


#Settin up sets
Nurses = [f"{i}" for i in range(1,10)]
Shifts = ["Shift1", "Shift2", "Shift3"]
Days = [f"{i}" for i in range(1,10)]

rNurses = [i for i in range(len(Nurses))]
rShifts = [i for i in range(len(Shifts))]
rDays = [i for i in range(len(Days))]

#Setting up parameters


#Setting up a dict with shift requirements
shiftStaffingRequirements = {
    "1": {"Shift1": 2, "Shift2": 2, "Shift3": 2},
    "2": {"Shift1": 2, "Shift2": 2, "Shift3": 2},
    "3": {"Shift1": 3, "Shift2": 2, "Shift3": 2},
    "4": {"Shift1": 3, "Shift2": 2, "Shift3": 2},
    "5": {"Shift1": 3, "Shift2": 2, "Shift3": 2},
    "6": {"Shift1": 2, "Shift2": 2, "Shift3": 2},
    "7": {"Shift1": 3, "Shift2": 2, "Shift3": 2},
    "8": {"Shift1": 2, "Shift2": 2, "Shift3": 2},
    "9": {"Shift1": 2, "Shift2": 2, "Shift3": 2},
}

#Parameter for cost of staffing a shift
shiftCost = {
    "1": {"Shift1": 1000 + 200, "Shift2": 1200+200, "Shift3": 1500+200},
    "2": {"Shift1": 1000 + 200, "Shift2": 1200+200, "Shift3": 1500+200},
    "3": {"Shift1": 1000, "Shift2": 1200, "Shift3": 1500},
    "4": {"Shift1": 1000, "Shift2": 1200, "Shift3": 1500},
    "5": {"Shift1": 1000, "Shift2": 1200, "Shift3": 1500},
    "6": {"Shift1": 1000, "Shift2": 1200, "Shift3": 1500},
    "7": {"Shift1": 1000, "Shift2": 1200, "Shift3": 1500},
    "8": {"Shift1": 1000 + 200, "Shift2": 1200+200, "Shift3": 1500+200},
    "9": {"Shift1": 1000 + 200, "Shift2": 1200+200, "Shift3": 1500+200},
}

#Paramater for cost of shift for a substitute nurse
shiftCostSubstitute = {
    "1": {"Shift1": 2000, "Shift2": 2400, "Shift3": 3000},
    "2": {"Shift1": 2000, "Shift2": 2400, "Shift3": 3000},
    "3": {"Shift1": 2000, "Shift2": 2400, "Shift3": 3000},
    "4": {"Shift1": 2000, "Shift2": 2400, "Shift3": 3000},
    "5": {"Shift1": 2000, "Shift2": 2400, "Shift3": 3000},
    "6": {"Shift1": 2000, "Shift2": 2400, "Shift3": 3000},
    "7": {"Shift1": 2000, "Shift2": 2400, "Shift3": 3000},
    "8": {"Shift1": 2000, "Shift2": 2400, "Shift3": 3000},
    "9": {"Shift1": 2000, "Shift2": 2400, "Shift3": 3000},
}

#Setting constant Params
shiftLength = 8
L = 7/len(rDays)



#Create the model
m = gp.Model("Nurse Rostering")
m.ModelSense = GRB.MINIMIZE

#Add variables
x = m.addVars(rNurses, rShifts, rDays, vtype="B", name="x")
y = m.addVars(rShifts, rDays, vtype="B", name="y")
lamda = m.addVars(rNurses, rDays, vtype="B", name="lamda")
hoursPenalty = m.addVars(rNurses, vtype="C", name ="hoursPenalty")


#Adding Constraints:

#Max one shift per day constraint:
for n in rNurses:
    for d in rDays:
        m.addConstr(gp.quicksum(x[n,s,d] for s in rShifts) <= 1)


#Atleast 11 hours of rest constraint:
for d in rDays[1:]:
    for n in rNurses:
        m.addConstr(x[n,0,d] + x[n,1,d-1] +x[n,2,d-1] <= 1)
        m.addConstr(x[n, 1, d] + x[n, 0, d] + x[n, 2, d - 1]  <= 1)

#Both Days or none of the days in a weekend off
for n in rNurses:
    m.addConstr(gp.quicksum(x[n,s,0]for s in rShifts) == gp.quicksum(x[n,s,1]for s in rShifts))
    m.addConstr(gp.quicksum(x[n, s, 7] for s in rShifts) == gp.quicksum(x[n, s, 8] for s in rShifts))

#Every other weekend off
for n in rNurses:
    m.addConstr(gp.quicksum(x[n,s,0] + x[n,s,7] for s in rShifts) <= 1)

#Work atmost 6 consecutive days:
for n in rNurses:
    for d_num in rDays:
        m.addConstr(gp.quicksum(x[n,s,d] for s in rShifts for d in rDays[d_num:d_num + 6]) <= 6)

#Work atmost 4 consecutive Night shifts:
for n in rNurses:
    for d_num in range(len(Days)-3):
        m.addConstr(gp.quicksum(x[n,s,d] for s in rShifts for d in rDays[d_num:d_num + 3]) <= 4)


#Each shift has enough Personnel
for d in rDays:
    for s in rShifts:
        m.addConstr(gp.quicksum(x[n, s, d] for n in rNurses) + y[s, d] >= shiftStaffingRequirements[Days[d]][Shifts[s]])

#Creating penalty costs for Switching shifts:
for n in rNurses:
    for d in rDays[:7]:
        m.addConstr(x[n, 0, d] + x[n, 1, d + 1] + x[n, 2, d + 1] >= 2* lamda[n,d])
        m.addConstr(x[n, 1, d] + x[n, 0, d + 1] + x[n, 2, d + 1] >= 2* lamda[n,d])
        m.addConstr(x[n, 2, d] + x[n, 0, d + 1] + x[n, 1, d + 1] >= 2* lamda[n,d])

#Functional constraint for limiting number of hours worked
#Todo: come up with an alternative way of enforcing 37.5 hour weeks
#for n in rNurses:
#    m.addConstr(gp.quicksum(x[n,s,d] for s in rShifts for d in rDays) * shiftLength >= 37.5*L)

#for n in rNurses:
#    m.addConstr(gp.quicksum(x[n,s,d]*shiftLength for s in rShifts for d in rDays) - 37.5/L == hoursPenalty[n])

#Symmetry breaking constraint
for n in rNurses[:8]:
    m.addConstr(x[n,0,0] >= x[n+1,0,0])


#Create the objective function:
#TODO: Add hours constraints
m.setObjective(
    gp.quicksum(x[n,s,d] * shiftCost[Days[d]][Shifts[s]] for n in rNurses for s in rShifts for d in rDays) +
    gp.quicksum(y[s,d] * shiftCostSubstitute[Days[d]][Shifts[s]] for s in rShifts for d in rDays) +
    gp.quicksum(lamda[n,d] * 10 for n in rNurses for d in rDays)
)


m.optimize()

print('SOLUTION:')



for d in rDays:
    print(f"Day {d+1}")
    for s in rShifts:
        print(f"Shift{s + 1}:")
        if y[s, d].X > 0:
            print(f"    Substitute")
        for n in rNurses:
            if x[n,s,d].X > 0:
                print(f"    Nurse {n + 1}")

for n in rNurses:
    print(f"Nurse{n+1} Average per week:", gp.quicksum(x[n,s,d].X for s in rShifts for d in rDays)*8*L, "Schedule: ")
    for d in rDays:
        print(x[n,0,d].X,x[n,1,d].X,x[n,2,d].X)
















