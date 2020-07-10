from random import randint

TOKEN_PATH = "./resources/_token"


def get(columns: int = 4, magic: int = 3, eof: int = 9786):
    with open(TOKEN_PATH, "r") as f:
        token = ""
        data = tuple(map(int, str.split(f.read())))

        for i in range(len(data) // magic):
            index = i + 2 * (i+1)
            value = data[index]

            if value == eof:
                return token
            token += chr(value)
        raise SyntaxError("token has no EOF character")


def set(token, columns: int = 4, magic: int = 3, fill: int = 16,
        fill_char: str = "0", eof: int = 9786):
    if fill_char != "0":
        fill_char = f"{fill_char}>"
    token += chr(eof)

    with open(TOKEN_PATH, "w") as f:
        buffer = []

        for char in token:
            for i in range(1, magic+1):
                if i == magic:
                    buffer.append(f"{ord(char):0{fill}}")
                elif i < magic:
                    buffer.append(f"{randint(10, eof):{fill_char}{fill}}")

                if len(buffer) == columns:
                    line = (" ").join(buffer)
                    buffer = []
                    f.write(f"{line}\n")
        if len(buffer) > 0:
            f.write(str.join(" ", buffer))
