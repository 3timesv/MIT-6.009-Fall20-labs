import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:

    def __add__(self, other):
        return Add(self, other)

    __radd__ = __add__

    def __sub__(self, other):
        return Sub(self, other)

    __rsub__ = __sub__

    def __mul__(self, other):
        return Mul(self, other)

    __rmul__ = __mul__

    def __truediv__(self, other):
        return Div(self, other)

    __rtruediv__ = __truediv__


class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Var(' + repr(self.name) + ')'

    def deriv(self, var):
        if var == self.name:
            return 1

        return 0

    def simplify(self):
        return self


class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return 'Num(' + repr(self.n) + ')'

    def deriv(self, var):
        return 0

    def simplify(self):
        return self


class BinOp(Symbol):
    def __init__(self, left, right, op):
        if isinstance(left, int):
            self.left = Num(left)
        elif isinstance(left, str):
            self.left = Var(left)
        else:
            self.left = left

        if isinstance(right, int):
            self.right = Num(right)
        elif isinstance(right, str):
            self.right = Var(right)
        else:
            self.right = right

        self.op = op
        self.order = {'*': 0, '/': 0, '+': 1, '-': 1}

    def __str__(self):

        l_exp = self._wrap(self.left)
        r_exp = self._wrap(self.right)

        if self.op == '-' or self.op == '/':
            if (self.order[self.op] == self.order[self.right.op]):
                r_exp = '(' + r_exp + ')'

        return l_exp + ' ' + self.op + ' ' + r_exp

    def _wrap(self, exp):
        result = str(exp)

        if isinstance(exp, BinOp):
            if self.order[exp.op] > self.order[self.op]:
                return '(' + result + ')'

        return result

    def is_both_num(self):
        return isinstance(self.left, Num) and isinstance(self.right, Num)


class Add(BinOp):
    def __init__(self, left, right):
        self.op = '+'
        super().__init__(left, right, self.op)

    def __repr__(self):
        return "Add(" + repr(self.left) + ', ' + repr(self.right) + ')'

    def deriv(self, var):
        return self.left.deriv(var) + self.right.deriv(var)

    def simplify(self):
        if self.is_both_num():
            print("add both num", self.left, self.right)
            return Num(self.left.n + self.right.n)

        if isinstance(self.left, Num) and (self.left.n == 0):
            return self.right.simplify()
        if isinstance(self.right, Num) and (self.right.n == 0):
            return self.left.simplify()

        return self.left.simplify() + self.right.simplify()


class Sub(BinOp):
    def __init__(self, left, right):
        self.op = '-'
        super().__init__(left, right, self.op)

    def __repr__(self):
        return "Sub(" + repr(self.left) + ', ' + repr(self.right) + ')'

    def deriv(self, var):
        return self.left.deriv(var) - self.right.deriv(var)

    def simplify(self):
        if self.is_both_num():
            return Num(self.left.n - self.right.n)

        if isinstance(self.left, Num) and (self.left.n == 0):
            return self.right.simplify()
        if isinstance(self.right, Num) and (self.right.n == 0):
            return self.left.simplify()

        return self.left.simplify() - self.right.simplify()


class Mul(BinOp):
    def __init__(self, left, right):
        self.op = '*'
        super().__init__(left, right, self.op)

    def __repr__(self):
        return 'Mul(' + repr(self.left) + ', ' + repr(self.right) + ')'

    def deriv(self, var):
        left_exp = self.left * self.right.deriv(var)
        right_exp = self.right * self.left.deriv(var)

        return left_exp + right_exp

    def simplify(self):
        if isinstance(self.left, Num):
            if self.left.n == 0:
                return 0
            elif self.left.n == 1:
                return self.right.simplify()

        if isinstance(self.right, Num):
            if self.right.n == 0:
                return 0
            elif self.right.n == 1:
                return self.left.simplify()

        if self.is_both_num():
            return Num(self.left.n * self.right.n)

        return self.left.simplify() * self.right.simplify()



class Div(BinOp):
    def __init__(self, left, right):
        self.op = '/'
        super().__init__(left, right, self.op)

    def __repr__(self):
        return 'Div(' + repr(self.left) + ', ' + repr(self.right) + ')'

    def deriv(self, var):
        num_left_exp = self.right * self.left.deriv(var)
        num_right_exp = self.left * self.right.deriv(var)

        numerator = num_left_exp - num_right_exp
        denominator = self.right * self.right

        return numerator / denominator

    def simplify(self):
        if self.is_both_num() and (self.right.n == 0):
            return Num(self.left.n / self.right.n)

        if isinstance(self.left, Num) and (self.left.n == 0):
            return 0

        return self.left.simplify() / self.right.simplify()


if __name__ == '__main__':
    doctest.testmod()
    x = Var('x')
    y = Var('y')
    z = 2*x - x*y + 3*y
    import pdb; pdb.set_trace()

    print(z.deriv('x').simplify())
