import os
import aiohttp
import random
import string
import asyncio
import shutil
import re

from threading import Thread
from io import BytesIO
from zipfile import ZipFile

from discord.ext import commands
from core import BotError

DEFAULT_MAJOR = "512"
DEFAULT_MINOR = "1416"

class WindowsProcessThread(Thread):
    def __init__(self, proc, p_args):
        super().__init__()
        self._proc = proc

        self._args = p_args

        self.errored = False
        self.error_msg = None

    def run(self):
        winloop = asyncio.ProactorEventLoop()

        future = self._proc(winloop, *self._args)

        try:
            winloop.run_until_complete(future)
        except BotError as err:
            self.errored = True
            self.error_msg = err.message
        except Exception:
            self.errored = True
            self.error_msg = "Unknown error caught in worker thread."

        winloop.close()

def validate_byond_build(byond_str):
    """
    A little shit of a failed command argument.
    
    Return a tuple containing (major, minor) build information if the argument
    string matches the defined format of: v:{major}.{minor} {rest of code here}.
    Returns None if such a tuple can't be generated.
    """
    if not byond_str.startswith("v:"):
        return None

    chunks = byond_str.split(" ")
    if not len(chunks) > 1:
        return None

    chunks = chunks[0].split(".")

    # This is triggered alyways forever. So. Return null if format doesn't match.
    if len(chunks) != 2:
        return None

    try:
        major = int(chunks[0][2:])
        minor = int(chunks[1])
    except ValueError:
        raise BotError("Error processing BYOND version request.", "validate_byond_build")

    return major, minor

