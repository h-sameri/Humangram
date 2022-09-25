from datetime import datetime
from telethon import TelegramClient, events, Button
from telethon.tl.types import PeerUser, PeerChannel
import config
import db

bot = TelegramClient('bot', config.api_key, config.api_hash).start(bot_token=config.bot_token)


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if type(event.message.peer_id) == PeerUser:
        join_time, score, max_members, oldest_message, phone_number, vouched_for = \
            datetime.now(), 0, 0, 0, None, 0
        conn = db.get_connection(config.db_url)
        cur = conn.cursor()
        cur.execute(
            'SELECT user_id, join_time, score, max_members, oldest_message, phone_number, vouched_for '
            'from users WHERE user_id = %s;',
            (event.message.peer_id.user_id,))
        bot_user = cur.fetchone()
        if bot_user is None:
            cur.execute(
                'INSERT INTO users (user_id) VALUES (%s);',
                (event.message.peer_id.user_id,))
        else:
            join_time, score, max_members, oldest_message, phone_number, vouched_for = \
                bot_user[1], bot_user[2], bot_user[3], bot_user[4], bot_user[5], bot_user[6]
        cur.close()
        db.close_connection(conn)
        keyboard = [
            [
                Button.inline('Share your phone number', b'number'),
                Button.inline('Forward an old message', b'forward')
            ],
            [
                Button.inline('Verify channel ownership', b'channel'),
                Button.inline("Get vouched for by others", b'voucher')
            ]
        ]
        msg = f'''Welcome {event.message.peer_id.user_id},
Use this bot to prove you are a human. Your current stats:

**Humanity proof score: {score}**
Phone number: {phone_number}
Oldest message: {oldest_message} days ago
Highest members in your channels: {max_members}
People vouched for your humanity: {vouched_for}
First seen here: {join_time}

Check your score anytime by sending /start here.

Increase your humanity proof score by completing tasks:'''
        await bot.send_message(event.chat_id, msg, buttons=keyboard)
    else:
        await event.respond('Please start the bot in a private chat.')
    raise events.StopPropagation


@bot.on(events.CallbackQuery(data=b'number'))
async def number(event):
    keyboard = [Button.request_phone('Share phone number')]
    msg = f'''Share your phone number to complete this task.
You'll earn {config.score_phone_number} points.'''
    await bot.send_message(event.chat_id, msg, buttons=keyboard)
    raise events.StopPropagation


@bot.on(events.NewMessage(incoming=True, forwards=False, func=lambda e: e.message.media and e.message.reply_to))
async def check_phone_number(event):
    if type(event.message.peer_id) == PeerUser:
        if event.message.media.phone_number is not None and event.message.media.user_id is not None:
            if event.message.peer_id.user_id == event.message.media.user_id:
                conn = db.get_connection(config.db_url)
                cur = conn.cursor()
                cur.execute(
                    'SELECT phone_number '
                    'from users WHERE phone_number = %s;',
                    (event.message.media.phone_number,))
                phone_number = cur.fetchone()
                if phone_number is None:
                    cur.execute(
                        'SELECT phone_number '
                        'from users WHERE user_id = %s;',
                        (event.message.peer_id.user_id,))
                    phone_number = cur.fetchone()
                    if phone_number is not None:
                        if phone_number[0] is None:
                            cur.execute(
                                'UPDATE users SET phone_number = %s, score = score + %s WHERE user_id = %s;',
                                (event.message.media.phone_number,
                                 config.score_phone_number,
                                 event.message.peer_id.user_id))
                            await event.respond(f'You earned {config.score_phone_number} point(s).',
                                                buttons=Button.clear())
                        else:
                            await event.respond('You have already shared a phone number.',
                                                buttons=Button.clear())
                else:
                    await event.respond('This phone number has been shared before.',
                                        buttons=Button.clear())
                cur.close()
                db.close_connection(conn)
                raise events.StopPropagation


