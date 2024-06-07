class A:
    var1 = 10
    def method1(self):
        pass

    def method2(self):
        pass

class B(A):
    def method3(self):
        pass

class C(A):
    def method4(self):
        pass

class D(B, C):
    def method5(self):
        pass
