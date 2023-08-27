import helpers
from loguru import logger
import discord
from config import settings
from discord.ext import commands, tasks
from DataBases import cursor
from datetime import datetime
from pytz import timezone


db = cursor.DataBase()
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@client.event
async def on_ready():
    logger.info("The bot is working now")
    logger.info("-------------------------------------------")
    for guild in client.guilds:
        # Adding each guild's invites to our dict
        settings.INVITES[guild.id] = await guild.invites()
    statistic_message.start()
    # set_banner.start()  # starts loop of banner updating


@client.event
async def on_message(ctx):
    if not ctx.author.bot:
        db.save_statistic("messages", ctx.guild.id)
    await client.process_commands(ctx)


@client.event
async def on_message_delete(message: discord.Message):
    """Sends discord.Embed when message deletes to logs channel"""
    channel = client.get_channel(settings.LOGS_GUILD_LIST[message.guild.id]) 
    await channel.send(embed=helpers.log_delete(message))
    for attachment in message.attachments:
        await channel.send(attachment.url)
    if message.embeds:
        await channel.send(embeds=message.embeds)
        await channel.send(embed=helpers.split_embed())
    if len(str(message.content)) >= 2000:
        await channel.send(file=discord.File(helpers.log_txt_delete(str(message.content)), "message.txt"))
    elif 2000 > len(str(message.content)) >= 256:
        await channel.send(str(message.content))
        await channel.send(embed=helpers.split_embed())


@client.event
async def on_message_edit(message_before: discord.Message, message_after: discord.Message):
    """Sends discord.Embed when message changes to logs channel"""
    if message_before.content != message_after.content:
        channel = client.get_channel(settings.LOGS_GUILD_LIST[message_before.guild.id])

        is_message_too_big = len(str(message_before.content)) >= 2000 or len(str(message_after.content)) >= 2000

        if is_message_too_big:
            # if message > 2000
            helpers.log_txt_edit(message_before, message_after)
            with open("message.txt", "rb") as file:
                await channel.send(file=discord.File(file, "message.txt"))

        elif 2000 > len(str(message_before.content)) > 256 or 2000 > len(str(message_after.content)) > 256:
            # if 2000 > message > 256
            await channel.send(str(message_before.content))
            embed = discord.Embed(title="To:")
            await channel.send(embed=embed)
            await channel.send(str(message_after.content))
            await channel.send(embed=helpers.split_embed())
        else:
            # if message < 256
            await channel.send(embed=helpers.log_edit(message_before, message_after))


@client.event
async def on_member_remove(member):
    """log of leaving server"""
    channel = client.get_channel(settings.LOGS_GUILD_LIST[member.guild.id])
    await channel.send(embed=helpers.leave_log(member))
    db.save_statistic("people removed", member.guild.id)


@client.event
async def on_member_join(member):
    """logs of joining server"""
    channel = client.get_channel(settings.LOGS_GUILD_LIST[member.guild.id])
    await channel.send(embed=helpers.join_log(member))
    db.save_statistic("people joined", member.guild.id)
    invites_before_join = settings.INVITES[member.guild.id]
    invites_after_join = await member.guild.invites()
    for invite in invites_before_join:
        if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:
            embed = discord.Embed(title=f"Inviter: {invite.inviter}")
            embed.add_field(name="Invite Code: ", value=invite.code)
            await channel.send(embed=embed)
            settings.INVITES[member.guild.id] = invites_after_join
            return


@tasks.loop(seconds=20.0)
async def set_banner(ctx):
    # Every 20 seconds changes guild banner with current number of voice members
    # and members of channel
    guild = client.get_guild(ctx.guild.id)
    helpers.gif_edit(
        settings.BANNER_LOCATION, settings.EDITED_BANNER_LOCATION, guild, settings.COORDINATES_X, settings.COORDINATES_Y
    )
    with open(settings.EDITED_BANNER_LOCATION, "rb") as file:
        banner = file.read()
    await guild.edit(banner=banner)


@tasks.loop(minutes=10)
async def statistic_message():
    kyiv = timezone("Europe/Kiev")
    kv_time = datetime.now(kyiv)
    time_now = kv_time.strftime("%H")
    if time_now == "00":
        for generator in db.get_statistic():
            for row in generator:
                statistic_channel_id = db.get_id(row[0])
                if statistic_channel_id:
                    channel = client.get_channel(db.get_id(row[0])[0][0])
                    message_text = f"Today {row[1]}: {row[2]}\n"
                    await channel.send(embed=helpers.statistic_embed(message_text))


@client.event
async def on_voice_state_update(member, before, after):
    db.save_statistic("muted", member.guild.id)
    # sends logs about self_mute status
    if before.self_mute != after.self_mute:
        channel = client.get_channel(settings.MICROPHONE_GUILD_LIST[member.guild.id])
        if after.self_mute:
            await channel.send(embed=helpers.on_mute_log(member))
        else:
            await channel.send(embed=helpers.on_unmute_log(member))


@client.command(name="logs")
@commands.has_permissions(administrator=True)
async def logs(ctx):
    db.save_id(ctx.guild.id, ctx.channel.id, None, None)


@client.command(name="microphone_logs")
@commands.has_permissions(administrator=True)
async def microphone_logs(ctx):
    db.save_id(ctx.guild.id, None, ctx.channel.id, None)


@client.command(name="statistic")
@commands.has_permissions(administrator=True)
async def statistic(ctx):
    db.save_id(ctx.guild.id, None, None, ctx.channel.id)


@client.command(name="reset")
@commands.has_permissions(administrator=True)
async def reset(ctx):
    db.reset(ctx.guild.id)


def find_invite_by_code(invite_list, code):
    for inv in invite_list:
        if inv.code == code:
            return inv


if __name__ == "__main__":
    client.run(settings.DISCORD_API_TOKEN)
