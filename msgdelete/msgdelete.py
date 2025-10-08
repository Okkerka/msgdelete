from redbot.core import commands, Config
import discord

class MessageDelete(commands.Cog):
    """Automatically deletes messages from specific users."""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "blocked_users": []
        }
        self.config.register_guild(**default_guild)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Delete messages from blocked users."""
        # Only work in guilds (servers), not DMs
        if not message.guild:
            return
        
        # Ignore messages from bots to avoid potential loops
        if message.author.bot:
            return
        
        # Get the list of blocked users for this guild
        blocked_users = await self.config.guild(message.guild).blocked_users()
        
        # Check if the message is from a blocked user
        if message.author.id in blocked_users:
            try:
                await message.delete()
                print(f"Deleted message from user {message.author.id} in {message.guild.name}")
            except discord.Forbidden:
                print(f"Missing permissions to delete message in {message.channel.name}")
            except discord.HTTPException as e:
                print(f"Failed to delete message: {e}")
    
    @commands.group()
    @commands.is_owner()
    @commands.guild_only()
    async def msgblock(self, ctx):
        """Manage users whose messages are automatically deleted in this server."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @msgblock.command(name="add")
    async def msgblock_add(self, ctx, user_id: int):
        """Add a user to the message deletion list for this server.
        
        Usage: [p]msgblock add <user_id>
        """
        blocked_users = await self.config.guild(ctx.guild).blocked_users()
        
        if user_id in blocked_users:
            await ctx.send(f"❌ User ID `{user_id}` is already in the blocked list for this server.")
            return
        
        blocked_users.append(user_id)
        await self.config.guild(ctx.guild).blocked_users.set(blocked_users)
        await ctx.send(f"✅ Added user ID `{user_id}` to the message deletion list for this server.")
    
    @msgblock.command(name="remove")
    async def msgblock_remove(self, ctx, user_id: int):
        """Remove a user from the message deletion list for this server.
        
        Usage: [p]msgblock remove <user_id>
        """
        blocked_users = await self.config.guild(ctx.guild).blocked_users()
        
        if user_id not in blocked_users:
            await ctx.send(f"❌ User ID `{user_id}` is not in the blocked list for this server.")
            return
        
        blocked_users.remove(user_id)
        await self.config.guild(ctx.guild).blocked_users.set(blocked_users)
        await ctx.send(f"✅ Removed user ID `{user_id}` from the message deletion list for this server.")
    
    @msgblock.command(name="list")
    async def msgblock_list(self, ctx):
        """Show all users in the message deletion list for this server.
        
        Usage: [p]msgblock list
        """
        blocked_users = await self.config.guild(ctx.guild).blocked_users()
        
        if not blocked_users:
            await ctx.send("📝 The message deletion list is empty for this server.")
            return
        
        user_list = []
        for user_id in blocked_users:
            member = ctx.guild.get_member(user_id)
            if member:
                # User is in the server - show name and ID
                user_list.append(f"• {member.mention} (`{member.name}` - `{user_id}`)")
            else:
                # User not in server - just show ID
                user_list.append(f"• `{user_id}` (Not in server)")
        
        embed = discord.Embed(
            title=f"🚫 Blocked Users List - {ctx.guild.name}",
            description="\n".join(user_list),
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Total: {len(blocked_users)} user(s)")
        await ctx.send(embed=embed)
    
    @commands.command(hidden=True)
    async def thanos(self, ctx):
        """A hidden Thanos command."""
        embed = discord.Embed(color=discord.Color.purple())
        embed.set_image(url="https://imgur.com/a/iV2kXUJ")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MessageDelete(bot))