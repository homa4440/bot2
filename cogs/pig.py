from discord.ext import commands
import discord
import json
import os

AUTHORIZED_USER_ID = 624392139052154912  # 🔐 Замени на свой ID
CONFIG_FILE = 'admin_config.json'

class Pig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = {
            'target_user_id': None,
            'response_message': "Привет! Это автоответ.",
            'active': False
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

    def save_config(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    @commands.command()
    async def set_user(self, ctx, user: discord.User):
        if ctx.author.id != AUTHORIZED_USER_ID:
            return await ctx.send("❌ Нет доступа")
        self.config['target_user_id'] = user.id
        self.save_config()
        await ctx.send(f"👤 Пользователь установлен: {user.mention}")

    @commands.command()
    async def set_mes(self, ctx, *, message: str):
        if ctx.author.id != AUTHORIZED_USER_ID:
            return await ctx.send("❌ Нет доступа")
        self.config['response_message'] = message
        self.save_config()
        await ctx.send(f"💬 Сообщение установлено:n`{message}`")

    @commands.command()
    async def on(self, ctx):
        if ctx.author.id != AUTHORIZED_USER_ID:
            return await ctx.send("❌ Нет доступа")
        self.config['active'] = True
        self.save_config()
        await ctx.send("✅ Автоответ включён")

    @commands.command()
    async def off(self, ctx):
        if ctx.author.id != AUTHORIZED_USER_ID:
            return await ctx.send("❌ Нет доступа")
        self.config['active'] = False
        self.save_config()
        await ctx.send("⛔ Автоответ выключен")

    @commands.command(name='admin')
    async def admin_panel(self, ctx):
        if ctx.author.id != AUTHORIZED_USER_ID:
            return await ctx.send("❌ Нет доступа")

        user = self.config['target_user_id']
        msg = self.config['response_message']
        status = "🟢 ВКЛЮЧЕН" if self.config['active'] else "🔴 ВЫКЛЮЧЕН"
        user_display = f"<@{user}>" if user else "не установлен"

        embed = discord.Embed(title="🛠️ Админ-панель", color=0x3498db)
        embed.add_field(name="!set_user @пользователь", value="Целевой пользователь", inline=False)
        embed.add_field(name="!set_message текст", value="Ответное сообщение", inline=False)
        embed.add_field(name="!on / !off", value="Включение / отключение ответа", inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="Пользователь", value=user_display, inline=True)
        embed.add_field(name="Статус", value=status, inline=True)
        embed.add_field(name="Сообщение", value=f"`{msg}`", inline=False)

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not self.config['active']:
            return
        if message.author.id == self.config['target_user_id']:
            try:
                await message.reply(self.config['response_message'])
            except Exception as e:
                print(f"Ошибка при ответе: {e}")

# ✅ Правильная асинхронная регистрация Cog
async def setup(bot):
    await bot.add_cog(Pig(bot))
