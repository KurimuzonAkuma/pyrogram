<p align="center">
    <a href="https://github.com/KurimuzonAkuma/pyrogram">
        <img src="https://docs.kurigram.xyz/_static/pyrogram.png" alt="Pyrogram" width="128">
    </a>
    <br>
    <b>Telegram MTProto API Framework for Python</b>
    <br>
    <a href="https://kurigram.xyz">
        Homepage
    </a>
    •
    <a href="https://docs.kurigram.xyz">
        Documentation
    </a>
    •
    <a href="https://t.me/kurigram_news">
        News
    </a>
    •
    <a href="https://t.me/kurigram_chat">
        Chat
    </a>
</p>

## Pyrogram

> [!NOTE]
> Unfortunately, the original pyrogram is no longer supported. I will try to be your @delivrance.

> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots

``` python
from pyrogram import Client, filters

app = Client("my_account")


@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from Pyrogram!")


app.run()
```

**Pyrogram** is a modern, elegant and asynchronous [MTProto API](https://docs.kurigram.xyz/topics/mtproto-vs-botapi)
framework. It enables you to easily interact with the main Telegram API through a user account (custom client) or a bot
identity (bot API alternative) using Python.

### Support

If you'd like to support my fork, you can consider:

- `kurimuzonakuma.ton` - TON
- `TCbZ7CSpTvTJ6rno2eoWWYBx7hmYF75wk3` - USDT TRC20

### Key Features

- **Ready**: Install Pyrogram with pip and start building your applications right away.
- **Easy**: Makes the Telegram API simple and intuitive, while still allowing advanced usages.
- **Elegant**: Low-level details are abstracted and re-presented in a more convenient way.
- **Fast**: Boosted up by [TgCrypto](https://github.com/pyrogram/tgcrypto), a high-performance cryptography library written in C.
- **Type-hinted**: Types and methods are all type-hinted, enabling excellent editor support.
- **Async**: Fully asynchronous (also usable synchronously if wanted, for convenience).
- **Powerful**: Full access to Telegram's API to execute any official client action and more.

### Installing

``` bash
pip3 install kurigram --force-reinstall
```

### Resources

- Check out the [docs](https://docs.kurigram.xyz) to learn more about Pyrogram, get started right
away and discover more in-depth material for building your client applications.
- Join the [official channel](https//t.me/kurigram_news) and stay tuned for news, updates and announcements.
- Join the [official chat](https//t.me/kurigram_chat) to communicate with people.
