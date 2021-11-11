import os
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from donlee_robot.donlee_robot import DonLee_Robot
from database import add_connection, all_connections, if_active, delete_connection


@DonLee_Robot.on_message((filters.private | filters.group) & filters.command("connect"))
async def addconnection(client,message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == "private":
        try:
            cmd, group_id = message.text.split(" ", 1)
        except:
            await message.reply_text(
                "<b>Eɴᴛᴇʀ ɪɴ ᴄᴏʀʀᴇᴄᴛ ғᴏʀᴍᴀᴛ!</b>\n\n"
                "<code>/connect ɢʀᴏᴜᴘɪᴅ</code>\n\n"
                "<i>Gᴇᴛ ʏᴏᴜʀ Gʀᴏᴜᴘ ɪᴅ ʙʏ ᴀᴅᴅɪɴɢ ᴛʜɪs ʙᴏᴛ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴜsᴇ  <code>/id</code></i>",
                quote=True
            )
            return

    elif (chat_type == "group") or (chat_type == "supergroup"):
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if (st.status == "administrator") or (st.status == "creator") or (str(userid) in Config.AUTH_USERS):
            pass
        else:
            await message.reply_text("Yᴏᴜ sʜᴏᴜʟᴅ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ɪɴ Gɪᴠᴇɴ ɢʀᴏᴜᴘ!", quote=True)
            return
    except Exception as e:
        print(e)
        await message.reply_text(
            "Invalid Group ID!\n\nIf correct, Make sure I'm present in your group!!",
            quote=True
        )
        return

    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == "administrator":
            ttl = await client.get_chat(group_id)
            title = ttl.title

            addcon = await add_connection(str(group_id), str(userid))
            if addcon:
                await message.reply_text(
                    f"Sᴜᴄᴇssғᴜʟʟʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ **{title}**\nNᴏᴡ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ғʀᴏᴍ ᴍʏ ᴘᴍ !",
                    quote=True,
                    parse_mode="md"
                )
                if (chat_type == "group") or (chat_type == "supergroup"):
                    await client.send_message(
                        userid,
                        f"Connected to **{title}** !",
                        parse_mode="md"
                    )
            else:
                await message.reply_text(
                    "Yᴏᴜ'ʀᴇ ᴀʟʀᴇᴀᴅʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ!",
                    quote=True
                )
        else:
            await message.reply_text("Aᴅᴅ ᴍᴇ ᴀs ᴀɴ ᴀᴅᴍɪɴ ɪɴ ɢʀᴏᴜᴘ", quote=True)
    except Exception as e:
        print(e)
        await message.reply_text(
            "Some error occured! Try again later.",
            quote=True
        )
        return


@DonLee_Robot.on_message((filters.private | filters.group) & filters.command("disconnect"))
async def deleteconnection(client,message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == "private":
        await message.reply_text("Run /connections to view or disconnect from groups!", quote=True)

    elif (chat_type == "group") or (chat_type == "supergroup"):
        group_id = message.chat.id

        st = await client.get_chat_member(group_id, userid)
        if not ((st.status == "administrator") or (st.status == "creator") or (str(userid) in Config.AUTH_USERS)):
            return

        delcon = await delete_connection(str(userid), str(group_id))
        if delcon:
            await message.reply_text("Successfully disconnected from this chat", quote=True)
        else:
            await message.reply_text("This chat isn't connected to me!\nDo /connect to connect.", quote=True)


@DonLee_Robot.on_message(filters.private & filters.command(["connections"]))
async def connections(client,message):
    userid = message.from_user.id

    groupids = await all_connections(str(userid))
    if groupids is None:
        await message.reply_text(
            "There are no active connections!! Connect to some groups first.",
            quote=True
        )
        return
    buttons = []
    for groupid in groupids:
        try:
            ttl = await client.get_chat(int(groupid))
            title = ttl.title
            active = await if_active(str(userid), str(groupid))
            if active:
                act = " - ACTIVE"
            else:
                act = ""
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{title}:{act}"
                    )
                ]
            )
        except:
            pass
    if buttons:
        await message.reply_text(
            "Your connected group details ;\n\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