@bot.on(events.CallbackQuery(data=b'forward'))
async def forward(event):
    msg = f'''Forward an old message of yours to prove you had this account for a long time.
You'll earn a point for each {config.score_point_per_x_days} days.
For example, if the message was originally sent {config.score_point_per_x_days*2} days ago, you'll earn 2 points.'''
    await event.respond(msg)
    raise events.StopPropagation


@bot.on(events.NewMessage(incoming=True, forwards=True))
async def check_forward(event):
    if type(event.message.peer_id) == PeerUser:
        if event.message.peer_id.user_id == event.message.fwd_from.from_id.user_id:
            conn = db.get_connection(config.db_url)
            cur = conn.cursor()
            cur.execute(
                'SELECT oldest_message '
                'from users WHERE user_id = %s;',
                (event.message.peer_id.user_id,))
            oldest_message = cur.fetchone()
            if oldest_message is not None:
                new_delta = (datetime.now() - event.message.fwd_from.date.replace(tzinfo=None)
                             ).days - int(oldest_message[0])
                if new_delta > 0:
                    cur.execute(
                        'UPDATE users SET oldest_message = %s, score = score + %s WHERE user_id = %s;',
                        ((datetime.now() - event.message.fwd_from.date.replace(tzinfo=None)).days,
                        int(new_delta / config.score_point_per_x_days),
                        event.message.peer_id.user_id))
                    msg = f'''You earned {int(new_delta / config.score_point_per_x_days)} point(s).
Send /start to view more details of your scoring.'''
                    await event.respond(msg)
                else:
                    await event.respond('You had already forwarded an older message than this one.')
            cur.close()
            db.close_connection(conn)
        else:
            msg = '''Forwarded message ignored because your account was not in the forward header.
Please make sure the following conditions are met:

* The original message was sent on your behalf (not as a channel)
* Don't select "Remove sender name" option when forwarding
* If your forward message privacy setting is not set to "Everybody",
  add this bot as an exception or change the setting temporarily'''
            await event.respond(msg)
    raise events.StopPropagation


@bot.on(events.CallbackQuery(data=b'channel'))
async def channel(event):
    try:
        msg = f'''1- Add this bot to a channel you own (no permission required)

2- Post this verification code to the channel --> `humangram:{event.original_update.user_id}`

3- You'll receive a verification success message from the bot shortly

4- You can delete the post and remove the bot'''
        await event.respond(msg)
    except:
        # button is not clicked by a user inside the bot
        pass
    raise events.StopPropagation


@bot.on(events.NewMessage(incoming=True, forwards=False, pattern='humangram:*'))
async def check_channel(event):
    if type(event.message.peer_id) == PeerChannel:
        verification_code = event.message.message.split(':')[-1]
        conn = db.get_connection(config.db_url)
        cur = conn.cursor()
        cur.execute(
            'SELECT channel_id, user_id from channels WHERE channel_id = %s;',
            (event.message.peer_id.channel_id,))
        channel_user = cur.fetchone()
        if channel_user is None:
            cur.execute(
                'SELECT max_members from users WHERE user_id = %s;',
                (verification_code,))
            max_members = cur.fetchone()
            if max_members is not None:
                members = await bot.get_participants(event.message.peer_id)
                cur.execute(
                    'INSERT INTO channels (channel_id, user_id, members) VALUES (%s, %s, %s);',
                    (event.message.peer_id.channel_id, verification_code, members.total))
                new_delta = int((members.total - max_members[0])/config.score_point_per_x_members)
                if new_delta > 0:
                    cur.execute(
                        'UPDATE users SET max_members = %s, score = score + %s WHERE user_id = %s;',
                        (members.total, new_delta, verification_code))
                msg = f'''You earned {max(new_delta, 0)} point(s).
Send /start to view more details of your scoring.'''
                await bot.send_message(int(verification_code), msg)
            else:
                await event.respond('Verification code is incorrect.')
        else:
            # TODO alternatively, we can update members and give delta points to the corresponding user_id
            await event.respond('This channel has already been used for earning points in the past.')
        cur.close()
        db.close_connection(conn)
    else:
        await event.respond('This code only works in a channel!')


