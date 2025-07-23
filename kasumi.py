import discord
from discord.ext import commands
import json
import os
import logging
import asyncio

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DISCORD_TOKEN = "MTM3NzY5MTQzNzA1OTE0NTkxMA.Ge4OPt.R_250rQ-wTGg9OtNzq5fBjP_K8JSq85kM56JUg"  # ← Замени на свой токен


class Kasumi(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )

        self.config_file = 'spam_config.json'
        self.config = {}
        self.load_config()

    def get_guild_config(self, guild_id):
        gid = str(guild_id)
        if gid not in self.config:
            self.config[gid] = {
                'target_channel': None,
                'spam_message': "SPAM",
                'spam_delay': 1,
                'mention_role': None,
                'is_spamming': False
            }
        return self.config[gid]

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
        except Exception as e:
            logging.error(f"Ошибка загрузки конфига: {e}")
            self.config = {}

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error(f"Ошибка сохранения конфига: {e}")

    async def on_ready(self):
        logging.info(f'Бот {self.user} готов к работе!')
        await self.change_presence(activity=discord.Game(name="!help для списка команд"))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        logging.error(f"Ошибка команды: {error}")
        await ctx.send(f"❌ Ошибка: {str(error)}")

    async def load_startup_cogs(self):
        cog_list = self.config.get("startup_cogs", [])
        for cog in cog_list:
            try:
                await self.load_extension(f'cogs.{cog}')
                logging.info(f'Загружен cog: cogs.{cog}')
            except Exception as e:
                logging.error(f'Ошибка при загрузке cogs.{cog}: {e}')


def setup_commands(bot: Kasumi):
    @bot.command(name='help')
    async def help_command(ctx):
        help_embed = discord.Embed(
            title="📜 Список команд бота",
            description="Все команды используют префикс `!`",
            color=0x00ff00
        )

        commands_info = [
            ("load <name>", "Загрузить указанный cog", "!load spamm"),
            ("reload <name>", "Перезагрузить cog", "!reload spamm"),
            ("addcog <name>", "Добавить cog в автозагрузку", "!addcog spamm"),
            ("showcogs", "Показать список автозагружаемых cog-ов", "!showcogs"),
            ("removecog <name>", "Удалить cog из автозагрузки", "!removecog spamm")
        ]

        for cmd, desc, example in commands_info:
            help_embed.add_field(
                name=f"!{cmd}",
                value=f"{desc}\nПример: `{example}`",
                inline=False
            )

        await ctx.send(embed=help_embed)

    @bot.command()
    async def load(ctx, name: str):
        path = f'cogs/{name}.py'
        if not os.path.isfile(path):
            return await ctx.send(f"❌ Файл `{path}` не найден.")

        try:
            await bot.load_extension(f'cogs.{name}')
            await ctx.send(f"✅ Cog `{name}` загружен.")
        except commands.ExtensionAlreadyLoaded:
            await ctx.send(f"⚠️ Cog `{name}` уже загружен.")
        except Exception as e:
            await ctx.send(f"❌ Ошибка при загрузке `{name}`:\n```{e}```")

    @bot.command()
    async def reload(ctx, name: str):
        try:
            await bot.unload_extension(f'cogs.{name}')
            await bot.load_extension(f'cogs.{name}')
            await ctx.send(f"♻️ Cog `{name}` перезагружен.")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"⚠️ Cog `{name}` не был загружен ранее.")
        except Exception as e:
            await ctx.send(f"❌ Ошибка при перезагрузке `{name}`:\n```{e}```")

    @bot.command()
    async def addcog(ctx, name: str):
        cogs = bot.config.get("startup_cogs", [])
        if name in cogs:
            return await ctx.send(f"⚠️ Cog `{name}` уже в списке автозагрузки.")

        cogs.append(name)
        bot.config["startup_cogs"] = cogs
        bot.save_config()
        await ctx.send(f"✅ Cog `{name}` добавлен в автозагрузку.\nТеперь загружаются:\n```{', '.join(cogs)}```")

    @bot.command()
    async def showcogs(ctx):
        cogs = bot.config.get("startup_cogs", [])
        if not cogs:
            await ctx.send("❌ Стартовые cog-и не заданы.")
        else:
            await ctx.send(f"📦 Загружаемые при запуске cog-и:\n```{', '.join(cogs)}```")

    @bot.command()
    async def removecog(ctx, name: str):
        cogs = bot.config.get("startup_cogs", [])
        if name not in cogs:
            return await ctx.send(f"⚠️ Cog `{name}` не найден в списке автозагрузки.")

        cogs.remove(name)
        bot.config["startup_cogs"] = cogs
        bot.save_config()
        await ctx.send(f"🗑️ Cog `{name}` удалён из автозагрузки.\nТеперь загружаются:\n```{', '.join(cogs) or 'ничего'}```")


async def start_bot():
    logging.info("Запуск бота...")
    bot = Kasumi()
    setup_commands(bot)
    await bot.load_startup_cogs()
    await bot.start(DISCORD_TOKEN)


def main():
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()
