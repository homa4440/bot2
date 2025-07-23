import discord
from discord.ext import commands
from discord import Embed
from datetime import datetime

class SenderReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = None  # ID канала для отправки сообщений в памяти

    def get_channel(self):
        if self.channel_id:
            return self.bot.get_channel(self.channel_id)
        return None

    @commands.command()
    async def send(self, ctx, *, message: str):
        """Отправить сообщение в указанный канал"""
        channel = self.get_channel()
        if not channel:
            return await ctx.send("❌ Целевой канал не установлен. Используй команду `!sendchannel set <channel_id>`.")
        try:
            await channel.send(message)
            await ctx.send("✅ Сообщение отправлено.")
        except discord.Forbidden:
            await ctx.send("⚠️ У меня нет прав на отправку сообщений в этот канал.")
        except Exception as e:
            await ctx.send(f"❌ Ошибка: {e}")

    @commands.group()
    async def sendchannel(self, ctx):
        """Управление целевым каналом"""
        if ctx.invoked_subcommand is None:
            await ctx.send("❗ Используй: `!sendchannel set <channel_id>`")

    @sendchannel.command()
    async def set(self, ctx, channel_id: int):
        """Установить ID канала для отправки"""
        channel = self.bot.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            return await ctx.send("❌ Канал не найден или не является текстовым.")
        self.channel_id = channel.id
        await ctx.send(f"✅ Канал установлен: {channel.mention}")

    # Обновлённая команда help-report (без параметров)
    @commands.command()
    async def help_report(self, ctx):
        help_embed = Embed(
            title="📋 Правила ГП Шахтёрский Союз [DRGS]",
            description="Проcьба, соблюдать данные правила",
            color=0x00FF00
        )

        fields = [
            ("1. Соблюдайте адекватное поведение на сервере — как в текстовых, так и в голосовых каналах."),
            ("2. Слушайте лидера или полковника, особенно если вам делают замечания или сообщают важную информацию."),
            ("3. Оскорбления участников сервера строго запрещены. Допускается шутливая форма, но важно не переходить границы адекватности."),
            ("4. Запрещено распространять ложную информацию о клане, других источниках, связанных с кланами, а также о проекте STALCRAFT в целом."),
            ("5. Использование Soundpad разрешено, но не чаще одного звука в полминуты. То же правило распространяется на звуковую панель в Discord."),
            ("6. Запрещено намеренно мешать лидеру или полковнику во время оглашения информации в голосовом или текстовом чате."),
            ("7. Отгулы следует писать по установленной форме — это поможет быстрее определить, кто не сможет прийти на КВ."),
        ]

        for field in fields:
            help_embed.add_field(name=field, value="", inline=False)

        await ctx.send(embed=help_embed)

    @commands.command(name="help-mess")
    async def help_mess(self, ctx):
        help_embed = Embed(
            title="📋 Команды отправки сообщений",
            description="Используйте префикс `!` перед командами",
            color=0x00ff00
        )

        commands_info = [
            ("sendchannel set <channel_id>", "Установить канал для отправки сообщений", "!sendchannel set 123456789012345678"),
            ("send <сообщение>", "Отправить сообщение в установленный канал", "!send Привет, мир!"),
            ("help-report", "Показать информацию о формате отчёта", "!help-report"),
            ("help-mess", "Показать эту справку", "!help-mess")
        ]

        for name, desc, example in commands_info:
            help_embed.add_field(
                name=f"!{name}",
                value=f"{desc}\nПример: `{example}`",
                inline=False
            )

        await ctx.send(embed=help_embed)

async def setup(bot):
    await bot.add_cog(SenderReport(bot))