class DmCog(commands.Cog):
    WORK_FOLDER = "cogs\\byond_eval"

    DM_BOILERPLATE = "/world/loop_checks = FALSE;\n" + \
                     "\n/world/New() {{ dm_eval(); del(src); }}" + \
                     "\n{0}\n/proc/dm_eval() {{ {1} {2} }}"

    def __init__(self, bot):
        self.bot = bot

        self._instances = []

        self._safety_patterns = [r'#(\s*)?include', r'include', r'##',
                                 r'```.*```', r'`.*`', r'Reboot']
        self._safety_expressions = []

        self._arg_expression = re.compile(r'(?:(?P<pre_proc>.*);;;)?(?:(?P<proc>.*);;)?(?P<to_out>.*)?')

        for patt in self._safety_patterns:
            self._safety_expressions.append(re.compile(patt))

    def get_work_dir(self):
        """Returns the folder where BYOND versions and instances should be saved."""
        cwd = os.getcwd()

        return os.path.join(cwd, self.WORK_FOLDER)

    def new_instance(self, length):
        """Generates a unique instance ID, one which is currently not in use."""
        while True:
            rand = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])

            if rand not in self._instances:
                self._instances.append(rand)
                return rand

    def cleanup_instance(self, instance_id, instance_dir):
        """Deletes all files associated with an instance and removes it from the list."""
        if not os.path.isdir(instance_dir):
            return

        self._instances.remove(instance_id)

        shutil.rmtree(instance_dir, ignore_errors=True)

    def process_args(self, code):
        """
        Generates an array of code segments to be placed into the compiled DM code.
        
        Returned dictionary must have three keys: "pre_proc", "proc", and "to_out".
        If those pieces do not exist, they are to be set as None. As to avoid key
        errors further down the call stack.
        """

        res = self._arg_expression.match(code)

        if not res or not res.groupdict():
            raise BotError("No valid code sent.", "process_args")

        code_segs = {"pre_proc": None, "proc": None, "to_out": None}

        res_dict = res.groupdict()

        for key in code_segs:
            if key in res_dict:
                code_segs[key] = res_dict[key]

        if (code_segs["pre_proc"] and 
                not code_segs["pre_proc"].endswith(";") and 
                not code_segs["pre_proc"].endswith("}")):
            code_segs["pre_proc"] += ";"

        if (code_segs["proc"] and not code_segs["proc"].endswith(";")
            and not code_segs["proc"].endswith(";")):
            code_segs["proc"] += ";"

        if code_segs["to_out"]:
            code_segs["to_out"] = code_segs["to_out"].split(";")

        return code_segs

    def validate_dm(self, code):
        """Validates the code given for potential exploits."""

        for expr in self._safety_expressions:
            if expr.search(code):
                raise BotError("Disallowed/dangerous code found. Aborting.", "validate_dm")

    def generate_dm(self, segments, instance_dir):
        """Generates the .dme file to be compiled."""
        with open(f"{instance_dir}\\eval.dme", "w+") as f:
            if not segments["pre_proc"]:
                segments["pre_proc"] = ""

            if segments["to_out"]:
                var_dump = ""
                for var in segments["to_out"]:
                    var_dump += f"world.log << {var};"

                segments["to_out"] = var_dump

                self.validate_dm(var_dump)
            else:
                segments["to_out"] = ""

            if not segments["proc"]:
                segments["proc"] = ""

            output = self.DM_BOILERPLATE
            output = output.format(segments["pre_proc"], segments["proc"], segments["to_out"])

            f.write(output)

    async def compile_dm(self, loop, instance_dir, major, minor):
        """Executor proc to compile the .dme file provided."""
        dm_path = os.path.join(self.get_work_dir(),
                               f"byond{major}.{minor}\\byond\\bin\\dm.exe")
        if not os.path.isfile(dm_path):
            raise BotError("dm.exe not found.", "compile_dm")

        dme_path = os.path.join(instance_dir, "eval.dme")
        if not os.path.isfile(dme_path):
            raise BotError(".dme under evaluation not found.", "compile_dm")

        process = await asyncio.create_subprocess_exec(*[dm_path, dme_path], loop=loop,
                                                       stderr=asyncio.subprocess.DEVNULL,
                                                       stdout=asyncio.subprocess.DEVNULL)

        try:
            await asyncio.wait_for(process.wait(), timeout=60.0, loop=loop)
        except TimeoutError:
            raise BotError("Compiler timed out.", "compile_dm")

        if process.returncode != 0:
            raise BotError("Error compiling or running DM.", "compile_dm")

    def validate_compile(self, instance_dir):
        """Checks wether or not the compiled end result is safe to run."""
        dmb_found = False

        for fname in os.listdir(instance_dir):
            if fname.endswith(".rsc"):
                raise BotError("Resource file detected. Execution aborted.", "validate_compile")
            elif fname.endswith(".dmb"):
                dmb_found = True

        if not dmb_found:
            raise BotError("Compilation failed and no .dmb was generated.", "validate_compile")

    async def run_dm(self, loop, instance_dir, major, minor):
        """Executor proc to host and run the .dmb file provided."""
        dd_path = os.path.join(self.get_work_dir(),
                               f"byond{major}.{minor}\\byond\\bin\\dreamdaemon.exe")
        if not os.path.isfile(dd_path):
            raise BotError("dreadaemon.exe not found.", "run_dm")

        dmb_path = os.path.join(instance_dir, "eval.dmb")
        if not os.path.isfile(dmb_path):
            raise BotError(".dmb under evaluation not found.", "run_dm")

        p_args = [dd_path, dmb_path] + ["-invisible", "-ultrasafe", "-logself", "-log", "output.log", "-once", "-close", "-quiet"]

        process = await asyncio.create_subprocess_exec(*p_args, loop=loop,
                                                       stderr=asyncio.subprocess.DEVNULL,
                                                       stdout=asyncio.subprocess.DEVNULL)

        try:
            await asyncio.wait_for(process.wait(), timeout=60.0, loop=loop)
        except TimeoutError:
            raise BotError("DreamDaemon timed out.", "run_dm")

    async def run_executor(self, proc, p_args):
        """A helper for running Windows subprocesses in a separate thread."""
        thread = WindowsProcessThread(proc, p_args)

        thread.start()

        cycles = 0

        while cycles < 60:
            if not thread.is_alive():
                break

            cycles += 1
            await asyncio.sleep(1)

        error = thread.errored
        error_msg = thread.error_msg

        thread.join()

        if error:
            raise BotError(error_msg, "run_executor")

    def get_output(self, instance_dir):
        """Returns a string containing the first 30 lines from the test instance's log."""
        log_path = os.path.join(instance_dir, "output.log")
        if not os.path.isfile(log_path):
            return "Error: no log file found."

        with open(log_path, "r") as file:
            content = file.readlines()

        if len(content) < 2:
            return "No contents found in the log file."

        content = [x.strip() for x in content]
        content = content[1:11]
        content = "\n".join(content)
        
        if len(content) > 1750:
            content = content[0:1750] + "\n...Cut-off reached..."

        out = "World.log output:\n```\n" + content + "\n```"

        return out

    def byond_found(self, major=DEFAULT_MAJOR, minor=DEFAULT_MINOR):
        """Checks whether or not the specified version is already found in the test folder."""
        path = self.get_work_dir()

        byond_path = os.path.join(path, f"byond{major}.{minor}")

        if os.path.isdir(byond_path) and os.path.isfile(f"{byond_path}\\byond\\bin\\dm.exe"):
            return True

        return False

    async def setup_byond(self, major=DEFAULT_MAJOR, minor=DEFAULT_MINOR):
        """Downloads and unzips the provided BYOND version."""
        path = self.get_work_dir()
        byond_path = os.path.join(path, f"byond{major}.{minor}")

        url = f"http://www.byond.com/download/build/{major}/{major}.{minor}_byond.zip"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                try:
                    data = await resp.read()
                except Exception:
                    raise BotError("Unable to download the BYOND zip file.", "init_byond")

                if resp.status != 200:
                    raise BotError("Unable to download the specified BYOND version.", "init_byond")

                with ZipFile(BytesIO(data)) as z:
                    z.extractall(byond_path)

    @commands.command(aliases=["dmeval", "dme"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dm_eval(self, ctx, *, code):
        """
        Evaluates given DM code by compiling and running it. Accepts a maximum 
        of 4 formatted arguments: v:{byond_major}.{byond.minor} {global_code};;;{eval_code};;{vars;to;log}.

        All arguments other than {vars;to;log} are optional and may simply be omitted.
        So at bare minimum you simply need to write some variables/expressions to be
        evaluated and printed to world.log.
        """
        try:
            version_tuple = validate_byond_build(code)

            if not version_tuple:
                version_tuple = (DEFAULT_MAJOR, DEFAULT_MINOR)
            else:
                code = code[(code.find(" ") + 1):]

            if not self.byond_found(*version_tuple):
                await ctx.send(f"Version {version_tuple[0]}.{version_tuple[1]} not cached. Downloading. (This may take a bit.)")
                await self.setup_byond(*version_tuple)
        except BotError as err:
            await ctx.send(f"Error while setting up BYOND:\n{err}")
            return
        except Exception:
            await ctx.send(f"Unrecognized exception while setting up BYOND.")
            return

        instance = self.new_instance(32)

        instance_folder = os.path.join(self.get_work_dir(), f"_instances\\{instance}")
        if not os.path.isdir(instance_folder):
            os.makedirs(instance_folder)

        try:
            segs = self.process_args(code)

            self.generate_dm(segs, instance_folder)

            executor_args = [instance_folder, version_tuple[0], version_tuple[1]]

            await self.run_executor(self.compile_dm, executor_args)

            self.validate_compile(instance_folder)

            await self.run_executor(self.run_dm, executor_args)
        except BotError as err:
            await ctx.send(f"Error compiling or running code:\n{err}")
        except Exception:
            await ctx.send("Unrecognized error while compiling or running code.")
        else:
            await ctx.send(self.get_output(instance_folder))

        self.cleanup_instance(instance, instance_folder)

    @commands.command(aliases=["dmversion", "dmv"])
    async def dm_version(self, ctx):
        """Reports the default version of BYOND used by dm_eval."""
        await ctx.send(f"The default version of BYOND used for `dm_eval` is: {DEFAULT_MAJOR}.{DEFAULT_MINOR}.")

def setup(bot):
    bot.add_cog(DmCog(bot))