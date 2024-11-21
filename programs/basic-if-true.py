a = 3
if(a==3):
    print("True 1")
elif(a==3):
    print("True 2")
    if a == 1:
        print("True 2 False")
elif(a==1):
    print("False 1")
    if a == 1:
        print("False 1 False")
    else:
        print("False 1 True")
else:
    print("False 2")
print("Anyway")