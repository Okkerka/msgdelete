from redbot.core import commands, Config
import discord

class MessageDelete(commands.Cog):
    """Automatically deletes messages from specific users."""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_global = {
            "blocked_users": []
        }
        self.config.register_global(**default_global)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Delete messages from blocked users."""
        # Ignore messages from bots to avoid potential loops
        if message.author.bot:
            return
        
        # Get the list of blocked users
        blocked_users = await self.config.blocked_users()
        
        # Check if the message is from a blocked user
        if message.author.id in blocked_users:
            try:
                await message.delete()
                print(f"Deleted message from user {message.author.id} in {message.guild.name if message.guild else 'DMs'}")
            except discord.Forbidden:
                print(f"Missing permissions to delete message in {message.channel.name}")
            except discord.HTTPException as e:
                print(f"Failed to delete message: {e}")
    
    @commands.group()
    @commands.is_owner()
    async def msgblock(self, ctx):
        """Manage users whose messages are automatically deleted."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @msgblock.command(name="add")
    async def msgblock_add(self, ctx, user_id: int):
        """Add a user to the message deletion list.
        
        Usage: [p]msgblock add <user_id>
        """
        blocked_users = await self.config.blocked_users()
        
        if user_id in blocked_users:
            await ctx.send(f"❌ User ID `{user_id}` is already in the blocked list.")
            return
        
        blocked_users.append(user_id)
        await self.config.blocked_users.set(blocked_users)
        await ctx.send(f"✅ Added user ID `{user_id}` to the message deletion list.")
    
    @msgblock.command(name="remove")
    async def msgblock_remove(self, ctx, user_id: int):
        """Remove a user from the message deletion list.
        
        Usage: [p]msgblock remove <user_id>
        """
        blocked_users = await self.config.blocked_users()
        
        if user_id not in blocked_users:
            await ctx.send(f"❌ User ID `{user_id}` is not in the blocked list.")
            return
        
        blocked_users.remove(user_id)
        await self.config.blocked_users.set(blocked_users)
        await ctx.send(f"✅ Removed user ID `{user_id}` from the message deletion list.")
    
    @msgblock.command(name="list")
    async def msgblock_list(self, ctx):
        """Show all users in the message deletion list.
        
        Usage: [p]msgblock list
        """
        blocked_users = await self.config.blocked_users()
        
        if not blocked_users:
            await ctx.send("📝 The message deletion list is empty.")
            return
        
        user_list = "\n".join([f"• `{user_id}`" for user_id in blocked_users])
        embed = discord.Embed(
            title="🚫 Blocked Users List",
            description=user_list,
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Total: {len(blocked_users)} user(s)")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MessageDelete(bot))