@bot.on(events.CallbackQuery(data=b'voucher'))
async def voucher(event):
    try:
        msg = f'''Get vouched for humanity by asking others to send this code directly to the bot:

`vouch:{event.original_update.user_id}`

You'll be notified when someone vouches for you.'''
        await event.respond(msg)
    except:
        # button is not clicked by a user inside the bot
        pass
    raise events.StopPropagation


@bot.on(events.NewMessage(incoming=True, forwards=False, pattern='vouch:*'))
async def vouch(event):
    if type(event.message.peer_id) == PeerUser:
        vouch_code = event.message.message.split(':')[-1]
        if str(event.message.peer_id.user_id) != vouch_code:
            conn = db.get_connection(config.db_url)
            cur = conn.cursor()
            cur.execute(
                'SELECT user_id from users WHERE user_id = %s;',
                (vouch_code,))
            vouched_user = cur.fetchone()
            if vouched_user is not None:
                cur.execute(
                    'SELECT score from users WHERE user_id = %s;',
                    (event.message.peer_id.user_id,))
                user_score = cur.fetchone()
                if user_score is not None:
                    if int(user_score[0]) >= config.score_voucher:
                        cur.execute(
                            'INSERT INTO vouching (voucher, vouched_for) VALUES (%s, %s) ON CONFLICT DO NOTHING;',
                            (event.message.peer_id.user_id, vouch_code))
                        msg = f'''You're about to vouch for humanity of user #{vouch_code}.

**Warning: You'll lose {config.score_voucher} humanity score!**

Send the following code here to confirm:

`confirm:{vouch_code}`

Your current humanity score is {user_score[0]}.
Your humanity score after confirmation will be {int(user_score[0]) - config.score_voucher}.'''
                        await event.respond(msg)
                    else:
                        await event.respond('You don\'nt have enough humanity score to vouch for others.')
            else:
                await event.respond('Voucher code is invalid.')
            cur.close()
            db.close_connection(conn)
        else:
            await event.respond('You cannot vouch for yourself!')
    raise events.StopPropagation


@bot.on(events.NewMessage(incoming=True, forwards=False, pattern='confirm:*'))
async def confirm(event):
    if type(event.message.peer_id) == PeerUser:
        confirm_code = event.message.message.split(':')[-1]
        conn = db.get_connection(config.db_url)
        cur = conn.cursor()
        cur.execute(
            'SELECT status, vouching_time FROM vouching WHERE voucher = %s AND vouched_for = %s;',
            (event.message.peer_id.user_id, confirm_code))
        status_time = cur.fetchone()
        if status_time is not None:
            if status_time[0] == 'V':
                cur.execute(
                    'SELECT score from users WHERE user_id = %s;',
                    (event.message.peer_id.user_id,))
                user_score = cur.fetchone()
                if user_score is not None:
                    if user_score[0] >= config.score_voucher:
                        cur.execute(
                            'UPDATE vouching SET status = %s WHERE voucher = %s AND vouched_for = %s;',
                            ('C', event.message.peer_id.user_id, confirm_code))
                        cur.execute(
                            'UPDATE users SET vouched_for = vouched_for + 1, score = score + %s WHERE user_id = %s;',
                            (config.score_voucher, confirm_code))
                        cur.execute(
                            'UPDATE users SET score = score - %s WHERE user_id = %s;',
                            (config.score_voucher, event.message.peer_id.user_id))
                        msg = f'''You vouched for user #{confirm_code} successfully.

Your humanity score is {int(user_score[0]) - config.score_voucher} now.'''
                        await event.respond(msg)
                        msg = f'''Congratulations! User #{event.message.peer_id.user_id} vouched for you.

You earned +{config.score_voucher} humanity score as a result.

Send /start to view more details of your scoring.'''
                        await bot.send_message(int(confirm_code), msg)
                    else:
                        await event.respond('You don\'nt have enough humanity score to vouch for others.')
            elif status_time == 'C':
                await event.respond('You have already vouched for this user.')
        else:
            await event.respond('You should first initiate a vouching process before confirming it!')
        cur.close()
        db.close_connection(conn)
    raise events.StopPropagation


def main():
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
