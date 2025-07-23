# ======= 📄 Файл: spam_cog.py =======
import discord
from discord.ext import commands
import json
import os
import logging
import asyncio

class SpamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = 'spam_config.json'
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    'target_channel': None,
                    'spam_message': "SPAM",
                    'spam_delay': 1,
                    'mention_role': None,
                    'is_spamming': False
                }
                self.save_config()
        except Exception as e:
            logging.error(f"Ошибка загрузки конфига: {e}")
            self.config = {
                'target_channel': None,
                'spam_message': "SPAM",
                'spam_delay': 1,
                'mention_role': None,
                'is_spamming': False
            }

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error(f"Ошибка сохранения конфига: {e}")

    async def start_spam(self, ctx=None):
        try:
            if self.config['is_spamming']:
                if ctx:
                    await ctx.send("⚠️ Спам уже активен!")
                return

            if not self.config['target_channel']:
                if ctx:
                    await ctx.send("❌ Целевой канал не установлен! Используйте `!set_channel`")
                return

            channel = self.bot.get_channel(self.config['target_channel'])
            if not channel:
                if ctx:
                    await ctx.send("❌ Канал не найден!")
                return

            self.config['is_spamming'] = True
            self.save_config()

            if ctx:
                await ctx.send(f"✅ СПАМ ЗАПУЩЕН в {channel.mention}! Используйте `!stop` для остановки.")

            while self.config['is_spamming']:
                try:
                    message = self.config['spam_message']
                    if self.config['mention_role']:
                        role_mention = f"<@&{self.config['mention_role']}>"
                        message = f"{role_mention} {message}"

                    await channel.send(message)
                    await asyncio.sleep(self.config['spam_delay'])
                except Exception as e:
                    logging.error(f"Ошибка отправки сообщения: {e}")
                    break

        except Exception as e:
            logging.error(f"Ошибка в start_spam: {e}")
            if ctx:
                await ctx.send("❌ Произошла ошибка при запуске спама")

    @commands.command()
    async def spam(self, ctx):
        """Начать спам в установленный канал"""
        await self.start_spam(ctx)

    @commands.command()
    async def stop(self, ctx):
        """Остановить спам"""
        self.config['is_spamming'] = False
        self.save_config()
        await ctx.send("🛑 Спам остановлен!")

    @commands.command()
    async def set_channel(self, ctx, channel: discord.TextChannel):
        """Установить целевой канал для спама"""
        self.config['target_channel'] = channel.id
        self.save_config()
        await ctx.send(f"🎯 Целевой канал установлен: {channel.mention}")

    @commands.command()
    async def set_message(self, ctx, *, message: str):
        """Установить текст спам-сообщения"""
        self.config['spam_message'] = message
        self.save_config()
        await ctx.send(f"📝 Сообщение установлено: `{message}`")

    @commands.command()
    async def set_delay(self, ctx, delay: float):
        """Установить задержку между сообщениями (в секундах)"""
        if delay < 0.5:
            await ctx.send("⚠️ Минимальная задержка - 0.5 секунды!")
            return
        self.config['spam_delay'] = delay
        self.save_config()
        await ctx.send(f"⏱️ Задержка установлена: `{delay}` секунд")

    @commands.command()
    async def set_role(self, ctx, role: discord.Role):
        """Установить роль для упоминания в спаме"""
        self.config['mention_role'] = role.id
        self.save_config()
        await ctx.send(f"🔔 Роль для упоминания установлена: {role.mention}")

    @commands.command()
    async def remove_role(self, ctx):
        """Убрать упоминание роли в спаме"""
        self.config['mention_role'] = None
        self.save_config()
        await ctx.send("🔕 Упоминание роли убрано")

    @commands.command()
    async def settings(self, ctx):
        """Показать текущие настройки спама"""
        channel = self.bot.get_channel(self.config['target_channel']) if self.config['target_channel'] else None
        role = ctx.guild.get_role(self.config['mention_role']) if self.config['mention_role'] else None

        embed = discord.Embed(title="⚙️ Текущие настройки спама", color=0x00ff00)
        embed.add_field(name="Канал", value=channel.mention if channel else "Не установлен", inline=False)
        embed.add_field(name="Сообщение", value=f"`{self.config['spam_message']}`", inline=False)
        embed.add_field(name="Задержка", value=f"`{self.config['spam_delay']}` сек", inline=False)
        embed.add_field(name="Упоминаемая роль", value=role.mention if role else "Не установлена", inline=False)
        embed.add_field(name="Статус", value="🟢 Активен" if self.config['is_spamming'] else "🔴 Не активен", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="help-spam")
    async def help_spam(self, ctx):
        """Показать список всех команд спама"""
        help_embed = discord.Embed(
            title="📜 Список команд спам-бота",
            description="Все команды используют префикс `!`",
            color=0x00ff00
        )

        commands_info = [
            ("spam", "Начать спам в установленный канал", "!spam"),
            ("stop", "Остановить спам", "!stop"),
            ("set_channel #канал", "Установить целевой канал", "!set_channel #general"),
            ("set_message текст", "Установить текст сообщения", "!set_message Внимание!"),
            ("set_delay число", "Установить задержку (сек)", "!set_delay 1.5"),
            ("set_role @роль", "Установить роль для упоминания", "!set_role @Админы"),
            ("remove_role", "Убрать упоминание роли", "!remove_role"),
            ("settings", "Показать текущие настройки", "!settings"),
            ("help", "Показать эту справку", "!help")
        ]

        for name, desc, example in commands_info:
            help_embed.add_field(
                name=f"!{name}",
                value=f"{desc}\nПример: `{example}`",
                inline=False
            )

        await ctx.send(embed=help_embed)

async def setup(bot):
    await bot.add_cog(SpamCog(bot))