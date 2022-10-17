from typing import Callable

TOKEN_TYPE = int
INTERMEDIATE = list[tuple[TOKEN_TYPE]]

# Обозначим каждую команду уникальным обозначением
PUSH = 0
ADDITION = 1
SUBTRACTION = 2
MULTIPLICATION = 3
DIVISION = 4
MODULO = 5
POWER = 6
OPEN_BRACKET = 7

# создаем словари для хранения операций, токенов и приоритетов
all_ops: dict[TOKEN_TYPE, Callable[[list], int]] = {}
all_tokens: dict[str, TOKEN_TYPE] = {}
all_priorities: dict[TOKEN_TYPE, int] = {}

# создаем декоратор для операций
def binary_op(str_token: str, token: TOKEN_TYPE, priority: int) -> Callable[[Callable[[int, int], int]], Callable[[list], int]]:
    def make_binop(func: Callable[[int, int], int]) -> Callable[[list], int]:
        def redef(stack: list) -> int:
            if len(stack) < 2:
                raise ValueError(f"Недостаточно операндов на стаке")
            b = stack.pop()
            a = stack.pop()
            result = func(a, b)
            stack.append(result)
            return result
            
        all_ops[token] = redef
        all_tokens[str_token] = token
        all_priorities[token] = priority
        return redef
    return make_binop


# Перечень реализованных операций
@binary_op('+', ADDITION, 0)
def add(a, b):
    return a + b


@binary_op('-', SUBTRACTION, 0)
def sub(a, b):
    return a - b


@binary_op('*', MULTIPLICATION, 1)
def mul(a, b):
    return a * b


@binary_op('//', DIVISION, 1)
def div(a, b):
    return a // b


@binary_op('%', MODULO, 1)
def mod(a, b):
    return a % b


@binary_op('^', POWER, 2)
def power(a, b):
    return a ** b

# алгоритм сортировочной станции
def alg_sort_stack(infix: str) -> INTERMEDIATE:
    token_list = []
    stack = []
    token = ""
    last_was_digit = False

    # для работы с операциями
    def process_op():
        nonlocal token
        if not token:
            return

        op1 = all_tokens.get(token, None)
        if op1 is None:
            raise ValueError("Неизвестная операция")
        
        #пока оператор на вершине стака, проверяем выражение и перекладываем его в token_list 
        priority_op1 = all_priorities[op1]
        while len(stack) >= 1 and stack[-1] != OPEN_BRACKET and all_priorities[stack[-1]] >= priority_op1:
            token_list.append((stack.pop(),))

        stack.append(op1)
        token = ""
    # для работы с числами
    def process_num():
        nonlocal token
        if not token:
            return
        value = int(token)
        token_list.append((PUSH, value))
        token = ""

    # обработка выражения
    for ch in infix:

        # проверка на пробел
        if ch.isspace():
            continue

        # проверка на открывающую скобку
        if ch == "(":
            process_op()
            stack.append(OPEN_BRACKET)

        # также проверяем на закрывающую скобку
        elif ch == ")":
            process_num()
            while len(stack) >= 1:
                if (op := stack.pop()) != OPEN_BRACKET:
                    token_list.append((op,))
                else:
                    break
            else:
                raise ValueError("В выражении пропущена открывающая скобка")
        else:
            # проверка на число
            if ch.isdigit():
                if not last_was_digit:
                    process_op()
                last_was_digit = True
            else:
                if last_was_digit:
                    process_num()
                last_was_digit = False
            token += ch
    else:
        # проверка на оператор
        if token:
            if last_was_digit:
                process_num()
            else:
                raise ValueError("Запись оканчивается на оператор")
                
        # проверка на закрывающую скобку
        for op in reversed(stack):
            if op == OPEN_BRACKET:
                raise ValueError("В выражении пропущена закрывающая скобка")
            token_list.append((op,))

    return token_list

# функция для вычислений в ОПН
def get_the_RPN(program: INTERMEDIATE) -> int:
    stack = []
    for op in program:
        token = op[0]
        if token == PUSH:
            stack.append(op[1])
            continue

        func = all_ops.get(token, None)
        if func is None:
            raise ValueError('Таковой операции не существует')

        func(stack)

    if len(stack) != 1:
        raise ValueError('На стаке осталось не одно число')

    return stack.pop()


# запускаем, проверяем
if __name__ == "__main__":
    print("Проверка")
    # все гуд
    print(get_the_RPN(alg_sort_stack("50 - 12")), "==", 38)
    print(get_the_RPN(alg_sort_stack("(15 + 7) * 2")), "==", 44)
    print(get_the_RPN(alg_sort_stack("(2 + 5) * 5 - 10")), "==", 25)
