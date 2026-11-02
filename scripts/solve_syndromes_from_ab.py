import kickmix as km
import numpy as np

field = km.GF2Field(12)

# Load the A and B values from previous output:
A = [0, 0, 2539, 2700, 1580, 143, 1642, 144, 908, 3379, 1992, 192, 2876, 533, 340, 1037, 2534, 4049, 1403, 1141, 2265, 1406, 3836, 1086, 2078, 1767, 1058, 1854, 1213, 3683, 794, 576, 1708, 4042, 1809]
B = [0, 0, 1177, 442, 971, 1309, 2488, 16, 1665, 2339, 3815, 3654, 3575, 191, 782, 991, 2177, 737, 820, 2654, 2838, 3656, 958, 3899, 2565, 1269, 3006, 2520, 2128, 742, 1021, 14, 939, 2082, 1246]

# In Berlekamp-Massey / Euclidean algorithm:
# A and B are the outputs of the continued fraction expansion of P / S!
# Let's check their relationship with S:
# What polynomial division produced A and B?
print("A nonzeros:", len([x for x in A if x != 0]))
print("B nonzeros:", len([x for x in B if x != 0]))

