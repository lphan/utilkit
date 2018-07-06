# Source:
# 	https://www.indeed.com/viewjob?jk=3a8836124e8d2dad&q=junior+data+scientist&tk=1cgb6v0m23cjdb0r&from=ja&alid=5a30ec3ce4b0cb7b372f1d43&utm_source=jobseeker_emails&utm_medium=email&utm_campaign=job_alerts&rgtk=1cgb6v0m23cjdb0r

# 1) Write three functions that compute the sum of the numbers in a given list using a for-loop, a while-loop, 
# and recursion.

# 2) Write a function that combines two lists by alternatingly taking elements. 
# For example: given the two lists [a, b, c] and [1, 2, 3], the function should return [a, 1, b, 2, c, 3].

# 3) Write a function that computes the list of the first 100 Fibonacci numbers. 
# By definition, the first two numbers in the Fibonacci sequence are 0 and 1, 
# and each subsequent number is the sum of the previous two. 
# As an example, here are the first 10 Fibonnaci numbers: 0, 1, 1, 2, 3, 5, 8, 13, 21, and 34.
__author__ = 'Long Phan'


def one_sumnum(func, a=[1,2,3,4,5]):
    if func is 'for':
        return sum([item for item in a])

    elif func is 'while':
        i = 0
        su = 0
        while i<len(a):
            su = su + a[i]
            i=i+1
        return su

    elif func is 'recursion':
        su = 0
        def rec(a):
            if len(a) is 0:
                return 0
            else:
                return a.pop()+rec(a)
        return rec(a)
    
    else:
        return 


def two_combinelists(a=[1,2,3,4], b=['a','b','c','d']):
    if not a:
        return b
    elif not b:
        return a
    else:
        c = []
        b.reverse()
        for item in a:
            c.append(item)
            if b:
                c.append(b.pop())
        return c                       

def three_fibo(n=100):
    i = 0
    a = 0
    b = 1
    sum = 0
    res = [a, b]
    while i < n:
        sum = (a + b)
        res.append(sum)
        a = b 
        b = sum
        i = i + 1
    return res

print("\nFor loop: ", one_sumnum(a=[1,3,5,7,9,10], func='for'), "\n")
print("While loop: ", one_sumnum(a=[1,3,5,7,9,10], func='while'), "\n")
print("Recursion: ", one_sumnum(a=[1,3,5,7,9,10], func='recursion'), "\n")
print("Combine_Two_Lists: ", two_combinelists(), "\n")
print(three_fibo())
