import discord
from discord.ext import commands
import json
import os
from datetime import datetime

LOG_CONFIG_FILE = 'log_config.json'

def load_log_config():
    if not os.path.exists(LOG_CONFIG_FILE):
        return {"log_guilds": [], "target_user_id": None}
    with open(LOG_CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_log_config(config):
    with open(LOG_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_log_config()

    def is_logging_enabled(self, guild: discord.Guild):
        return guild and guild.id in self.config.get("log_guilds", [])

    async def send_log(self, guild, content):
        user_id = self.config.get("target_user_id")
        if not user_id:
            return
        user = self.bot.get_user(user_id)
        if not user:
            try:
                user = await self.bot.fetch_user(user_id)
            except:
                return

        prefix = (
            f"[🛡️ Сервер: {guild.name}]\n" if guild else "[📬 Приватное сообщение боту]\n"
        )
        prefix += f"[🕒 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n"
        try:
            await user.send(prefix + content)
        except discord.Forbidden:
            pass

    # ========== События сообщений ==========
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # 🔹 Логирование ЛС
        if message.guild is None:
            content = (
                f"[📩 ЛС]\n"
                f"[👤 {message.author}]\n"
                f"📨 Сообщение в ЛС:\n"
                f"{message.content}"
            )
            await self.send_log(None, content)
            return

        # 🔹 Логирование серверных сообщений
        if not self.is_logging_enabled(message.guild):
            return
        if message.type != discord.MessageType.default:
            return
        content = (
            f"[👤 {message.author}]\n"
            f"📨 Сообщение в #{message.channel}:\n"
            f"{message.content}"
        )
        await self.send_log(message.guild, content)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not self.is_logging_enabled(message.guild):
            return
        content = (
            f"[👤 {message.author}]\n"
            f"❌ Удалено сообщение из #{message.channel}:\n"
            f"{message.content}"
        )
        await self.send_log(message.guild, content)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not self.is_logging_enabled(before.guild):
            return
        if before.content == after.content:
            return
        content = (
            f"[👤 {before.author}]\n"
            f"✏️ Редактировано в #{before.channel}:\n"
            f"До: {before.content}\nПосле: {after.content}"
        )
        await self.send_log(before.guild, content)

    # ========== Участники ==========
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not self.is_logging_enabled(member.guild):
            return
        await self.send_log(member.guild, f"➕ Пользователь зашёл на сервер: {member}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not self.is_logging_enabled(member.guild):
            return
        await self.send_log(member.guild, f"➖ Пользователь покинул сервер: {member}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not self.is_logging_enabled(before.guild):
            return
        changes = []
        added = [r for r in after.roles if r not in before.roles]
        removed = [r for r in before.roles if r not in after.roles]
        if added:
            changes.append("🟢 Добавлены роли: " + ", ".join(r.name for r in added))
        if removed:
            changes.append("🔴 Удалены роли: " + ", ".join(r.name for r in removed))
        if before.nick != after.nick:
            changes.append(f"📝 Ник: {before.nick} → {after.nick}")
        if changes:
            await self.send_log(before.guild, f"[👤 {before}]\n" + "\n".join(changes))

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:
            content = f"👤 Пользователь сменил имя:\n{before} → {after}"
            for guild in self.bot.guilds:
                if self.is_logging_enabled(guild):
                    await self.send_log(guild, content)

    # ========== Голос ==========
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not self.is_logging_enabled(member.guild):
            return
        if before.channel != after.channel:
            if after.channel and not before.channel:
                action = f"🔊 {member} подключился к голосовому каналу: {after.channel.name}"
            elif before.channel and not after.channel:
                action = f"🔇 {member} вышел из голосового канала: {before.channel.name}"
            else:
                action = f"🔁 {member} перешёл из {before.channel.name} в {after.channel.name}"
            await self.send_log(member.guild, action)

    # ========== Каналы ==========
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if self.is_logging_enabled(channel.guild):
            await self.send_log(channel.guild, f"📁 Создан канал: #{channel.name}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if self.is_logging_enabled(channel.guild):
            await self.send_log(channel.guild, f"🗑️ Удалён канал: #{channel.name}")

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if self.is_logging_enabled(before.guild):
            changes = []
            if before.name != after.name:
                changes.append(f"📛 Название: {before.name} → {after.name}")
            if before.overwrites != after.overwrites:
                changes.append("🔐 Изменились права доступа.")
            if changes:
                await self.send_log(before.guild, f"🔧 Обновлён канал #{before.name}:\n" + "\n".join(changes))

    # ========== Роли ==========
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        if self.is_logging_enabled(role.guild):
            await self.send_log(role.guild, f"🎖️ Создана роль: {role.name}")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if self.is_logging_enabled(role.guild):
            await self.send_log(role.guild, f"❌ Удалена роль: {role.name}")

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if self.is_logging_enabled(before.guild):
            changes = []
            if before.name != after.name:
                changes.append(f"📛 Название: {before.name} → {after.name}")
            if before.permissions != after.permissions:
                changes.append("🔐 Изменены права доступа.")
            if changes:
                await self.send_log(before.guild, f"⚙️ Обновлена роль {before.name}:\n" + "\n".join(changes))

    # ========== Системные ==========
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if self.is_logging_enabled(guild):
            await self.send_log(guild, f"🔨 Забанен пользователь: {user}")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if self.is_logging_enabled(guild):
            await self.send_log(guild, f"🎉 Разбанен пользователь: {user}")

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if self.is_logging_enabled(before):
            if before.name != after.name:
                await self.send_log(before, f"🏷️ Сервер переименован: {before.name} → {after.name}")

    # ========== Реакции ==========
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or not self.is_logging_enabled(reaction.message.guild):
            return
        await self.send_log(
            reaction.message.guild,
            f"➕ {user} добавил реакцию {reaction.emoji} в #{reaction.message.channel}"
        )

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot or not self.is_logging_enabled(reaction.message.guild):
            return
        await self.send_log(
            reaction.message.guild,
            f"➖ {user} убрал реакцию {reaction.emoji} в #{reaction.message.channel}"
        )

    # ========== Команды ==========
    @commands.command()
    async def logtarget(self, ctx, member: discord.User):
        self.config["target_user_id"] = member.id
        save_log_config(self.config)
        await ctx.send(f"✅ Теперь логи будут отправляться в ЛС пользователю {member}.")

    @commands.command()
    async def logserver(self, ctx, action: str, guild_id: int):
        guilds = self.config.get("log_guilds", [])
        if action == "add":
            if guild_id in guilds:
                return await ctx.send("⚠️ Сервер уже в списке.")
            guilds.append(guild_id)
            await ctx.send("✅ Сервер добавлен в список логирования.")
        elif action == "remove":
            if guild_id not in guilds:
                return await ctx.send("⚠️ Сервер не в списке.")
            guilds.remove(guild_id)
            await ctx.send("✅ Сервер удалён из логирования.")
        else:
            return await ctx.send("❌ Используй `add` или `remove`.")
        self.config["log_guilds"] = guilds
        save_log_config(self.config)

    @commands.command()
    async def logservers(self, ctx):
        ids = self.config.get("log_guilds", [])
        if not ids:
            return await ctx.send("📭 Список пуст.")
        await ctx.send("📋 Список логируемых серверов:\n```\n" + "\n".join(map(str, ids)) + "\n```")

    @commands.command(name="help-log")
    async def help_log(self, ctx):
        help_embed = discord.Embed(
            title="📚 Справка по логированию",
            description="Команды для настройки логирования бота.",
            color=0x00FF00,
            timestamp=datetime.utcnow()
        )
        commands_info = [
            ("logtarget <пользователь>", "Устанавливает пользователя, которому будут приходить логи в ЛС.", "`!logtarget @User`"),
            ("logserver add <guild_id>", "Добавляет сервер в список логирования.", "`!logserver add 123456789012345678`"),
            ("logserver remove <guild_id>", "Удаляет сервер из списка логирования.", "`!logserver remove 123456789012345678`"),
            ("logservers", "Показывает список серверов, с которых собираются логи.", "`!logservers`"),
        ]
        for name, desc, example in commands_info:
            help_embed.add_field(name=f"!{name}", value=f"{desc}\nПример: {example}", inline=False)

        await ctx.send(embed=help_embed)

async def setup(bot):
    await bot.add_cog(Logger(bot))
