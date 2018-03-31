import os
import aiohttp
import random
import string
import asyncio

from io import BytesIO
from zipfile import ZipFile

from discord.ext import commands
from core import BotError

# args:
# dmb -invisible -ultrasafe -logself -log somefile.log -once -quiet

class DmCog:
    DEFAULT_MAJOR = "512"
    DEFAULT_MINOR = "1416"
    WORK_FOLDER = "cogs\\byond_eval"

    DM_BOILERPLATE = "/world/loop_checks = FALSE;\n" + \
                     "\n/world/New() {{ dm_eval(); del(src); }}" + \
                     "\n{0}\n/proc/dm_eval() {{ {1} {2} }}"

    def __init__(self, bot):
        self.bot = bot

        self.current_major = self.DEFAULT_MAJOR
        self.current_minor = self.DEFAULT_MINOR

        self._instances = []

    def get_work_dir(self):
        cwd = os.getcwd()

        return os.path.join(cwd, self.WORK_FOLDER)

    def new_instance(self, length):
        while True:
            rand = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])

            if rand not in self._instances:
                return rand

    def process_args(self, lines):
        code = "".join(lines)

        slices = code.split(";;;")
        code_segs = {"pre_proc": None, "proc": None, "to_out": None}

        if not slices:
            raise BotError("No valid code sent.", "process_args")

        if len(slices) > 1:
            code_segs["pre_proc"] = slices[0]
            slices = slices[1].split(";;")

        code_segs["proc"] = slices[0]

        if len(slices) > 1:
            code_segs["to_out"] = slices[1].split(";")

        return code_segs

    def generate_dm(self, segments, instance_dir):
        with open(f"{instance_dir}\\eval.dme", "w+") as f:
            if not segments["pre_proc"]:
                segments["pre_proc"] = ""

            if segments["to_out"]:
                var_dump = ""
                for var in segments["to_out"]:
                    var_dump += f"world << {var};"

                segments["to_out"] = var_dump
            else:
                segments["to_out"] = ""

            output = self.DM_BOILERPLATE
            output = output.format(segments["pre_proc"], segments["proc"], segments["to_out"])

            f.write(output)

    async def compile_dm(self, instance_dir):
        dm_path = os.path.join(self.get_work_dir(),
                               f"byond{self.current_major}.{self.current_minor}\\byond\\bin\\dm.exe")
        if not os.path.isfile(dm_path):
            raise BotError("dm.exe not found.", "compile_dm")

        dme_path = os.path.join(instance_dir, "eval.dme")
        if not os.path.isfile(dme_path):
            raise BotError(".dme under evaluation not found.", "compile_dm")

        create = asyncio.create_subprocess_exec(dm_path, dme_path, stdout=asyncio.subprocess.PIPE)

        process = await create

        data, _ = await process.communicate()

        if process.returncode != 0:
            raise BotError("Error compiling or running DM.", "compile_dm")

    async def init_byond(self):
        path = self.get_work_dir()

        byond_path = os.path.join(path, f"byond{self.current_major}.{self.current_minor}")

        if os.path.isdir(byond_path) and os.path.isfile(f"{byond_path}\\byond\\bin\\dm.exe"):
            return

        url = f"http://www.byond.com/download/build/{self.current_major}/{self.current_major}.{self.current_minor}_byond.zip"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                try:
                    data = await resp.read()
                except Exception:
                    raise BotError("Unable to download the BYOND zip file.", "init_byond")

                with ZipFile(BytesIO(data)) as z:
                    z.extractall(byond_path)

    @commands.command()
    @commands.is_owner()
    async def dm_test(self, ctx, *lines):
        try:
            await self.init_byond()
        except Exception as err:
            await ctx.send(f"Aaaaa: {err}")
            return

        instance = self.new_instance(32)

        instance_folder = os.path.join(self.get_work_dir(), f"_instances\\{instance}")
        if not os.path.isdir(instance_folder):
            os.makedirs(instance_folder)

        try:
            segs = self.process_args(lines)

            self.generate_dm(segs, instance_folder)

            await self.compile_dm(instance_folder)
        except BotError as err:
            await ctx.send(f"Error running prechecks: {err}")
        except Exception as err:
            await ctx.send(f"Aaaaaa {str(err)}")

def setup(bot):
    bot.add_cog(DmCog(bot))