import discord
from discord.ext import commands, tasks
import aiohttp


class EmissionAlert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_ids = [827817877557477408, 653566920393490442, 624392139052154912]  # ID пользователей
        self.api_base = "https://dapi.stalcraft.net"  # Демонстрационное API
        self.last_status = None
        self.check_emission.start()

    def cog_unload(self):
        self.check_emission.cancel()

    @tasks.loop(seconds=60)
    async def check_emission(self):
        url = f"{self.api_base}/public/emission"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        print(f"[EmissionChecker] Ответ: {response.status}")
                        return

                    data = await response.json()

                    is_active = data.get("active", False)

                    if is_active and self.last_status != True:
                        await self.notify_users()
                        self.last_status = True
                    elif not is_active:
                        self.last_status = False

        except Exception as e:
            print(f"[EmissionChecker] Ошибка при запросе API: {e}")

    async def notify_users(self):
        for user_id in self.user_ids:
            user = self.bot.get_user(user_id)
            if user:
                try:
                    embed = discord.Embed(
                        title="☢️ ВЫБРОС В STALCRAFT!",
                        description="Срочно укрывайся в безопасном месте!",
                        color=0xff0000
                    )
                    embed.set_footer(text="По данным STALCRAFT DEMO API")
                    await user.send(embed=embed)
                except discord.Forbidden:
                    print(f"❌ Не могу отправить сообщение пользователю {user_id} (нет прав)")


async def setup(bot):
    await bot.add_cog(EmissionAlert(bot))
