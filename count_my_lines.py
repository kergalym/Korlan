import re
from pathlib import Path
from os import walk
from os.path import exists

game_dir = str(Path.cwd())


def simple_regex(line):
    if re.search(r"\w+", line):
        return True


def exclude_docstrings(count):
    if re.match(r'"""[\w\W]+"""', count):
        return re.sub(r'"""[\w\W]+"""', '', count)
    elif re.match(r"'''[\w\W]+'''", count):
        return re.sub(r"'''[\w\W]+'''", '', count)
    else:
        return count


def count_my_lines():
    data = ''
    total = 0
    exclude_dir = 'Render'
    exclude_dir2 = "tmp"
    exclude_dir3 = "venv3.7"
    exclude_dir4 = "dist"
    exclude_dir5 = "build"
    docstrings = None

    if exists(game_dir):

        for root, dirs, files in walk(game_dir, topdown=True):
            if exclude_dir in dirs:
                dirs.remove(exclude_dir)
            if exclude_dir2 in dirs:
                dirs.remove(exclude_dir2)
            if exclude_dir3 in dirs:
                dirs.remove(exclude_dir3)
            if exclude_dir4 in dirs:
                dirs.remove(exclude_dir4)
            if exclude_dir5 in dirs:
                dirs.remove(exclude_dir5)

            for file in files:
                f_str = str(file)
                if (f_str.endswith(".py") and not f_str.startswith("start_")
                        and f_str != "lightmap_test.py"
                        and f_str != "korlan_test.py"
                        and f_str != "count_my_lines.py"
                        and f_str != "main_test.py"):
                    path = "{0}/{1}".format(root, file)
                    # Here we read python file and count lines
                    name = str(file)
                    with open(path, "r") as f:
                        count = f.read()
                        count = exclude_docstrings(count)
                        count = count.split("\n")
                        sorted = []

                        for line in count:
                            if simple_regex(line):
                                if not line.startswith("#"):
                                    total += 1
                                    sorted.append(line)

                        data += "{0}: {1} line(s) of code\n\n".format(name, len(sorted))

        file_of_excl_dir = "{0}/Engine/Render/render.py".format(game_dir)
        if exists(game_dir):
            with open(file_of_excl_dir, "r") as f:
                count = f.read()
                count = exclude_docstrings(count)
                count = count.split("\n")
                sorted = []

                for line in count:
                    if simple_regex(line):
                        if (not line.startswith('"""')
                                or not line.startswith("'''")
                                or not line.startswith("#")):
                            total += 1
                            sorted.append(line)

                data += "render.py: {0} line(s) of code\n\n".format(len(sorted))

    total_text = "Total: {0} line(s) of code\n\n".format(total)

    print(data, total_text)


count_my_lines()
