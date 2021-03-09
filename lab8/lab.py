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

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    __rmul__ = __mul__

    def __truediv__(self, other):
        return Div(self, other)
    
    def __rtruediv__(self, other):
        return Div(other, self)



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
            return Num(1)

        return Num(0)

    def simplify(self):
        return self

    def eval(self, mapping):
        return mapping[self.name]


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
        return Num(0)

    def simplify(self):
        return self

    def eval(self, mapping):
        return self.n


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

        if isinstance(self.right, BinOp) and (self.op == '-' or self.op == '/'):
            if (self.order[self.op] == self.order[self.right.op]):
                r_exp = '(' + r_exp + ')'

        return l_exp + ' ' + self.op + ' ' + r_exp

    def _wrap(self, exp):
        result = str(exp)

        if isinstance(exp, BinOp):
            if self.order[exp.op] > self.order[self.op]:
                return '(' + result + ')'

        return result


class Add(BinOp):
    def __init__(self, left, right):
        self.op = '+'
        super().__init__(left, right, self.op)

    def __repr__(self):
        return "Add(" + repr(self.left) + ', ' + repr(self.right) + ')'

    def deriv(self, var):
        return self.left.deriv(var) + self.right.deriv(var)

    def simplify(self):
        left_exp = self.left.simplify()
        right_exp = self.right.simplify()

        if isinstance(left_exp, Num) and isinstance(right_exp, Num):
            return Num(left_exp.n + right_exp.n)

        if isinstance(left_exp, Num) and (left_exp.n == 0):
            return right_exp

        if isinstance(right_exp, Num) and (right_exp.n == 0):
            return left_exp

        result = left_exp + right_exp

        return result

    def eval(self, mapping):
        return self.left.eval(mapping) + self.right.eval(mapping)


class Sub(BinOp):
    def __init__(self, left, right):
        self.op = '-'
        super().__init__(left, right, self.op)

    def __repr__(self):
        return "Sub(" + repr(self.left) + ', ' + repr(self.right) + ')'

    def deriv(self, var):
        return self.left.deriv(var) - self.right.deriv(var)

    def simplify(self):
        left_exp = self.left.simplify()
        right_exp = self.right.simplify()

        if isinstance(left_exp, Num) and isinstance(right_exp, Num):
            return Num(left_exp.n - right_exp.n)

#        if isinstance(left_exp, Num) and (left_exp.n == 0):
#            return right_exp

        if isinstance(right_exp, Num) and (right_exp.n == 0):
            return left_exp

        return left_exp - right_exp

    def eval(self, mapping):
        return self.left.eval(mapping) - self.right.eval(mapping)


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
        left_exp = self.left.simplify()
        right_exp = self.right.simplify()

        if isinstance(left_exp, Num):
            if left_exp.n == 0:
                return Num(0)
            elif left_exp.n == 1:
                return right_exp

        if isinstance(right_exp, Num):
            if right_exp.n == 0:
                return Num(0)
            elif right_exp.n == 1:
                return left_exp

        if isinstance(left_exp, Num) and isinstance(right_exp, Num):
            return Num(left_exp.n * right_exp.n)

        return left_exp * right_exp

    def eval(self, mapping):
        return self.left.eval(mapping) * self.right.eval(mapping)


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
        left_exp = self.left.simplify()
        right_exp = self.right.simplify()

        if isinstance(left_exp, Num) and (left_exp.n == 0):
            return Num(0)

        if isinstance(right_exp, Num) and (right_exp.n == 1):
            return left_exp
        if isinstance(left_exp, Num) and isinstance(right_exp, Num):
            return Num(left_exp.n / right_exp.n)

        return left_exp / right_exp

    def eval(self, mapping):
        return self.left.eval(mapping) / self.right.eval(mapping)


if __name__ == '__main__':
    doctest.testmod()
    x = Var('x')
    y = Var('y')
    z = 2*x - x*y + 3*y
    print(z.deriv('y').simplify())
