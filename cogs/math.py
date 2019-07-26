from __future__ import division
from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional, ZeroOrMore, Forward, nums, alphas, oneOf)
import discord
from discord.ext import commands
import math
import random
import re
import operator

class MathCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def math(self, ctx, *, inp: str):
        """Does math. Uses python syntax with math library. Use like math 5 + 3 * 2 or math [function](5). To get list of all functions use math_functions command."""
        if inp == "":
            await ctx.send("You need to give some numbers and functions to me")
            return
        try:
            nsp = NumericStringParser()
            answer = nsp.eval(inp)
            await ctx.send(answer)
        except Exception:
            await ctx.send(f"Unable to understand math expression! :angry:")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def math_functions(self, ctx):
        """List of all math functions for math command. Call this command to see the list."""
        n = NumericStringParser()
        func = set(n.fn.keys())
        rand_function = random.choice(list(func))
        clean = re.sub('[\'{}]', '', str(func))
        await ctx.send(f"```List of all math functions:\n{clean}\n\nUse them like {rand_function}(number or function)\nEach function needs brackets\nOr you can use operators like (2 + 5 / 4) ^ 2```")

class NumericStringParser(object):
    '''
    Most of this code comes from the fourFn.py pyparsing example

    '''

    def push_first(self, strg, loc, toks):
        self.expr_stack.append(toks[0])

    def push_u_minus(self, strg, loc, toks):
        if toks and toks[0] == '-':
            self.expr_stack.append('unary -')

    def __init__(self):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(Word("+-" + nums, nums) +
                          Optional(point + Optional(Word(nums))) +
                          Optional(e + Word("+-" + nums, nums)))
        ident = Word(alphas, alphas + nums + "_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        mod = Literal("%")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div | mod
        expop = Literal("^")
        pi = CaselessLiteral("PI")
        expr = Forward()
        atom = ((Optional(oneOf("- +")) +
                 (ident + lpar + expr + rpar | pi | e | fnumber).setParseAction(self.push_first))
                | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
                ).setParseAction(self.push_u_minus)
        # by defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + \
            ZeroOrMore((expop + factor).setParseAction(self.push_first))
        term = factor + \
            ZeroOrMore((multop + factor).setParseAction(self.push_first))
        expr << term + \
            ZeroOrMore((addop + term).setParseAction(self.push_first))
        # addop_term = ( addop + term ).setParseAction( self.push_first )
        # general_term = term + ZeroOrMore( addop_term ) | OneOrMore( addop_term)
        # expr <<  general_term
        self.bnf = expr
        # map operator symbols to corresponding arithmetic operations
        epsilon = 1e-12
        self.opn = {"+": operator.add,
                    "-": operator.sub,
                    "*": operator.mul,
                    "/": operator.truediv,
                    "^": operator.pow,
                    "%": operator.mod}
        self.fn = {"sin": math.sin,
                   "cos": math.cos,
                   "tan": math.tan,
                   "exp": math.exp,
                   "degrees": math.degrees,
                   "radians": math.radians,
                   "log10": math.log10,
                   "log": math.log,
                   "ceil": math.ceil,
                   "floor": math.floor,
                   "sqrt": math.sqrt,
                   "abs": abs,
                   "trunc": lambda a: int(a),
                   "round": round,
                   "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0}

    def evaluate_stack(self, s):
        op = s.pop()
        if op == 'unary -':
            return -self.evaluate_stack(s)
        if op in "+-*/^%":
            op2 = self.evaluate_stack(s)
            op1 = self.evaluate_stack(s)
            return self.opn[op](op1, op2)
        elif op == "PI":
            return math.pi  # 3.1415926535
        elif op == "E":
            return math.e  # 2.718281828
        elif op in self.fn:
            return self.fn[op](self.evaluate_stack(s))
        elif op[0].isalpha():
            return 0
        else:
            return float(op)

    def eval(self, num_string, parse_all=True):
        self.expr_stack = []
        results = self.bnf.parseString(num_string, parse_all)
        val = self.evaluate_stack(self.expr_stack[:])
        return val

def setup(bot):
    bot.add_cog(MathCog(bot))
