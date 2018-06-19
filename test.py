from fractions import Fraction

geneRange = [i for i in range(-5, 5) if i != 0]
geneset = [i for i in set(
            Fraction(d, e)
            for d in geneRange
            for e in geneRange if e != 0)]

print(float(geneset[0]))
