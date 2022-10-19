CPT = {}

CPT.setdefault(1, {})
CPT[1][(1,1,'1000')]='000101'

CPT.setdefault(2, {})
CPT[2][(2,2,'200')] = 'aaa'
#CPT[(2,1,'1000')].append('010100')
#CPT[(2,1,'500')].append('010111')
#CPT[(2,2,'500')].append('011000')
#CPT[(2,3,'500')].append('011001')

#CPT[(3,1,'')].append('011100')
#CPT[(4,2,'1000')].append('011101')

#for i in CPT:
#print(CPT[(1,1,'1000')])

print(CPT[1])
print(CPT[2])
#print(i[(4,2,'1000')])

