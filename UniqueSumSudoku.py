# How hard can a 4x4 Sudoku be: https://www.youtube.com/watch?v=JvbnQMzOHhI
# The puzzle is "Unique Sum Sudoku" by I Love Sleeping & Myxo

# Non-standard 4x4-Sudoku rules apply. Fill the grid with digits 1-9, 
# such that no digit repeats in any row, column or box. The set of 
# digits in each row or column is unique, eg. if a row contains the 
# digits 1234, no other row or column may contain that combination 
# of digits.
# 
# The digits in every row, column and box sum to x, where x has to 
# be determined by the solver.
# 
# Normal XV-rules apply. Digits separated by an X sum to 10. Digits 
# separated by a V sum to 5. Not all Xs and Vs are necessarily given.

# aa v ab   ac   ad
#                 x
# ba   bb x bc   bd
#            v   
# ca   cb   cc   cd
#       x 
# da   db   dc   dd

from ortools.sat.python import cp_model

model = cp_model.CpModel()

aa = model.NewIntVar(1, 9, "aa")
ab = model.NewIntVar(1, 9, "ab")
ac = model.NewIntVar(1, 9, "ac")
ad = model.NewIntVar(1, 9, "ad")
ba = model.NewIntVar(1, 9, "ba")
bb = model.NewIntVar(1, 9, "bb")
bc = model.NewIntVar(1, 9, "bc")
bd = model.NewIntVar(1, 9, "bd")
ca = model.NewIntVar(1, 9, "ca")
cb = model.NewIntVar(1, 9, "cb")
cc = model.NewIntVar(1, 9, "cc")
cd = model.NewIntVar(1, 9, "cd")
da = model.NewIntVar(1, 9, "da")
db = model.NewIntVar(1, 9, "db")
dc = model.NewIntVar(1, 9, "dc")
dd = model.NewIntVar(1, 9, "dd")
x = model.NewIntVar(4, 36, "x")

quads = [
    # horizontal
    [aa, ab, ac, ad],
    [ba, bb, bc, bd],
    [ca, cb, cc, cd],
    [da, db, dc, dd],

    # vertical
    [aa, ba, ca, da],
    [ab, bb, cb, db],
    [ac, bc, cc, dc],
    [ad, bd, cd, dd],
]

boxes = [
    [aa, ab, ba, bb],
    [ac, ad, bc, bd],
    [ca, cb, da, db], 
    [cc, cd, dc, dd],
]

# V and X
model.Add(aa + ab == 5)
model.Add(ad + bd == 10)
model.Add(bb + bc == 10)
model.Add(bc + cc == 5)
model.Add(cb + db == 10)


# First off, we can iterate over the boxes and ensure all cells are
# different and sum to some x that we don't know yet.
for box in boxes:
    model.AddAllDifferent(box)
    model.Add(box[0] + box[1] + box[2] + box[3] == x)


# Next, we can do the same with the rows and colums (henceforth 
# "quads"). Moreover we also find the product of each quad which we
# need later to ensure all quads have different selections of numbers.
products = []
for idx, quad in enumerate(quads):
    model.AddAllDifferent(quad)
    model.Add(quad[0] + quad[1] + quad[2] + quad[3] == x)

    # Due to a bug in OR-tools one cannot do AddMultiplicationEquality
    # for lists longer than two. We'd like to multiply four values, so
    # we first create two products A, B each taking two operands, then 
    # multiplying THOSE to get the full product.
    productA = model.NewIntVar(1, 9*8, "productA%d" % idx)
    productB = model.NewIntVar(1, 9*8, "productB%d" % idx)
    model.AddMultiplicationEquality(productA, [quad[0], quad[1]])
    model.AddMultiplicationEquality(productB, [quad[2], quad[3]])

    product = model.NewIntVar(1, 9*8*7*6, "product%d" % idx)
    model.AddMultiplicationEquality(product, [productA, productB])

    products.append(product)

# We're using the products of the quads to ensure they all contain 
# different sets of numbers. *waves hand vigorously*
# 
# TODO: Insert proof here that we can sanely use the multiplication 
#       operator for this....
model.AddAllDifferent(products)


# The model has been set up, we can set up the solver...
solver = cp_model.CpSolver()

status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Solution found. Tada!")
    print(f"x = {solver.Value(x)}")
    print()
    print(f"{solver.Value(aa)} {solver.Value(ab)} {solver.Value(ac)} {solver.Value(ad)}")
    print(f"{solver.Value(ba)} {solver.Value(bb)} {solver.Value(bc)} {solver.Value(bd)}")
    print(f"{solver.Value(ca)} {solver.Value(cb)} {solver.Value(cc)} {solver.Value(cd)}")
    print(f"{solver.Value(da)} {solver.Value(db)} {solver.Value(dc)} {solver.Value(dd)}")

else:
    print("No solution found.")
